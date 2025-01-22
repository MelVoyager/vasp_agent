# https://www.vasp.at/wiki/index.php/Bandstructure_of_Si_in_GW_(VASP2WANNIER90)
# Step 1: default PBE
cp INCAR1 INCAR
mpirun -np 8 vasp_std

# Step 2: virtual orbitals
cp INCAR2 INCAR
mpirun -np 8 vasp_std

# Step 3: GW + WANNIER90
cp INCAR3 INCAR
mpirun -np 8 vasp_std

# Step 4:WANNIER90
wannier90.x wannier90