# https://www.vasp.at/wiki/index.php/Bandgap_of_Si_in_GW
# Step 1: a DFT groundstate calculation
cp INCAR1 INCAR
mpirun -np 8 vasp_std

# Step 2: obtain DFT virtual orbitals
cp INCAR2 INCAR
mpirun -np 8 vasp_std

# cp WAVECAR WAVECAR.DIAG
# cp WAVEDER WAVEDER.DIAG

# Step 3: the actual GW calculation
cp INCAR3 INCAR
mpirun -np 8 vasp_std

# Step 4:find the QP-energy
bash gap_GW.sh OUTCAR