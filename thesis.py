import os
from typing import TypedDict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from config import settings
from utils import read_file

# define state
class ThesisState(TypedDict):
    code: str
    thesis_system_prompt: str
    thesis_arguments: List[str]
    anti_thesis_system_prompt: str
    anti_thesis_arguments: List[str]
    limit_counter: int
    limit: int


class ThesisAgent:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite", debug:bool=False):
        # Set API key during initialization
        os.environ["GOOGLE_API_KEY"] = settings.api_key.gemini25flash
        self.model = ChatGoogleGenerativeAI(model=model_name)
        
        # Instance variable instead of a global variable
        self.full_conversation: List[str] = []
        
        # Build the graph once when the agent is instantiated
        self.thesis_agent = self._build_system()

        self.debug = debug

    # methods
    def thesis_prompt(self, state: ThesisState):
        combined = f"{state['thesis_system_prompt']}\nDebate topic:{state['code']}"
        prompt = [SystemMessage(content=combined)]
        
        for i in range(len(state["anti_thesis_arguments"])):
            prompt.append(AIMessage(content=state["thesis_arguments"][i]))
            prompt.append(HumanMessage(content=state["anti_thesis_arguments"][i]))
        
        if len(state["anti_thesis_arguments"]) == 0:
            prompt.append(HumanMessage(content="The debate is starting. Please present your opening thesis on the topic."))

        return prompt
    

    def anti_thesis_prompt(self, state: ThesisState):
        combined = f"{state['anti_thesis_system_prompt']}\nDebate topic:{state['code']}"
        prompt = [SystemMessage(content=combined)]
        
        for i in range(len(state["anti_thesis_arguments"])):
            prompt.append(HumanMessage(content=state["thesis_arguments"][i]))
            prompt.append(AIMessage(content=state["anti_thesis_arguments"][i]))
            
        # Safely get the latest thesis argument
        if len(state["thesis_arguments"]) > len(state["anti_thesis_arguments"]):
            prompt.append(HumanMessage(content=state["thesis_arguments"][-1]))  
        
        return prompt


    def limit_check(self, state: ThesisState):
        limit_counter = state["limit_counter"]
        limit = state["limit"]

        if limit_counter >= limit:
            print("Debate limit reached.")
            return END
        else:
            return "thesis"


    # define nodes
    def thesis(self, state: ThesisState) -> ThesisState:
        prompt = self.thesis_prompt(state)
        
        if self.debug:
            response = "placeholder for thesis arguments"
        else:
            response = self.model.invoke(prompt).content
            settings.requests += 1

        output = f"\nSpeaker: Thesis\n{response}"
        
        print(output)
        print("-" * 50)
        
        self.full_conversation.append(output)
        state["thesis_arguments"].append(response)
        
        return state


    def anti_thesis(self, state: ThesisState) -> ThesisState:
        prompt = self.anti_thesis_prompt(state)

        if self.debug:
            response = "placeholder for anti-thesis arguments"
        else:
            response = self.model.invoke(prompt).content
            settings.requests += 1

        output = f"\nSpeaker: Anti-Thesis\n{response}"
        
        print(output)
        print("-" * 50)
        
        self.full_conversation.append(output)
        state["anti_thesis_arguments"].append(response)
        state["limit_counter"] += 1
        
        return state


    def _build_system(self):
        # build system
        agent_builder = StateGraph(ThesisState)

        agent_builder.add_node("thesis", self.thesis)
        agent_builder.add_node("anti-thesis", self.anti_thesis)

        agent_builder.add_edge(START, "thesis")
        agent_builder.add_edge("thesis", "anti-thesis")

        agent_builder.add_conditional_edges(
            "anti-thesis",
            self.limit_check,
            ["thesis", END]
        )

        return agent_builder.compile()


    def run_thesis_agent(self, code: str, thesis_prompt_path: str, anti_thesis_prompt_path: str, limit: int = 5) -> List[str]:
        # Reset the conversation for a fresh run
        self.full_conversation = []
        
        thesis_sys_prompt = read_file(thesis_prompt_path)
        anti_thesis_sys_prompt = read_file(anti_thesis_prompt_path)

        initial_state: ThesisState = {
            "code": code,
            "thesis_system_prompt": thesis_sys_prompt,
            "thesis_arguments": [],
            "anti_thesis_system_prompt": anti_thesis_sys_prompt,
            "anti_thesis_arguments": [],
            "limit": limit,
            "limit_counter": 0
        }

        self.thesis_agent.invoke(initial_state)


        return self.full_conversation
    


if __name__ == "__main__":
    agent = ThesisAgent()

    code_path = "./llm-council/prompts/code.md"
    thesis_prompt_path = "./llm-council/prompts/thesis.md"
    anti_thesis_prompt_path = "./llm-council/prompts/anti-thesis.md"

    try:
        conversation_history = agent.run_thesis_agent(
            code_path=code_path,
            thesis_prompt_path=thesis_prompt_path,
            anti_thesis_prompt_path=anti_thesis_prompt_path,
            limit=5
        )
        
        print("\n--- DEBATE FINISHED ---")
        
    except FileNotFoundError as e:
        print(f"Demo Error: Please make sure your .md prompt files exist. Details: {e}")


