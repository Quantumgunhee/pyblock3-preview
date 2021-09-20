
from pyscf import gto, scf, ci, mcscf, ao2mo, symm
import numpy as np

mol = gto.M(atom="""
        O  0.000000  0.000000  0.000000
        H  0.758602  0.000000  0.504284
        H  0.758602  0.000000  -0.504284
    """, basis='sto3g', verbose=3, symmetry='c2v')
mf = scf.RHF(mol)
mf.kernel()

n_sites = mol.nao
n_elec = sum(mol.nelec)
tol = 1E-13

fcidump_sym = ["A1", "B1", "B2", "A2"]
optimal_reorder = ["A1", "B1", "B2", "A2"]
orb_sym_str = symm.label_orb_symm(mol, mol.irrep_name, mol.symm_orb, mf.mo_coeff)
orb_sym = np.array([fcidump_sym.index(i) + 1 for i in orb_sym_str])

print(orb_sym)

mc = mcscf.CASCI(mf, n_sites, n_elec)
h1e, e_core = mc.get_h1cas()
g2e = mc.get_h2cas()
g2e = ao2mo.restore(1, g2e, n_sites)

h1e[np.abs(h1e) < tol] = 0
g2e[np.abs(g2e) < tol] = 0

n = n_sites
gh1e = np.zeros((n * 2, n * 2), dtype=complex)
gg2e = np.zeros((n * 2, n * 2, n * 2, n * 2), dtype=complex)

for i in range(n * 2):
    for j in range(i % 2, n * 2, 2):
        gh1e[i, j] = h1e[i // 2, j // 2]

for i in range(n * 2):
    for j in range(i % 2, n * 2, 2):
        for k in range(n * 2):
            for l in range(k % 2, n * 2, 2):
                gg2e[i, j, k, l] = g2e[i // 2, j // 2, k // 2, l // 2]

# atomic mean-field spin-orbit integral (AMFI)
hsoao = np.zeros((3, 7, 7), dtype=complex)
v = 2.1281747964476273E-004j * 2
hsoao[:] = 0
hsoao[0, 4, 3] = hsoao[1, 2, 4] = hsoao[2, 3, 2] = v
hsoao[0, 3, 4] = hsoao[1, 4, 2] = hsoao[2, 2, 3] = -v

hso = np.einsum('rij,ip,jq->rpq', hsoao, mf.mo_coeff, mf.mo_coeff)

for i in range(n * 2):
    for j in range(i % 2, n * 2, 2):
        if i % 2 == 0 and j % 2 == 0: # aa
            gh1e[i, j] += hso[2, i // 2, j // 2]
        elif i % 2 == 1 and j % 2 == 1: # bb
            gh1e[i, j] -= hso[2, i // 2, j // 2]
        elif i % 2 == 0 and j % 2 == 1: # ab
            gh1e[i, j] += hso[0, i // 2, j // 2] - hso[1, i // 2, j // 2] * 1j
        elif i % 2 == 1 and j % 2 == 0: # ba
            gh1e[i, j] += hso[0, i // 2, j // 2] + hso[1, i // 2, j // 2] * 1j

from pyblock3.fcidump import FCIDUMP
from pyblock3.hamiltonian import Hamiltonian
from pyblock3.algebra.mpe import CachedMPE, MPE

# orb_sym = [orb_sym[i // 2] for i in range(n * 2)]
orb_sym = [0] * (n * 2)

fd = FCIDUMP(pg='d2h', n_sites=n * 2, n_elec=n_elec, twos=n_elec, ipg=0, h1e=gh1e,
    g2e=gg2e, orb_sym=orb_sym, const_e=e_core)

SPIN, SITE, OP = 1, 2, 16384
def generate_qc_terms(n_sites, h1e, g2e, cutoff=1E-9):
    OP_C, OP_D = 0 * OP, 1 * OP
    h_values = []
    h_terms = []
    for i in range(0, n_sites):
        for j in range(0, n_sites):
            t = h1e[i, j]
            if abs(t) > cutoff:
                for s in [0, 1]:
                    h_values.append(t)
                    h_terms.append([OP_C + i * SITE + s * SPIN,
                                    OP_D + j * SITE + s * SPIN, -1, -1])
    for i in range(0, n_sites):
        for j in range(0, n_sites):
            for k in range(0, n_sites):
                for l in range(0, n_sites):
                    v = g2e[i, j, k, l]
                    if abs(v) > cutoff:
                        for sij in [0, 1]:
                            for skl in [0, 1]:
                                h_values.append(0.5 * v)
                                h_terms.append([OP_C + i * SITE + sij * SPIN,
                                                OP_C + k * SITE + skl * SPIN,
                                                OP_D + l * SITE + skl * SPIN,
                                                OP_D + j * SITE + sij * SPIN])
    if len(h_values) == 0:
        return np.zeros((0, ), dtype=np.complex128), np.zeros((0, 4), dtype=np.int32)
    else:
        return np.array(h_values, dtype=np.complex128), np.array(h_terms, dtype=np.int32)

def build_qc(hamil, cutoff=1E-9, max_bond_dim=-1):
    terms = generate_qc_terms(
            hamil.fcidump.n_sites, hamil.fcidump.h1e, hamil.fcidump.g2e, 1E-13)
    mm = hamil.build_mpo(terms, cutoff=cutoff, max_bond_dim=max_bond_dim,
        const=hamil.fcidump.const_e)
    return mm

hamil = Hamiltonian(fd, flat=True)
mpo = build_qc(hamil, max_bond_dim=-5)
mpo, error = mpo.compress(left=True, cutoff=1E-9, norm_cutoff=1E-9)
mps = hamil.build_mps(250)

bdims = [250] * 5 + [500] * 5
noises = [1E-5] * 2 + [1E-6] * 4 + [1E-7] * 3 + [0]
davthrds = [5E-3] * 4 + [1E-4] * 4 + [1E-5]

nroots = 4
extra_mpes = [None] * (nroots - 1)
for ix in range(nroots - 1):
    xmps = hamil.build_mps(250)
    extra_mpes[ix] = MPE(xmps, mpo, xmps)

dmrg = MPE(mps, mpo, mps).dmrg(bdims=bdims, noises=noises,
    dav_thrds=davthrds, iprint=2, n_sweeps=10, extra_mpes=extra_mpes)
ener = dmrg.energies[-1]
print("FINAL ENERGY          = ", ener)
