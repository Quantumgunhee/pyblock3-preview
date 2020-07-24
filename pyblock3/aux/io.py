
#  block2: Efficient MPO implementation of quantum chemistry DMRG
#  Copyright (C) 2020 Huanchen Zhai <hczhai@caltech.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
#
#

"""
MPS/MPO format transform between block2 and pyblock2.
"""

import numpy as np
from ..algebra.core import SparseTensor, SubTensor, FermionTensor
from ..algebra.mps import MPS
from ..algebra.symmetry import SZ as ASZ

from block2 import OpTypes, QCTypes, SZ
from block2.sz import StateInfo, MPOQC


class TensorTools:
    @staticmethod
    def from_block2_left_fused(bspmat, l, m, lm, clm):
        """Translate block2 rank2 left-fused SparseMatrix to pyblock2 rank3 tensor."""
        blocks = []
        for i in range(bspmat.info.n):
            qlm = bspmat.info.quanta[i].get_bra(bspmat.info.delta_quantum)
            qr = bspmat.info.quanta[i].get_ket()
            if bspmat.info.is_wavefunction:
                qr = -qr
            ib = lm.find_state(qlm)
            bbed = clm.n if ib == lm.n - 1 else clm.n_states[ib + 1]
            pmat = np.array(bspmat[i])
            nr = pmat.shape[1]
            ip = 0
            for bb in range(clm.n_states[ib], bbed):
                ibba = clm.quanta[bb].data >> 16
                ibbb = clm.quanta[bb].data & 0xFFFF
                ql, nl = l.quanta[ibba], l.n_states[ibba]
                qm, nm = m.quanta[ibbb], m.n_states[ibbb]
                rmat = pmat[ip: ip + nl * nm, :].reshape((nl, nm, nr))
                blocks.append(
                    SubTensor(q_labels=(ql, qm, qr), reduced=rmat.copy()))
                ip += nl * nm
            assert ip == pmat.shape[0]
        return SparseTensor(blocks=blocks)

    @staticmethod
    def from_block2_right_fused(bspmat, m, r, mr, cmr):
        """Translate block2 rank2 right-fused SparseMatrix to pyblock2 rank3 tensor."""
        blocks = []
        for i in range(bspmat.info.n):
            ql = bspmat.info.quanta[i].get_bra(bspmat.info.delta_quantum)
            qmr = bspmat.info.quanta[i].get_ket()
            if bspmat.info.is_wavefunction:
                qmr = -qmr
            ik = mr.find_state(qmr)
            kked = cmr.n if ik == mr.n - 1 else cmr.n_states[ik + 1]
            pmat = np.array(bspmat[i])
            nl = pmat.shape[0]
            ip = 0
            for kk in range(cmr.n_states[ik], kked):
                ikka = cmr.quanta[kk].data >> 16
                ikkb = cmr.quanta[kk].data & 0xFFFF
                qm, nm = m.quanta[ikka], m.n_states[ikka]
                qr, nr = r.quanta[ikkb], r.n_states[ikkb]
                rmat = pmat[:, ip:ip + nm * nr].reshape((nl, nm, nr))
                blocks.append(
                    SubTensor(q_labels=(ql, qm, qr), reduced=rmat.copy()))
                ip += nm * nr
            assert ip == pmat.shape[1]
        return SparseTensor(blocks=blocks)


class MPSTools:
    @staticmethod
    def from_block2(bmps):
        """Translate block2 MPS to pyblock2 MPS."""
        tensors = [None] * bmps.n_sites
        canonical_form = []
        for i, ic in enumerate(bmps.canonical_form):
            if ic == 'C':
                if i == 0:
                    canonical_form.append('L')
                elif i == bmps.n_sites - 1:
                    canonical_form.append('R')
                else:
                    assert False
            else:
                canonical_form.append(ic)
        for i in range(0, bmps.n_sites):
            if canonical_form[i] == 'L':
                bmps.info.load_left_dims(i)
                l = bmps.info.left_dims[i]
                m = bmps.info.get_basis(i)
                lm = StateInfo.tensor_product_ref(
                    l, m, bmps.info.left_dims_fci[i + 1])
                clm = StateInfo.get_connection_info(l, m, lm)
                bmps.load_tensor(i)
                tensors[i] = TensorTools.from_block2_left_fused(
                    bmps.tensors[i], l, m, lm, clm)
                bmps.unload_tensor(i)
                clm.deallocate()
                lm.deallocate()
                l.deallocate()
            else:
                bmps.info.load_right_dims(i + 1)
                m = bmps.info.get_basis(i)
                r = bmps.info.right_dims[i + 1]
                mr = StateInfo.tensor_product_ref(
                    m, r, bmps.info.right_dims_fci[i])
                cmr = StateInfo.get_connection_info(m, r, mr)
                bmps.load_tensor(i)
                tensors[i] = TensorTools.from_block2_right_fused(
                    bmps.tensors[i], m, r, mr, cmr)
                bmps.unload_tensor(i)
                cmr.deallocate()
                mr.deallocate()
                r.deallocate()
        for block in tensors[bmps.center].blocks:
            block.q_labels = block.q_labels[:-1] + \
                (bmps.info.target - block.q_labels[-1], )
        for i in range(bmps.center + bmps.dot, bmps.n_sites):
            for block in tensors[i].blocks:
                block.q_labels = (bmps.info.target - block.q_labels[0],
                                  block.q_labels[1], bmps.info.target - block.q_labels[2])
        for i in range(0, bmps.n_sites):
            for block in tensors[i].blocks:
                block.q_labels = tuple(ASZ(x.n, x.twos, x.pg)
                                       for x in block.q_labels)
        return MPS(tensors=tensors)


class MPOTools:
    @staticmethod
    def from_block2(bmpo):
        """Translate block2 (un-simplified) MPO to pyblock2 MPO."""
        assert bmpo.schemer is None
        if isinstance(bmpo, MPOQC):
            assert bmpo.mode == QCTypes.NC or bmpo.mode == QCTypes.CN
        tensors = [None] * bmpo.n_sites
        # tranlate operator name symbols to quantum labels
        idx_mps, idx_qss, idx_imps = [], [], []
        for i in range(0, bmpo.n_sites - 1):
            lidx_mp = {}
            lidx_qs = [op.q_label for op in bmpo.left_operator_names[i].data]
            for ip, q in enumerate(lidx_qs):
                if q not in lidx_mp:
                    lidx_mp[q] = []
                lidx_mp[q].append(ip)
            limp = {iv: iiv for _, v in lidx_mp.items()
                    for iiv, iv in enumerate(v)}
            idx_mps.append(lidx_mp)
            idx_qss.append(lidx_qs)
            idx_imps.append(limp)
        for i in range(0, bmpo.n_sites):
            assert bmpo.tensors[i].lmat == bmpo.tensors[i].rmat
            mat = bmpo.tensors[i].lmat
            ops = bmpo.tensors[i].ops
            map_blocks_odd = {}
            map_blocks_even = {}
            if i == 0:
                for k, expr in enumerate(mat.data):
                    if expr.get_type() == OpTypes.Zero:
                        continue
                    elif expr.get_type() == OpTypes.Elem:
                        spmat = ops[expr.abs()]
                        if spmat.factor == 0 or spmat.info.n == 0:
                            continue
                        qr = idx_qss[i][k]
                        nr = len(idx_mps[i][qr])
                        ir = idx_imps[i][k]
                        for p in range(spmat.info.n):
                            qu = spmat.info.quanta[p].get_bra(
                                spmat.info.delta_quantum)
                            qd = spmat.info.quanta[p].get_ket()
                            nu = spmat.info.n_states_bra[p]
                            nd = spmat.info.n_states_ket[p]
                            qx = (SZ(0, 0, 0), qu, qd, qr)
                            map_blocks = map_blocks_odd if (
                                qu - qd).is_fermion else map_blocks_even
                            if qx not in map_blocks:
                                map_blocks[qx] = SubTensor(
                                    q_labels=qx, reduced=np.zeros((1, nu, nd, nr)))
                            map_blocks[qx][0, :, :, ir] += expr.factor * \
                                spmat.factor * np.array(spmat[p])
                    else:
                        assert False
            elif i == bmpo.n_sites - 1:
                for k, expr in enumerate(mat.data):
                    if expr.get_type() == OpTypes.Zero:
                        continue
                    elif expr.get_type() == OpTypes.Elem:
                        spmat = ops[expr.abs()]
                        if spmat.factor == 0 or spmat.info.n == 0:
                            continue
                        ql = idx_qss[i - 1][k]
                        nl = len(idx_mps[i - 1][ql])
                        il = idx_imps[i - 1][k]
                        for p in range(spmat.info.n):
                            qu = spmat.info.quanta[p].get_bra(
                                spmat.info.delta_quantum)
                            qd = spmat.info.quanta[p].get_ket()
                            nu = spmat.info.n_states_bra[p]
                            nd = spmat.info.n_states_ket[p]
                            qx = (ql, qu, qd, SZ(0, 0, 0))
                            map_blocks = map_blocks_odd if (
                                qu - qd).is_fermion else map_blocks_even
                            if qx not in map_blocks:
                                map_blocks[qx] = SubTensor(
                                    q_labels=qx, reduced=np.zeros((nl, nu, nd, 1)))
                            map_blocks[qx][il, :, :, 0] += expr.factor * \
                                spmat.factor * np.array(spmat[p])
                    else:
                        assert False
            else:
                for (j, k), expr in zip(mat.indices, mat.data):
                    if expr.get_type() == OpTypes.Zero:
                        continue
                    elif expr.get_type() == OpTypes.Elem:
                        spmat = ops[expr.abs()]
                        if spmat.factor == 0 or spmat.info.n == 0:
                            continue
                        ql, qr = idx_qss[i - 1][j], idx_qss[i][k]
                        nl, nr = len(idx_mps[i - 1][ql]
                                     ), len(idx_mps[i][qr])
                        il, ir = idx_imps[i - 1][j], idx_imps[i][k]
                        for p in range(spmat.info.n):
                            qu = spmat.info.quanta[p].get_bra(
                                spmat.info.delta_quantum)
                            qd = spmat.info.quanta[p].get_ket()
                            nu = spmat.info.n_states_bra[p]
                            nd = spmat.info.n_states_ket[p]
                            qx = (ql, qu, qd, qr)
                            map_blocks = map_blocks_odd if (
                                qu - qd).is_fermion else map_blocks_even
                            if np.linalg.norm(np.array(spmat[p])) == 0:
                                continue
                            if qx not in map_blocks:
                                map_blocks[qx] = SubTensor(
                                    q_labels=qx, reduced=np.zeros((nl, nu, nd, nr)))
                            map_blocks[qx][il, :, :, ir] += expr.factor * \
                                spmat.factor * np.array(spmat[p])
                    else:
                        assert False
            tensors[i] = FermionTensor(
                odd=list(map_blocks_odd.values()), even=list(map_blocks_even.values()))
        for i in range(0, len(tensors)):
            for block in tensors[i].odd.blocks + tensors[i].even.blocks:
                block.q_labels = tuple(ASZ(x.n, x.twos, x.pg)
                                       for x in block.q_labels)
        return MPS(tensors=tensors, const=bmpo.const_e)
