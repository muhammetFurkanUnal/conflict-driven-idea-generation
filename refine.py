import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# Assuming these are available in your environment
from config import settings
from utils import read_file

class RefineAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite", debug:bool = False):
        os.environ["GOOGLE_API_KEY"] = settings.api_key.gemini25flash
        self.model = ChatGoogleGenerativeAI(model=model_name)

        self.debug = debug

    def run(self, code, thesis, prompt_file:str) -> str:
        self.system_prompt = read_file(prompt_file)

        prompt = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"{code}\n\n{thesis}")
        ]
        
        if self.debug:
            response = "placeholder for refined code"
        else:
            response = self.model.invoke(prompt).content
            settings.requests += 1
        
        return response

