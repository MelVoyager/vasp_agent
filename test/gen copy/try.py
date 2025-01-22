import subprocess
import numpy as np
import matplotlib.pyplot as plt

def modify_lattice_constant(file_path, lattice_constant):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Assuming the lattice constant is on the second line
    lines[1] = f"{lattice_constant}\n"
    
    with open(file_path, 'w') as file:
        file.writelines(lines)

def run_simulation(script_path):
    result = subprocess.run(['bash', script_path], capture_output=True, text=True)
    return result.stdout

def extract_energy(output):
    # Assuming energy is in a line that contains 'energy' keyword
    for line in output.splitlines():
        if 'energy' in line.lower():
            # Extract the energy value from the line
            return float(line.split()[-1])
    return None

def main():
    poscar_path = './test/gen/POSCAR'
    script_path = './test/gen/script.sh'
    
    lattice_constants = np.linspace(3.5, 4.5, 11)  # Example range of lattice constants
    energies = []

    for lc in lattice_constants:
        modify_lattice_constant(poscar_path, lc)
        output = run_simulation(script_path)
        energy = extract_energy(output)
        if energy is not None:
            energies.append(energy)
        else:
            print(f"Failed to extract energy for lattice constant {lc}")
            energies.append(float('inf'))

    # Plotting
    plt.plot(lattice_constants, energies, marker='o')
    plt.xlabel('Lattice Constant')
    plt.ylabel('Energy')
    plt.title('Energy vs Lattice Constant')
    plt.grid(True)
    plt.show()

    # Find the lattice constant with the lowest energy
    min_energy_index = np.argmin(energies)
    optimal_lattice_constant = lattice_constants[min_energy_index]
    print(f"The optimal lattice constant is: {optimal_lattice_constant}")

if __name__ == "__main__":
    main()