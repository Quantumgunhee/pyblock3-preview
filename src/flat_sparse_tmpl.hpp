
/*
 * pyblock3: An Efficient python MPS/DMRG Library
 * Copyright (C) 2020 The pyblock3 developers. All Rights Reserved.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 *
 */

// explicit template instantiation

#ifndef TMPL_EXTERN
#define TMPL_EXTERN
#endif

#ifdef TMPL_Q

#ifdef TMPL_FL

TMPL_EXTERN template void flat_sparse_tensor_transpose<TMPL_Q, TMPL_FL>(
    const py::array_t<uint32_t> &ashs, const py::array_t<TMPL_FL> &adata,
    const py::array_t<uint32_t> &aidxs, const py::array_t<int32_t> &perm,
    py::array_t<TMPL_FL> &cdata);

TMPL_EXTERN template tuple<py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<TMPL_FL>, py::array_t<uint32_t>>
flat_sparse_tensor_tensordot<TMPL_Q, TMPL_FL>(
    const py::array_t<uint32_t> &aqs, const py::array_t<uint32_t> &ashs,
    const py::array_t<TMPL_FL> &adata, const py::array_t<uint32_t> &aidxs,
    const py::array_t<uint32_t> &bqs, const py::array_t<uint32_t> &bshs,
    const py::array_t<TMPL_FL> &bdata, const py::array_t<uint32_t> &bidxs,
    const py::array_t<int> &idxa, const py::array_t<int> &idxb);

TMPL_EXTERN template tuple<py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<TMPL_FL>, py::array_t<uint32_t>>
flat_sparse_tensor_add<TMPL_Q, TMPL_FL>(
    const py::array_t<uint32_t> &aqs, const py::array_t<uint32_t> &ashs,
    const py::array_t<TMPL_FL> &adata, const py::array_t<uint32_t> &aidxs,
    const py::array_t<uint32_t> &bqs, const py::array_t<uint32_t> &bshs,
    const py::array_t<TMPL_FL> &bdata, const py::array_t<uint32_t> &bidxs);

TMPL_EXTERN template tuple<py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<TMPL_FL>, py::array_t<uint32_t>>
flat_sparse_tensor_kron_add<TMPL_Q, TMPL_FL>(
    const py::array_t<uint32_t> &aqs, const py::array_t<uint32_t> &ashs,
    const py::array_t<TMPL_FL> &adata, const py::array_t<uint32_t> &aidxs,
    const py::array_t<uint32_t> &bqs, const py::array_t<uint32_t> &bshs,
    const py::array_t<TMPL_FL> &bdata, const py::array_t<uint32_t> &bidxs,
    const unordered_map<uint32_t, uint32_t> &infol,
    const unordered_map<uint32_t, uint32_t> &infor);

TMPL_EXTERN template tuple<py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<TMPL_FL>, py::array_t<uint32_t>>
flat_sparse_tensor_fuse<TMPL_Q, TMPL_FL>(const py::array_t<uint32_t> &aqs,
                                         const py::array_t<uint32_t> &ashs,
                                         const py::array_t<TMPL_FL> &adata,
                                         const py::array_t<uint32_t> &aidxs,
                                         const py::array_t<int32_t> &idxs,
                                         const map_fusing &info,
                                         const string &pattern);

#else

TMPL_EXTERN template map_fusing
flat_sparse_tensor_kron_sum_info<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                                         const py::array_t<uint32_t> &ashs,
                                         const string &pattern);

TMPL_EXTERN template tuple<py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<uint32_t>>
flat_sparse_tensor_skeleton<TMPL_Q>(
    const vector<unordered_map<uint32_t, uint32_t>> &infos,
    const string &pattern, uint32_t fdq);

TMPL_EXTERN template vector<unordered_map<uint32_t, uint32_t>>
flat_sparse_tensor_get_infos<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                                     const py::array_t<uint32_t> &ashs);

TMPL_EXTERN template tuple<py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<double>, py::array_t<uint32_t>,
                           py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<double>, py::array_t<uint32_t>>
flat_sparse_left_canonicalize<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                                      const py::array_t<uint32_t> &ashs,
                                      const py::array_t<double> &adata,
                                      const py::array_t<uint32_t> &aidxs);

TMPL_EXTERN template tuple<py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<double>, py::array_t<uint32_t>,
                           py::array_t<uint32_t>, py::array_t<uint32_t>,
                           py::array_t<double>, py::array_t<uint32_t>>
flat_sparse_right_canonicalize<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                                       const py::array_t<uint32_t> &ashs,
                                       const py::array_t<double> &adata,
                                       const py::array_t<uint32_t> &aidxs);

TMPL_EXTERN template tuple<
    py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<double>,
    py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<uint32_t>,
    py::array_t<double>, py::array_t<uint32_t>, py::array_t<uint32_t>,
    py::array_t<uint32_t>, py::array_t<double>, py::array_t<uint32_t>>
flat_sparse_left_svd<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                             const py::array_t<uint32_t> &ashs,
                             const py::array_t<double> &adata,
                             const py::array_t<uint32_t> &aidxs);

TMPL_EXTERN template tuple<
    py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<double>,
    py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<uint32_t>,
    py::array_t<double>, py::array_t<uint32_t>, py::array_t<uint32_t>,
    py::array_t<uint32_t>, py::array_t<double>, py::array_t<uint32_t>>
flat_sparse_right_svd<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                              const py::array_t<uint32_t> &ashs,
                              const py::array_t<double> &adata,
                              const py::array_t<uint32_t> &aidxs);

TMPL_EXTERN template pair<
    tuple<py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<double>,
          py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<uint32_t>,
          py::array_t<double>, py::array_t<uint32_t>>,
    py::array_t<uint32_t>>
flat_sparse_left_canonicalize_indexed<TMPL_Q>(
    const py::array_t<uint32_t> &aqs, const py::array_t<uint32_t> &ashs,
    const py::array_t<double> &adata, const py::array_t<uint32_t> &aidxs);

TMPL_EXTERN template pair<
    tuple<py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<double>,
          py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<uint32_t>,
          py::array_t<double>, py::array_t<uint32_t>>,
    py::array_t<uint32_t>>
flat_sparse_right_canonicalize_indexed<TMPL_Q>(
    const py::array_t<uint32_t> &aqs, const py::array_t<uint32_t> &ashs,
    const py::array_t<double> &adata, const py::array_t<uint32_t> &aidxs);

TMPL_EXTERN template pair<
    tuple<py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<double>,
          py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<uint32_t>,
          py::array_t<double>, py::array_t<uint32_t>, py::array_t<uint32_t>,
          py::array_t<uint32_t>, py::array_t<double>, py::array_t<uint32_t>>,
    py::array_t<uint32_t>>
flat_sparse_left_svd_indexed<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                                     const py::array_t<uint32_t> &ashs,
                                     const py::array_t<double> &adata,
                                     const py::array_t<uint32_t> &aidxs);

TMPL_EXTERN template pair<
    tuple<py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<double>,
          py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<uint32_t>,
          py::array_t<double>, py::array_t<uint32_t>, py::array_t<uint32_t>,
          py::array_t<uint32_t>, py::array_t<double>, py::array_t<uint32_t>>,
    py::array_t<uint32_t>>
flat_sparse_right_svd_indexed<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                                      const py::array_t<uint32_t> &ashs,
                                      const py::array_t<double> &adata,
                                      const py::array_t<uint32_t> &aidxs);

TMPL_EXTERN template tuple<
    py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<double>,
    py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<uint32_t>,
    py::array_t<double>, py::array_t<uint32_t>, py::array_t<uint32_t>,
    py::array_t<uint32_t>, py::array_t<double>, py::array_t<uint32_t>>
flat_sparse_tensor_svd<TMPL_Q>(const py::array_t<uint32_t> &aqs,
                               const py::array_t<uint32_t> &ashs,
                               const py::array_t<double> &adata,
                               const py::array_t<uint32_t> &aidxs, int idx,
                               const map_fusing &linfo, const map_fusing &rinfo,
                               const string &pattern);

TMPL_EXTERN template tuple<
    py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<double>,
    py::array_t<uint32_t>, py::array_t<uint32_t>, py::array_t<uint32_t>,
    py::array_t<double>, py::array_t<uint32_t>, py::array_t<uint32_t>,
    py::array_t<uint32_t>, py::array_t<double>, py::array_t<uint32_t>, double>
flat_sparse_truncate_svd<TMPL_Q>(
    const py::array_t<uint32_t> &lqs, const py::array_t<uint32_t> &lshs,
    const py::array_t<double> &ldata, const py::array_t<uint32_t> &lidxs,
    const py::array_t<uint32_t> &sqs, const py::array_t<uint32_t> &sshs,
    const py::array_t<double> &sdata, const py::array_t<uint32_t> &sidxs,
    const py::array_t<uint32_t> &rqs, const py::array_t<uint32_t> &rshs,
    const py::array_t<double> &rdata, const py::array_t<uint32_t> &ridxs,
    int max_bond_dim, double cutoff, double max_dw, double norm_cutoff,
    bool eigen_values);

#endif

#endif