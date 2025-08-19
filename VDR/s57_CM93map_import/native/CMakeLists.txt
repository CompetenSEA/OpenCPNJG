cmake_minimum_required(VERSION 3.10)
project(ocpn_min)

add_executable(ocpn_min ../vendor/opencpn_subset/minimal.cpp)
target_include_directories(ocpn_min PRIVATE ../vendor/opencpn_subset)
