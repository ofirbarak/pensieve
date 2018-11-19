#include <iostream>
#include <stdio.h>
#include <chrono>
#include <thread>
#include <cstdint>
#include "ipc_socket.hh"
#include <nlohmann/json.hpp>
#include <endian.h>

using json = nlohmann::json;
using namespace std;

string put_field(const uint16_t n)
{
  const uint16_t network_order = htobe16(n);
  return string(reinterpret_cast<const char *>(&network_order),
                sizeof(network_order));
}

auto start = std::chrono::system_clock::now();

int main () {
    // Open IPC Channel to pensieve ABR decision-maker
    remove("/tmp/pensieve");
    IPCSocket sock;
    sock.bind("/tmp/pensieve");
    sock.listen();
    auto connection = sock.accept();
    while(1) {

        // Get info from Pensieve
        auto read_data = connection.read();
        if (read_data.empty()) {
            cout << "Empty read, exiting" << endl;
            break;
        }
        cout << read_data << endl;

        std::this_thread::sleep_for(std::chrono::seconds(2)); //simulate real media server doing other stuff

        //RESPOND
        json j;
        j["delay"] = 3.99182; // ms
        j["playback_buf"] = 7230; // ms
        j["rebuf_time"] = 150; // ms
        j["last_chunk_size"] = 0.1850032; // MB
        j["next_chunk_sizes"] = {0.181801, 0.450283, 0.668286, 1.034108, 1.728879, 2.354772, 2.83424, 3.1289123}; //MB
        uint16_t json_len = j.dump().length();

        connection.write(put_field(json_len) + j.dump());
        //connection.write(to_string(j.dump().length()));
//        connection.write("bit rate = 5, pbuf = 6");
    }
}
