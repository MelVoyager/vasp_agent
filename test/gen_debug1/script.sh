#!/bin/bash

# Check if the necessary input files are present
required_files=("INCAR" "POSCAR" "POTCAR" "KPOINTS")
for file in "${required_files[@]}"; do
    if [[ ! -f $file ]]; then
        echo "Error: $file is missing."
        exit 1
    fi
done

# Run the VASP simulation
vasp_std

# Check if the simulation ran successfully
if [[ $? -eq 0 ]]; then
    echo "VASP simulation completed successfully."
else
    echo "Error: VASP simulation failed."
    exit 1
fi