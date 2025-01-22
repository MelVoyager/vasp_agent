#!/bin/bash

# Check if the necessary input files are present
required_files=("INCAR" "POSCAR" "POTCAR" "KPOINTS")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: $file is missing."
        exit 1
    fi
done

# Run the VASP simulation
echo "Starting VASP simulation..."
vasp_std > vasp_output.log

# Check if the simulation completed successfully
if [ $? -eq 0 ]; then
    echo "VASP simulation completed successfully."
else
    echo "VASP simulation failed. Check vasp_output.log for details."
    exit 1
fi