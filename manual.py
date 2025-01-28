import requests
from bs4 import BeautifulSoup
import openai

class Manual:
    def __init__(self, task_description, manual_url):
        self.task_description = task_description
        self.manual_url = manual_url

    def fetch_manual_content(self):
        response = requests.get(self.manual_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find(id='manual-content').get_text()
            return content
        else:
            raise Exception('无法获取手册内容')

    def query_gpt(self, prompt):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()

    def get_guidance(self):
        manual_content = self.fetch_manual_content()
        prompt = f"任务描述: {self.task_description}\n\nVASP 手册内容: {manual_content}\n\n请根据上述信息提供指导:"
        guidance = self.query_gpt(prompt)
        return guidance
