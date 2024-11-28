import json

Si_Lattice = [

    {
        "task_inst": "Using VASP to calculate the lattice constant of Si. You need to write a POSCAR file of Si. Here the lattice constant is unknown, therefore you should set as a variable.",
        "type": "vasp",
        "domain_knowledge": "",
        "out_fname": "./test/gen/POSCAR"
    },
    {
        "task_inst": "You need to write a INCAR file for Si.",
        "type": "vasp",
        "domain_knowledge": "",
        "out_fname": "./test/gen/INCAR"
    },
    {
        "task_inst": "You need to write a KPOINTS file for Si.",
        "type": "vasp",
        "domain_knowledge": "",
        "out_fname": "./test/gen/KPOINTS"
    },
    {
        "task_inst": "A POTCAR file for Si is needed, here the path is ./test/gen/POTCAR.",
        "type": "None",
        "domain_knowledge": "",
        "out_fname": ""
    },
    {
        "task_inst": "You have written all the input files for VASP. Now you need to run VASP to calculate the energy of Si. Write a bash script to run VASP simulation. Remember vasp executable is in environment, vasp_std can be run directly.",
        "type": "bash",
        "domain_knowledge": "",
        "out_fname": "./test/gen/script.sh"
    },
    {
        "task_inst": "Give a command in terminal to launch the bash script you written, the path is /home/xiazeyu21/Programs/Agent/test/gen/script.sh",
        "type": "command",
        "domain_knowledge": "",
        "out_fname": ""
    },
    {
        "task_inst": "Write a python code to change the lattice constant varible in your former output. The path is \'./test/gen/POSCAR\'. and you should initialize subprocesses with different lattice constants. In each subprocess, you should filter the output to obatin the energy of the system. Your previous bash script can launch the vasp simulation, whose location is ./test/gen/script.sh. Finally, plot the figure of different lattice constants and the energy, and output the real lattice constant, which has lowest energy.",
        "type": "python",
        "domain_knowledge": "",
        "out_fname": "./test/gen/try.py"
    },
]

with open("./dataset/Si_Lattice.json", "w") as f:
    json.dump(Si_Lattice, f, indent=4)