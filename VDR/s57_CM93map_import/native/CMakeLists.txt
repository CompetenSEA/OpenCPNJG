cmake_minimum_required(VERSION 3.18)
project(ocpn_min LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_definitions(-DOCPN_MIN_NO_GUI)

# Pull vendor file list
file(STRINGS ${CMAKE_SOURCE_DIR}/../vendor/vendor_filelist.cmake OCPN_SRCS)
list(TRANSFORM OCPN_SRCS PREPEND "${CMAKE_SOURCE_DIR}/../vendor/opencpn_subset/")

file(GLOB GDAL_CPL_SRCS
  ${CMAKE_SOURCE_DIR}/../vendor/gdal_cpl/*.c
  ${CMAKE_SOURCE_DIR}/../vendor/gdal_cpl/*.cpp)
add_library(gdal_cpl STATIC ${GDAL_CPL_SRCS})
target_include_directories(gdal_cpl PUBLIC
  ${CMAKE_SOURCE_DIR}/../vendor/gdal_cpl)

add_library(ocpn_s57 STATIC ${OCPN_SRCS} src/s57_iter.cpp src/ndjson.cpp src/types.hpp)
target_link_libraries(ocpn_s57 PUBLIC gdal_cpl)
target_include_directories(ocpn_s57 PUBLIC
  ${CMAKE_SOURCE_DIR}/../vendor/opencpn_subset
  ${CMAKE_SOURCE_DIR}/../vendor/opencpn_subset/src/libs/iso8211/include
  ${CMAKE_SOURCE_DIR}/src)

add_library(ocpn_cm93 STATIC src/cm93_iter.cpp src/ndjson.cpp src/types.hpp)
target_link_libraries(ocpn_cm93 PUBLIC gdal_cpl)
target_include_directories(ocpn_cm93 PUBLIC ${CMAKE_SOURCE_DIR}/src)

find_package(ZLIB REQUIRED)

add_executable(ocpn_min src/main.cpp)
target_link_libraries(ocpn_min PRIVATE ocpn_s57 ocpn_cm93 gdal_cpl ZLIB::ZLIB)

# Quick smoke: fail build if forbidden includes remain
add_custom_target(check_includes
  COMMAND ${CMAKE_COMMAND} -E echo "Scanning for forbidden includes..."
  COMMAND bash -c "! egrep -R --line-number -e '\\<wx/' -e 'OpenGL' -e 's52plib' -e 'Quilt' -e 'glChartCanvas' -e 'Osenc' ${CMAKE_SOURCE_DIR}/../vendor/opencpn_subset/src/libs/iso8211"
)
add_dependencies(ocpn_min check_includes)
