import json
import os
from engine import OpenaiEngine

class DFTTaskDecomposer:
    def __init__(self, llm_engine_name, examples_folder="./example", max_retries=10):
        self.llm_engine = OpenaiEngine(llm_engine_name)
        self.examples_folder = examples_folder
        self.max_retries = max_retries

    def load_examples(self):
        examples = []
        for filename in os.listdir(self.examples_folder):
            if filename.endswith(".json"):
                with open(os.path.join(self.examples_folder, filename), "r", encoding="utf-8") as f:
                    examples.append(json.load(f))
        return examples

    def decompose_task(self, user_task_description, output_json_path):
        examples = self.load_examples()
        examples_str = json.dumps(examples, indent=4, ensure_ascii=False)

        system_prompt = (
            "You are an expert in DFT and VASP-related computations. Below are some example JSON files that "
            "show how a given DFT-related task can be decomposed into a list of subtasks. Each subtask is an object "
            "with the following fields:\n"
            "- task_inst: A string describing the instruction for the subtask.\n"
            "- type: A string among [\"vasp\", \"bash\", \"command\", \"python\", \"None\"] describing the type of operation.\n"
            "- domain_knowledge: A string describing domain knowledge needed for that subtask (can be empty if not needed).\n"
            "- out_fname: A string for the output file name associated with that subtask (can be empty if not applicable).\n\n"
            "Study the examples carefully, and then, based on the user's new task description, produce a similar JSON array. "
            "Do not add any explanation, just return the JSON.\n\n"
            "Here are the examples:\n"
            f"{examples_str}\n\n"
            "Now, the user's task description is:\n"
            f"{user_task_description}\n\n"
            "Please return ONLY the JSON array of tasks, no additional explanations."
        )

        self.msg = [
            {'role': 'assistant', 'content': system_prompt}
        ]

        retries = 0
        while retries < self.max_retries:
            try:
                assistant_output, prompt_tokens, completion_tokens = self.llm_engine.respond(
                    self.msg, temperature=0.2, top_p=0.95
                )

                tasks = json.loads(assistant_output)

                with open(output_json_path, "w", encoding="utf-8") as f:
                    json.dump(tasks[0], f, indent=4, ensure_ascii=False)

                print(f"Task decomposition completed. Results saved to {output_json_path}")
                return tasks

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Attempt {retries + 1} failed: {str(e)}")
                retries += 1

        raise RuntimeError(f"Failed to decompose task after {self.max_retries} retries.")

# Usage example
dft_decomposer = DFTTaskDecomposer(llm_engine_name="gpt-4o", examples_folder="./example")
user_description = "Use VASP to perform a density of state calculation on Ga."
dft_decomposer.decompose_task(user_description, "./dataset/fe_lattice.json")
