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
    # Assuming the energy is in a line that contains "energy" and is formatted like "energy = <value>"
    for line in output.splitlines():
        if "energy" in line:
            return float(line.split('=')[1].strip())
    return None

def main():
    poscar_path = 'POSCAR'
    script_path = 'script.sh'
    lattice_constants = np.linspace(3.5, 4.5, 11)  # Example range of lattice constants
    energies = []

    for lc in lattice_constants:
        modify_lattice_constant(poscar_path, lc)
        output = run_simulation(script_path)
        print(output)
        energy = extract_energy(output)
        if energy is not None:
            energies.append(energy)
        else:
            print(f"Energy not found for lattice constant {lc}")

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
    print(f"The optimal lattice constant with the lowest energy is: {optimal_lattice_constant}")

if __name__ == "__main__":
    main()