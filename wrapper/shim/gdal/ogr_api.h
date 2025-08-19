#pragma once

enum OGRFieldType { OGR_INT, OGR_REAL, OGR_STR };

class OGRGeometry {
public:
    virtual ~OGRGeometry() = default;
};

class OGRPoint : public OGRGeometry {
public:
    OGRPoint(double, double, double = 0.0) {}
};

class OGRMultiPoint : public OGRGeometry {
public:
    void addGeometry(OGRPoint*) {}
    OGRGeometry* getGeometryRef(int) { return nullptr; }
};
