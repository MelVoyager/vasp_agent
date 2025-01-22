#!/bin/bash
# Run VASP simulation for Si

# Check if VASP is installed
if ! command -v vasp_std &> /dev/null
then
    echo "VASP is not installed or not in the PATH."
    exit 1
fi

# Run VASP
echo "Starting VASP simulation..."
vasp_std

# Check if VASP completed successfully
if [ $? -eq 0 ]; then
    echo "VASP simulation completed successfully."
else
    echo "VASP simulation failed."
    exit 1
fi