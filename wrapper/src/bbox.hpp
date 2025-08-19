#pragma once

struct BBox {
    double minx{0}, miny{0}, maxx{0}, maxy{0};
    bool intersects(const BBox& other) const {
        return !(other.minx > maxx || other.maxx < minx ||
                 other.miny > maxy || other.maxy < miny);
    }
};
