#pragma once
#include "types.hpp"
#include <ostream>

void write_dataset(std::ostream& os, const DatasetInfo& ds);
void write_feature(std::ostream& os, const DatasetInfo& ds, const Feature& f);
