from engine import OpenaiEngine
from litellm.utils import trim_messages
from pathlib import Path
from adapter import adapter, Interface
import re, sys
import copy

VASP_PROMPT = """You are an expert VASP assistant who helps users create high-quality VASP input files based on their requirements. Given a user's request, generate the complete VASP file and ensure it is correctly formatted. Wrap your VASP code in a code block labeled "vasp". For example:
```vasp
Si
  5.43
     1.000  0.000  0.000
     0.000  1.000  0.000
     0.000  0.000  1.000
   1
Direct
  0.000  0.000  0.000
```
"""
PYTHON_PROMPT = """You are a Python programming assistant who helps users write Python code to accomplish their tasks. Given a user's request, write a complete Python program that fulfills their requirements. Wrap your code in a code block labeled "python". For example:
```python
print("Hello World!")
```
"""

BASH_PROMPT = """You are a bash scripting assistant who helps users write shell scripts to automate tasks. Given a user's request, write a bash script that accomplishes the task. Wrap your script in a code block labeled "bash". For example:
```bash
#!/bin/bash
echo "Hello, World!"
```
"""

COMMAND_PROMPT = """You are an assistant that helps users generate terminal commands to execute their programs or scripts. After providing the code, give the appropriate command to run it in the terminal. Wrap your command in a code block labeled "command". For example:
```command
python try.py
```
"""

# SELF_DEBUG_PROMPT = """The user may execute your code and report any exceptions and error messages.
# Please address the reported issues and respond with a fixed, complete program."""

FORMAT_PROMPT = """Please keep your response concise and do not use a code block if it's not intended to be executed.
Please do not suggest a few line changes, incomplete program outline, or partial code that requires the user to modify.
Please do not use any interactive Python commands in your program, such as `!pip install numpy`, which will cause execution errors."""

REQUEST_PROMPT = "You are only required to answer the last prompt in context and all user prompts are just for reference. DO NOT ANSWER THE USER PROMPT BEFORE."

EVAL_PROMPT = "You are provided with the output of terminal. Please refer to message before to check them and determine whether to retrieve information or modify files. Please evaluate the output and verify whether is performed correctly. If not, modify the vasp input files, bash scripts or python files to make it correct. During the process, you are allowed only to provide one terminal command each time to gather information and modify the files. For example, you can use \"cat \"a.py to check the content of a.py, you can also use \"echo new content >> a.sh\" to modify files. Other operations are not allowed. "

FINISHED_PROMPT = """You may have more than one turn interactions to complete the goal.
Make sure to directly output 'ALL_COMPLETED' when you think the overall goal is achieved.
Do not print 'ALL_COMPLETED' from the script you write.
Do not output anything else if you output 'ALL_COMPLETED'."""

PROMPT_DICT = {
    "vasp": VASP_PROMPT,
    "python": PYTHON_PROMPT,
    "bash": BASH_PROMPT,
    "command": COMMAND_PROMPT,
    "None":""
}

class Agent():
    def __init__(self, llm_engine_name, workdir, context_cutoff=30000):
        self.llm_engine = OpenaiEngine(llm_engine_name)
        self.context_cutoff = context_cutoff
        self.use_knowledge = False
        # self.sys_msg = (
        #     SYSTEM_PROMPT + "\n\n" + 
        #     FORMAT_PROMPT + "\n\n" 
        # )
        # self.msg = [{"role": "system", "content":self.sys_msg}]
        self.history = []
        
        # script_path = Path(__file__).resolve()
        # self.adapter = adapter(workdir, "agent")
        self.adapter = Interface()

    def get_msg(self, task):
        usr_msg = (
            "\n" + task["task_inst"] + 
            ("\n" + str(task["domain_knowledge"]) if self.use_knowledge else "")
            # FINISHED_PROMPT + "\n"
        )
        # self.msg.append({"role":"user", "content": usr_msg})
        self.sys_msg = (
            PROMPT_DICT[task["type"]] + "\n\n" + 
            FORMAT_PROMPT + "\n\n" +
            FINISHED_PROMPT + "\n\n" 
        )
        self.msg = [{"role": "system", "content":self.sys_msg}, {"role":"user", "content": usr_msg}]
        
        trimmed_msg = trim_messages(
            self.msg, 
            self.llm_engine.llm_engine_name, 
            max_tokens=self.context_cutoff - 2000
        )
        if len(trimmed_msg) < len(self.msg):
            # the system prompt located in the first place will be trimmed
            trimmed_msg.insert(0, self.sys_msg)
            self.msg = trimmed_msg 

        return self.msg

    def write_program(self, task, assistant_output, out_fname):
        # old_program = ""
        # if Path(out_fname).exists():
        #     with open(out_fname, "r", encoding="utf-8") as f:
        #         old_program = f.read()
        # match = re.search(r"```VASP(.*?)```", assistant_output, re.DOTALL)
        command = None
        result = None
        match task["type"]:
            case "vasp":
                code = re.search(r"```vasp(.*?)```", assistant_output, re.DOTALL).group(1).strip()
            case "python":
                code = re.search(r"```python(.*?)```", assistant_output, re.DOTALL).group(1).strip()
            case "bash":
                code = re.search(r"```bash(.*?)```", assistant_output, re.DOTALL).group(1).strip()
            case "command":
                command = re.search(r"```command(.*?)```", assistant_output, re.DOTALL).group(1).strip()
            case "None":
                code = ""
            case _:
                raise ValueError("Invalid task type")
            
        if out_fname:
            with open(out_fname, "w+", encoding="utf-8") as f:
                f.write(code)
            result = f"{task['type']} code has been successfully written into {out_fname}."

        return command, result

    # def solve_task(self, task):
        
    #     self.msg = self.get_msg(task) # self.msg stores [system_prompt, usr_prompt1, usr_prompt2, ...]
    #     self.history.append(self.msg[-1])
    #     unfinished = True
    #     eval = False
    #     while(unfinished):
    #         assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
    #             self.msg, temperature=0.2, top_p=0.95
    #         )
    #         print('assistant output!!!' + '-'* 20)
    #         print(assistant_output)
    #         self.history.append(
    #             {'role': 'assistant', 'content': assistant_output}
    #         )
    #         command = self.write_program(task, assistant_output, task["out_fname"])

    #         if(command):
    #             returncode, output, error = self.adapter.run_command(command)
    #             if returncode == 0: 
    #                 print('returncode is 0!!!')
    #                 unfinished = False # fininshed
    #             msg = {'role': 'user', 'content': output} # terminal output
    #             # self.history.append(
    #             #     {'role': 'terminal', 'content': output}
    #             # )
    #             # self.msg.append({"role":"terminal", "content": output})
    #             self.history.append(msg)
    #             self.msg.append(msg)
    #             if(eval == False):
    #                 # self.msg.append({"role": "system", "content": EVAL_PROMPT})
    #                 self.msg.append({"role": "user", "content": EVAL_PROMPT})
    #                 eval = True
    #         else:
    #             unfinished = False
    #         print(self.msg)
        
    #     # if self.use_self_debug:
    #     #     for t in range(10):
    #     #         halt = self.step(out_fname, task["output_fname"])
    #     #         if halt:
    #     #             break
    #     # self.history = [
    #         # {'role': 'user', 'content': self.sys_msg}
    #     # ] + self.history
    #     return {"history": self.history}
    
    def solve_task(self, task):
        
        self.msg = self.get_msg(task) # self.msg stores [system_prompt, usr_prompt1, usr_prompt2, ...]
        # self.history.append(self.msg[-1])
        self.history = copy.deepcopy(self.msg)
        unfinished = True
        eval = False

        # assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
        #     self.msg, temperature=0.2, top_p=0.95
        # )
        print('self.msg', self.msg)
        assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
            self.history, temperature=0.2, top_p=0.95
        )
        print('-'* 20 + 'assistant output!!!' + '-'* 20)
        print(assistant_output)
        self.history.append(
            {'role': 'assistant', 'content': assistant_output}
        )
        command, result = self.write_program(task, assistant_output, task["out_fname"])

        unfinished = not 'ALL_COMPLETED' in assistant_output

        while(unfinished):

            if(command):
                returncode, stdout, stderr = self.adapter.run_command(command)
                msg = {'role': 'user', 'content': f'The returncode of previous command execution is {returncode}. The stdout is {stdout}. The stderr is {stderr}.'} # terminal output
                self.history.append(msg)
                self.msg.append(msg)
                if returncode != 0:
                    self.history.append({"role": "user", "content": EVAL_PROMPT})
                    self.msg.append({"role": "user", "content": EVAL_PROMPT})

            if result:
                msg = {'role': 'user', 'content': f'{result}'}
                self.history.append(msg)
                self.msg.append(msg)

            # self.history.append({'role': 'user', 'content': FINISHED_PROMPT})
            # self.msg.append({'role': 'user', 'content': FINISHED_PROMPT})
            
            # assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
            #     self.msg, temperature=0.2, top_p=0.95
            # )
            # print('self.msg', self.msg)
            print(command, result)
            print('-'* 20 + 'new message!!!' + '-'* 20)
            print(msg)
            assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
                self.history, temperature=0.2, top_p=0.95
            )
            print('-'* 20 + 'assistant output!!!' + '-'* 20)
            print(assistant_output)
            self.history.append(
                {'role': 'assistant', 'content': assistant_output}
            )
            unfinished = not 'ALL_COMPLETED' in assistant_output
            if not unfinished: break
            command, result = self.write_program(task, assistant_output, task["out_fname"])


        
        # if self.use_self_debug:
        #     for t in range(10):
        #         halt = self.step(out_fname, task["output_fname"])
        #         if halt:
        #             break
        # self.history = [
            # {'role': 'user', 'content': self.sys_msg}
        # ] + self.history
        return {"history": self.history}


class TaskAgent():
    # with context!
    # messages[0]: system prompt
    # messages[1]: user prompt, summary the task + current step of the task
    def __init__(self, llm_engine_name, context_cutoff=30000, max_iter=10, use_domain_knowledge=False):
        self.llm_engine = OpenaiEngine(llm_engine_name)
        self.context_cutoff = context_cutoff
        self.max_iter = max_iter
        self.use_domain_knowledge = use_domain_knowledge
        self.msg = []
        self.history = []
        self.summary = []
        self.prev_task = "The previous tasks you have accomplished is:\n"
        
        self.adapter = Interface()

    def get_msg(self, task):
        domain_knowledge = "\n" + "The current domain knowledge you can use is:\n" + (str(task["domain_knowledge"]) if task["domain_knowledge"] else "None")\
        if self.use_domain_knowledge else ""
        usr_msg = "\n" + self.prev_task + ("\n".join(self.summary) if len(self.summary) else 'None') +\
            "\n" + "The current task you need to finish is:" +\
            "\n" + task["task_inst"] +\
            domain_knowledge

        self.sys_msg = (
            PROMPT_DICT[task["type"]] + "\n\n" + 
            FORMAT_PROMPT + "\n\n" +
            FINISHED_PROMPT + "\n\n" 
        )
        self.msg = [{"role": "system", "content": self.sys_msg}, 
                    {"role": "user", "content": usr_msg}]
        
        trimmed_msg = trim_messages(
            self.msg, 
            self.llm_engine.llm_engine_name, 
            max_tokens=self.context_cutoff - 2000
        )
        if len(trimmed_msg) < len(self.msg):
            # the system prompt located in the first place will be trimmed
            trimmed_msg.insert(0, self.sys_msg)
            self.msg = trimmed_msg 

        return self.msg

    # TODO: write and execute program should be seperated for better program ending!
    def write_program(self, task, assistant_output, out_fname):
        command = None
        result = None
        match task["type"]:
            case "vasp":
                code = re.search(r"```vasp(.*?)```", assistant_output, re.DOTALL).group(1).strip()
            case "python":
                code = re.search(r"```python(.*?)```", assistant_output, re.DOTALL).group(1).strip()
            case "bash":
                code = re.search(r"```bash(.*?)```", assistant_output, re.DOTALL).group(1).strip()
            case "command":
                command = re.search(r"```command(.*?)```", assistant_output, re.DOTALL).group(1).strip()
            case "None":
                code = ""
            case _:
                raise ValueError("Invalid task type")
            
        if out_fname:
            with open(out_fname, "w+", encoding="utf-8") as f:
                f.write(code)
            result = f"{task['type']} code has been successfully written into {out_fname}."

        return command, result
    
    def solve_task(self, task):
        
        self.msg = self.get_msg(task) # self.msg stores [system_prompt, usr_prompt1, usr_prompt2, ...]
        # self.history.append(self.msg[-1])
        self.history = copy.deepcopy(self.msg)
        print('-'* 20 + 'init messages!!!' + '-'* 20)
        print(self.history)
        print('-'* 20 + 'summary!!!' + '-'* 20)
        print(self.summary)

        assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
            self.history, temperature=0.2, top_p=0.95
        )
        print('-'* 20 + 'assistant output!!!' + '-'* 20)
        print(assistant_output)
        self.history.append(
            {'role': 'assistant', 'content': assistant_output}
        )
        command, result = self.write_program(task, assistant_output, task["out_fname"])

        finished = 'ALL_COMPLETED' in assistant_output

        while not finished:

            if(command):
                returncode, stdout, stderr = self.adapter.run_command(command)
                msg = {'role': 'user', 'content': f'The returncode of previous command execution is {returncode}. The stdout is {stdout}. The stderr is {stderr}.'} # terminal output
                self.history.append(msg)
                self.msg.append(msg)
                if returncode != 0:
                    self.history.append({"role": "user", "content": EVAL_PROMPT})
                    self.msg.append({"role": "user", "content": EVAL_PROMPT})

            if result:
                msg = {'role': 'user', 'content': f'{result}'}
                self.history.append(msg)
                self.msg.append(msg)

            # self.history.append({'role': 'user', 'content': FINISHED_PROMPT})
            # self.msg.append({'role': 'user', 'content': FINISHED_PROMPT})
            
            # assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
            #     self.msg, temperature=0.2, top_p=0.95
            # )
            # print('self.msg', self.msg)
            print('-'* 20 + 'command and result!!!' + '-'* 20)
            print(command, result)
            print('-'* 20 + 'new message!!!' + '-'* 20)
            print(msg)
            assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
                self.history, temperature=0.2, top_p=0.95
            )
            print('-'* 20 + 'assistant output!!!' + '-'* 20)
            print(assistant_output)
            self.history.append(
                {'role': 'assistant', 'content': assistant_output}
            )
            finished = 'ALL_COMPLETED' in assistant_output
            if finished: break
            command, result = self.write_program(task, assistant_output, task["out_fname"])

        if finished:
            msg = "Great! You have finished the current task. Summary what the current task is and what you have done. \
                    You should directly output the summary without any special tags or signals. \
                    This summary will serve as preliminary to help solve the next one."
            msg = {"role": "user", "content": msg}
            self.msg.append(msg)
            self.history.append(msg)
            print('-'* 20 + 'command and result!!!' + '-'* 20)
            print(command, result)
            print('-'* 20 + 'new message!!!' + '-'* 20)
            print(msg)
            assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
                self.history, temperature=0.2, top_p=0.95
            )
            print('-'* 20 + 'assistant output!!!' + '-'* 20)
            print(assistant_output)
            self.history.append(
                {'role': 'assistant', 'content': assistant_output}
            )
            self.summary.append(f"(Step{len(self.summary) + 1}): " + assistant_output)
        else:
            print('Task failed. exiting...')
            sys.exit(1)
        return {"messages": self.msg, "history": self.history}