#include <iostream>
#include <vector>
#include <string>
#include "emit_ndjson.hpp"
#include "attr_codec.hpp"
#include "bbox.hpp"

int main(int argc, char** argv){
    std::cout << "{\"type\":\"Dataset\"}\n";
    // placeholder feature emission
    std::cout << "{\"type\":\"Feature\"}\n";
    return 0;
}
