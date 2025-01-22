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
sleep 5

# Check if the simulation ran successfully
if [[ $? -eq 0 ]]; then
    echo "VASP simulation completed successfully."
else
    echo "Error: VASP simulation failed."
    exit 1
fi
# Extract energy from OUTCAR
energy_line=$(grep 'energy  without entropy' OUTCAR | tail -n 1)
echo $energy_line

# Extract energy from OUTCAR
energy_line=$(grep 'energy  without entropy' OUTCAR | tail -n 1)
echo $energy_line
