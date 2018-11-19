# This is a modified env file that I created when I was originally planning
# on incoporating the env file into the ABR framework of using Pensieve within
# Puffer. I ultimately moved away from this design so this file is now superflous,
# but I am keeping it around for reference.

import os
import numpy as np


RANDOM_SEED = 42
MAX_NUM_BITRATES = 10
VIDEO_CHUNCK_LEN = 2000.0  # millisec
DRAIN_BUFFER_SLEEP_TIME = 500.0  # millisec
MILLISECONDS_IN_SECOND = 1000.0
BUFFER_THRESH = 60.0 * MILLISECONDS_IN_SECOND
B_IN_MB = 1000000.0
BITS_IN_BYTE = 8.0
PACKET_PAYLOAD_PORTION = 0.95
LINK_RTT = 80  # millisec
PACKET_SIZE = 1500  # bytes
NOISE_LOW = 0.9
NOISE_HIGH = 1.1
VIDEO_FOLDER = './videos/'
COOKED_TRACE_FOLDER = './cooked_traces/'

class Environment:
	def __init__(self, random_seed=RANDOM_SEED,
			   trace_folder=COOKED_TRACE_FOLDER,
			   video_folder=VIDEO_FOLDER):
		
		self.random_seed = random_seed
		np.random.seed(self.random_seed)
		self.trace_folder = trace_folder
		self.video_folder = video_folder

		# -- network traces --
		cooked_files = os.listdir(self.trace_folder)
		self.all_cooked_time = []
		self.all_cooked_bw = []
		self.all_file_names = []
		for cooked_file in cooked_files:
			file_path = self.trace_folder + cooked_file
			cooked_time = []
			cooked_bw = []
			# print file_path
			with open(file_path, 'rb') as f:
				for line in f:
					parse = line.split()
					cooked_time.append(float(parse[0]))
					cooked_bw.append(float(parse[1]))
			self.all_cooked_time.append(cooked_time)
			self.all_cooked_bw.append(cooked_bw)
			self.all_file_names.append(cooked_file)

                #if self.fixed_env:
                self.trace_idx = 0

		self.cooked_time = self.all_cooked_time[self.trace_idx]
		self.cooked_bw = self.all_cooked_bw[self.trace_idx]

		#if self.fixed_env:
		self.mahimahi_ptr = 1

		self.last_mahimahi_time = self.cooked_time[self.mahimahi_ptr - 1]

		# -- video configurations --
                # Hudson: Previously this stored for multiple videos,
                # for us it stores only for one video bc we only use it for testing

                self.video_num_bitrates = 8; # TODO: Make me a variable
                self.video_sizes = [] # Populate me via IPC over time (chunk sizes)
                                      # Fmt: double nested array [chunk#][quality]
                self.video_mask = [1,1,1,1,1,1,0,1,0] # TODO: Make me a variable
                # TODO: I probably should be training with a set of bitrates closer
                # to our actual bitrates

		self.chunk_idx = 0
		self.buffer_size = 0

	def get_video_chunk(self, quality, throughput, duration):

		assert quality >= 0
		assert quality < self.video_num_bitrates

		video_chunk_size = self.video_sizes[self.chunk_idx][quality] * B_IN_MB  # in bytes
		
		# use the delivery opportunity in mahimahi
		delay = 0.0  # in ms
		video_chunk_counter_sent = 0  # in bytes
		
		while True:  # download video chunk over mahimahi
                        # Replaced by inputs to this function
                        '''
			throughput = self.cooked_bw[self.mahimahi_ptr] \
						 * B_IN_MB / BITS_IN_BYTE
			duration = self.cooked_time[self.mahimahi_ptr] \
					   - self.last_mahimahi_time
                        '''
		
                        # H: This represents the number of bytes of the packet paylaod that
                        # has been sent
			packet_payload = throughput * duration * PACKET_PAYLOAD_PORTION

                        # H: Check if there has been enough troughput to send a whole
                        # video chunk (2 seconds of video in our case)
			if video_chunk_counter_sent + packet_payload > video_chunk_size:

				fractional_time = (video_chunk_size - video_chunk_counter_sent) / \
								  throughput / PACKET_PAYLOAD_PORTION
				delay += fractional_time
				self.last_mahimahi_time += fractional_time
				assert(self.last_mahimahi_time <= self.cooked_time[self.mahimahi_ptr])
				break

			video_chunk_counter_sent += packet_payload
			delay += duration
			self.last_mahimahi_time = self.cooked_time[self.mahimahi_ptr]
			self.mahimahi_ptr += 1

			if self.mahimahi_ptr >= len(self.cooked_bw):
				# loop back in the beginning
				# note: trace file starts with time 0
				self.mahimahi_ptr = 1
				self.last_mahimahi_time = 0

		delay *= MILLISECONDS_IN_SECOND
		delay += LINK_RTT

		# rebuffer time
		rebuf = np.maximum(delay - self.buffer_size, 0.0)

		# update the buffer
		self.buffer_size = np.maximum(self.buffer_size - delay, 0.0)

		# add in the new chunk
		self.buffer_size += VIDEO_CHUNCK_LEN

		# sleep if buffer gets too large
		sleep_time = 0
		if self.buffer_size > BUFFER_THRESH:
			# exceed the buffer limit
			# we need to skip some network bandwidth here
			# but do not add up the delay
			drain_buffer_time = self.buffer_size - BUFFER_THRESH
			sleep_time = np.ceil(drain_buffer_time / DRAIN_BUFFER_SLEEP_TIME) * \
						 DRAIN_BUFFER_SLEEP_TIME
			self.buffer_size -= sleep_time

			while True:
				duration = self.cooked_time[self.mahimahi_ptr] \
						   - self.last_mahimahi_time
				if duration > sleep_time / MILLISECONDS_IN_SECOND:
					self.last_mahimahi_time += sleep_time / MILLISECONDS_IN_SECOND
					break
				sleep_time -= duration * MILLISECONDS_IN_SECOND
				self.last_mahimahi_time = self.cooked_time[self.mahimahi_ptr]
				self.mahimahi_ptr += 1

				if self.mahimahi_ptr >= len(self.cooked_bw):
					# loop back in the beginning
					# note: trace file starts with time 0
					self.mahimahi_ptr = 1
					self.last_mahimahi_time = 0

		# the "last buffer size" return to the controller
		# Note: in old version of dash the lowest buffer is 0.
		# In the new version the buffer always have at least
		# one chunk of video
		return_buffer_size = self.buffer_size

		self.chunk_idx += 1

		next_video_chunk_sizes = self.video_sizes[self.chunk_idx]
		bitrate_mask = self.video_mask

		return delay, \
			sleep_time, \
			return_buffer_size / MILLISECONDS_IN_SECOND, \
			rebuf / MILLISECONDS_IN_SECOND, \
			video_chunk_size, \
			next_video_chunk_sizes, \
			bitrate_mask


def main():
	net_env = Environment()
	
	done = False
	while not done:
		delay, sleep_time, buf, rebuf, chunk_size, done, \
		num_chunk_remain, num_chunks, \
		next_chunk_size, bitrate_mask = net_env.get_video_chunk(0)
		print "delay", delay
		print "sleep", sleep_time
		print "buffer", buf
		print "rebuffering", rebuf
		print "chunk_size", chunk_size
		print "num_chunk_remain", num_chunk_remain
		print "num_chunks", num_chunks
		print "next_chunk", next_chunk_size
		print "mask", bitrate_mask
		print "\n"

		raw_input()


if __name__ == '__main__':
	main()
