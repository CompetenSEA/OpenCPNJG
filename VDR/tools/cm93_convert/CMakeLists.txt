cmake_minimum_required(VERSION 3.10)
project(cm93_convert)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(SQLite3 REQUIRED)

add_executable(cm93_convert main.cpp)
target_link_libraries(cm93_convert PRIVATE SQLite::SQLite3)

if(UNIX)
  target_link_options(cm93_convert PRIVATE -static)
endif()

install(TARGETS cm93_convert RUNTIME DESTINATION tools/bin)
