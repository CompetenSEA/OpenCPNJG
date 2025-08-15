cmake_minimum_required(VERSION 3.10)
project(opencpn_charts LANGUAGES CXX)

add_library(charts SHARED
    src/charts.cpp
    src/libcharts_api.cpp
    src/cm93/dummy.cpp
    src/s57chart/dummy.cpp
    src/ps52plib/dummy.cpp
)

target_include_directories(charts PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

set_target_properties(charts PROPERTIES
    OUTPUT_NAME "charts"
    VERSION 0.1.0
    SOVERSION 0
)

install(TARGETS charts DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)
