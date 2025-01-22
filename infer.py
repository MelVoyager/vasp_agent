from agent import Agent, TaskAgent
from tqdm import tqdm
import json, os
import argparse

# agent = Agent(
#     "gpt-4o", 
#     # "gpt-4o-mini-2024-07-18",
#     # "/home/xiazeyu21/Programs/Agent/test/gen",
#     "/home/trunk/RTrunk0/congjie/autoexp/vasp_agent/test/gen",
#     context_cutoff=30000,
# )

agent = TaskAgent(
    # "gpt-4o", 
    "gpt-4o-mini-2024-07-18",
    context_cutoff=30000,
    max_iter = 10,
    use_domain_knowledge = True
)

parser = argparse.ArgumentParser()
parser.add_argument('--ws', help='workspace')
args = parser.parse_args()

# TODO: this is main function for now...
# 1. better running and logging management -- simple verison
# 2. check if naive version works -- without context, no
# 3. try task agent with context
# 4. add a docker or use framework

task_list = [
    # 'dataset/bandgap_si_gw',
    'dataset/fccSidos',
    # 'dataset/si_bandstructure_gw',
]

for task in task_list:
    original_directory = os.getcwd()
    task_name = task.split('/')[-1]
    print(f'running task: {task_name}')
    os.system(f'cp -r {task} {args.ws}')
    os.chdir(f'{args.ws}/{task_name}')
    files = os.listdir('.')
    with open('task.json', 'r') as f:
        problems = json.load(f)
    print(problems)
    for i, problem in enumerate(problems):
        print('-'* 20 + f'running problem: {i}!!!' + '-'* 20)
        print(f'{problem["task_inst"]}')
        trajectory = agent.solve_task(problem)
        print(f'finished problem: {problem["task_inst"]}')
        print(trajectory)
    os.chdir(original_directory)
    print(f'finished with task: {task_name}')



# old version, deprecated.
# with open("./dataset/Si_Lattice_modified.json", "r") as f:
#     problem = json.load(f)
#     for id in tqdm(range(0, len(problem))):
#         trajectory = myagent.solve_task(problem[id])
#         print(trajectory)
#     # task = problem[-1]
#     # trajectory = myagent.solve_task(task)
#     print(trajectory)