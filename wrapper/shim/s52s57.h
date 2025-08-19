#ifndef OCPN_MIN_S52S57_H
#define OCPN_MIN_S52S57_H

#include <vector>

struct LUPrec;
struct S57Obj;
struct sm_parms;
struct mps_container;

struct ObjRazRules {
    LUPrec* LUP = nullptr;
    S57Obj* obj = nullptr;
    sm_parms* sm_transform_parms = nullptr;
    ObjRazRules* child = nullptr;
    ObjRazRules* next = nullptr;
    mps_container* mps = nullptr;
};

using ListOfObjRazRules = std::vector<ObjRazRules*>;

#endif // OCPN_MIN_S52S57_H
