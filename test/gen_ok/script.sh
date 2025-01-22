#!/bin/bash

# Check if the necessary input files are present
if [[ ! -f "INCAR" || ! -f "POSCAR" || ! -f "POTCAR" || ! -f "KPOINTS" ]]; then
    echo "Error: One or more VASP input files (INCAR, POSCAR, POTCAR, KPOINTS) are missing."
    exit 1
fi

# Run the VASP simulation
vasp_std

# Check if the simulation was successful by looking for the OUTCAR file
if [[ -f "OUTCAR" ]]; then
    echo "VASP simulation completed successfully."
else
    echo "Error: VASP simulation did not complete successfully."
    exit 1
fi