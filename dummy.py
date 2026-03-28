from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

import os
from config import settings
from typing import TypedDict, List
from utils import read_file

os.environ["GOOGLE_API_KEY"] = settings.API_KEY.gemini25flash
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")


class State(TypedDict):
	user_prompt_history: List[str]
	llm_response_history: List[str]
	limit_counter: int
	limit: int


# define nodes
def question(state: State):
	prompt = input("> ")
	state["user_prompt_history"].append(prompt)
	return state
	

def answer(state:State):
	system_prompt = read_file("./llm-council/prompts/dummy.md")
	prompt = [SystemMessage(system_prompt)]
	for i in range(len(state["llm_response_history"])):
		prompt.append(HumanMessage(state["user_prompt_history"][i]))
		prompt.append(AIMessage(state["llm_response_history"][i]))

	prompt.append(HumanMessage(state["user_prompt_history"][-1]))
	response = model.invoke(prompt)
	print(response.content)
	state["llm_response_history"].append(response.content)
	state["limit_counter"]+=1

	return state


# condition method
def limit_check(state: State) -> State:
	limit_counter = state["limit_counter"]
	limit = state["limit"]

	if limit_counter >= limit:
		print("Günlük kullanım limitine erişildi")
		return END
	else:
		return "question"


# build workflow
agent_builder = StateGraph(State)

agent_builder.add_node("question", question)
agent_builder.add_node("answer", answer)

agent_builder.add_edge(START, "question")
agent_builder.add_edge("question", "answer")
agent_builder.add_conditional_edges(
	"answer",
	limit_check,
	["question", END]
)

agent = agent_builder.compile()
agent.invoke({
	"user_prompt_history":[],
	"llm_response_history":[],
	"limit_counter":0,
	"limit":5
})

