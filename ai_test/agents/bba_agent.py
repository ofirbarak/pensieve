from typing import List


class ABRAgent:
    def __init__(
        self,
        video_sizes: List[List[float]],
        buffer_size_in_ms: float,
        chunk_len_in_ms: float = 2000,
        bitrates_in_kbps: List[float] = [
            200,
            300,
            450,
            750,
            1200,
            1850,
            2850,
            4300,
            6000,
            8000,
        ],
    ) -> None:
        self.video_sizes: List[List[float]] = video_sizes
        self.buffer_size_in_ms: float = buffer_size_in_ms
        self.chunk_len_in_ms: float = chunk_len_in_ms
        self.bitrates_in_kbps: List[float] = bitrates_in_kbps
        self.reservoir = 5
        self.cushion = 10

    def get_bitrate_index(
        self,
        curr_buffer_size_in_ms: float,
        last_chunk_sending_time: float,
        next_chunk_sizes_in_bytes: List[float],
        rebuf_in_ms: float,
    ) -> int:
        tmpBitrate = 0
        tmpQuality = 0
        bLevel = curr_buffer_size_in_ms / 1000

        if bLevel <= self.reservoir:
            tmpBitrate = self.bitrates_in_kbps[0]
        elif bLevel > self.reservoir + self.cushion:
            tmpBitrate = self.bitrates_in_kbps[-1]
        else:
            tmpBitrate = (
                self.bitrates_in_kbps[0]
                + (self.bitrates_in_kbps[-1] - self.bitrates_in_kbps[0])
                * (bLevel - self.reservoir)
                / self.cushion
            )

        for i in reversed(range(len(self.bitrates_in_kbps))):
            if tmpBitrate >= self.bitrates_in_kbps[i]:
                tmpQuality = i
                break

            tmpQuality = i

        return tmpQuality

    def get_quality_from_bitrate(self, bitrate_kbps):
        # Map bitrate in Kbps to a quality index based on predefined bitrates
        return self.bitrates_in_kbps.index(bitrate_kbps)

    def update(self, reward) -> None:
        pass
