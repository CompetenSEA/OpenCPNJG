#pragma once
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>

#define CPL_LSB 1
#define CPL_MSB 0
#define CPL_DLL
#define TRUE 1
#define FALSE 0
#define CE_Failure 3
#define CPLE_FileIO 0
#define CPLAssert(x) do { if(!(x)) std::abort(); } while(0)
inline int CPLError(int, int, const char*) { return 0; }
#define VSIFRead fread
#define VSIFOpen fopen
#define VSIFTell ftell
#define VSIFClose fclose

typedef unsigned char GByte;
typedef std::uint16_t GUInt16;
typedef std::int16_t GInt16;
typedef std::uint32_t GUInt32;
typedef std::int32_t GInt32;
