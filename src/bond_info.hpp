
#pragma once

#include "sz.hpp"
#include <algorithm>
#include <unordered_map>

using namespace std;

void bond_info_trans_to_sz(
    const vector<unordered_map<uint32_t, uint32_t>> &infos,
    const string &pattern, vector<vector<pair<SZLong, uint32_t>>> &infox,
    bool sorted = false);

unordered_map<uint32_t,
              pair<uint32_t, unordered_map<vector<uint32_t>,
                                           pair<uint32_t, vector<uint32_t>>>>>
bond_info_fusing_product(const vector<unordered_map<uint32_t, uint32_t>> &infos,
                         const string &pattern);