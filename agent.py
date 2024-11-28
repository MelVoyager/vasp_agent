from engine import OpenaiEngine
from litellm.utils import trim_messages
from pathlib import Path
from adapter import adapter
import re

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
PROMPT_DICT = {
    "vasp": VASP_PROMPT,
    "python": PYTHON_PROMPT,
    "bash": BASH_PROMPT,
    "command": COMMAND_PROMPT,
    "None":""
}

class agent():
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
        self.adapter = adapter(workdir, "agent")

    def get_msg(self, task):
        usr_msg = (
            "\n" + task["task_inst"] + 
            ("\n" + str(task["domain_knowledge"]) if self.use_knowledge else "")
        )
        # self.msg.append({"role":"user", "content": usr_msg})
        self.sys_msg = (
            PROMPT_DICT[task["type"]] + "\n\n" + 
            FORMAT_PROMPT + "\n\n" 
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

        return command

    def solve_task(self, task):
        
        self.msg = self.get_msg(task) # self.msg stores [system_prompt, usr_prompt1, usr_prompt2, ...]
        self.history.append(self.msg[-1])
        unfinished = True
        eval = False
        while(unfinished):
            assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
                self.msg, temperature=0.2, top_p=0.95
            )
            self.history.append(
                {'role': 'assistant', 'content': assistant_output}
            )
            command = self.write_program(task, assistant_output, task["out_fname"])

            if(command):
                returncode, output = self.adapter.run_command(command)
                self.history.append(
                    {'role': 'terminal', 'content': output}
                )
                self.msg.append({"role":"terminal", "content": output})
                if(eval == False):
                    self.msg.append({"role": "system", "content": EVAL_PROMPT})
                    eval = True
            else:
                unfinished = False

        
        # if self.use_self_debug:
        #     for t in range(10):
        #         halt = self.step(out_fname, task["output_fname"])
        #         if halt:
        #             break
        # self.history = [
            # {'role': 'user', 'content': self.sys_msg}
        # ] + self.history
        return {"history": self.history}
