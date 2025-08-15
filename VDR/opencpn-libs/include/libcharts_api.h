#pragma once
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

void charts_load_cell(const char *path);
unsigned char *charts_render_tile_png(double minx, double miny, double maxx,
                                      double maxy, int z, const char *palette,
                                      size_t *out_size);
unsigned char *charts_render_tile_mvt(double minx, double miny, double maxx,
                                      double maxy, int z, size_t *out_size);
void charts_free_buffer(unsigned char *buffer);

#ifdef __cplusplus
}
#endif
