cmake_minimum_required(VERSION 3.18)
project(ocpn_min LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_definitions(-DOCPN_MIN_NO_GUI)

# Pull vendor file list
file(STRINGS ${CMAKE_SOURCE_DIR}/../vendor/vendor_filelist.cmake OCPN_SRCS)
list(TRANSFORM OCPN_SRCS PREPEND "${CMAKE_SOURCE_DIR}/../vendor/opencpn_subset/")

add_library(ocpn_core STATIC ${OCPN_SRCS})
target_include_directories(ocpn_core PRIVATE
  ${CMAKE_SOURCE_DIR}/../vendor/opencpn_subset
  ${CMAKE_SOURCE_DIR}/../vendor/opencpn_subset/shim
  ${CMAKE_SOURCE_DIR}/../vendor/opencpn_subset/libs/iso8211/include
)

add_executable(ocpn_min ${CMAKE_SOURCE_DIR}/src/main.cpp)
target_link_libraries(ocpn_min PRIVATE ocpn_core)

# Quick smoke: fail build if forbidden includes remain
add_custom_target(check_includes
  COMMAND ${CMAKE_COMMAND} -E echo "Scanning for forbidden includes..."
  COMMAND bash -c "grep -R --line-number -E '(<wx/|OpenGL|s52plib|Quilt|glChartCanvas|Osenc)' ../vendor/opencpn_subset && exit 1 || exit 0"
)
add_dependencies(ocpn_min check_includes)
