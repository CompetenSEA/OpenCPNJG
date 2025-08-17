cmake_minimum_required(VERSION 3.10)
project(cm93_convert LANGUAGES NONE)

# The original utility was a small C++ program.  It has been replaced by a
# pure Python script so there is nothing to build here.  We simply install the
# script as an executable for convenience.

install(PROGRAMS main.py DESTINATION tools/bin RENAME cm93_convert)
