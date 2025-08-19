#pragma once
#include "wx.h"

#define wxLC_REPORT 0
#define wxLC_SINGLE_SEL 0
#define wxLC_HRULES 0
#define wxLC_VRULES 0
#define wxLC_VIRTUAL 0
#define wxBORDER_SUNKEN 0
#define wxLIST_FORMAT_LEFT 0
#define wxLIST_FORMAT_CENTER 0
#define wxLIST_STATE_SELECTED 0
#define wxEVT_COMMAND_LIST_ITEM_SELECTED 0
#define wxListEventHandler(x) x

class wxListEvent {};

class wxListCtrl {
public:
    wxListCtrl(...) {}
    void Connect(...) {}
    void InsertColumn(...) {}
    void InsertItem(...) {}
    void SetItem(...) {}
    void SetItemCount(...) {}
    void SetItemState(...) {}
    void DeleteAllItems() {}
    void Refresh(...) {}
    long GetItemCount() const { return 0; }
    bool IsVirtual() const { return false; }
};
