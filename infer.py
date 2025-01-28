from agent import agent
from tqdm import tqdm
import json

myagent = agent(
    "gpt-4o", #"gpt-4o-mini-2024-07-18",
    "/home/xiazeyu21/Programs/vasp_agent/test/gen",
    context_cutoff=30000,
)

# task = {
#     "task_inst": "Using VASP to calculate the lattice constant of Si. You need to write a POSCAR file.",
#     "domain_knowledge": "",
#     "output_fname": "./test/gen/POSCAR"
# }
with open("./dataset/si_lattice.json", "r") as f:
    problem = json.load(f)
    for id in tqdm(range(5, len(problem)-1)):
        trajectory = myagent.solve_task(problem[id])
        print(trajectory)
    # task = problem[-1]
    # trajectory = myagent.solve_task(task)
    print(trajectory)