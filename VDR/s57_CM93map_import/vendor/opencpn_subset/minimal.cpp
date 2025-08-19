#include "wx_shim.hpp"
#include "compat.hpp"
#include <iostream>

int main(int argc, char** argv) {
    if (argc > 1 && std::string(argv[1]) == "--help") {
        std::cout << "ocpn_min -- minimal OpenCPN subset\n";
        std::cout << "Usage: ocpn_min [--help]\n";
        return 0;
    }
    std::cout << "ocpn_min running" << std::endl;
    return 0;
}
