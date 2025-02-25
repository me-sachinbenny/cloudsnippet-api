import re

class FindTools:
    def __init__(self):
        self.VALID_TOOLS = ["Docker", "Kubernetes", "PostgreSQL", "Redis", "MongoDB", "C++", ".NET", "Python", "FastAPI", "Terraform", "OpenAI-GPT"]

    def extract_tool_names(self, query: str):
        tool_regex = r"\b(?:{})\b".format("|".join(map(re.escape, self.VALID_TOOLS)))
        return re.findall(tool_regex, query, re.IGNORECASE)