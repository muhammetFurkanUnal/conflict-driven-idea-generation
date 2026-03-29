from refine import RefineAgent
from thesis import ThesisAgent
from tree import Node, export_tree_to_json
from config import settings
from utils import read_file
from collections import deque
import argparse

# initialize the agents
first_code_path = "/home/furkan/projects/langchain-tutorial/llm-council/prompts/code.md"
debug_first_code_path = "/home/furkan/projects/langchain-tutorial/llm-council/prompts/debug-code.md"
refine_prompt_path = "/home/furkan/projects/langchain-tutorial/llm-council/prompts/refine.md"
thesis_prompt_path = "/home/furkan/projects/langchain-tutorial/llm-council/prompts/thesis.md"
anti_thesis_prompt_path = "/home/furkan/projects/langchain-tutorial/llm-council/prompts/anti-thesis.md"

refine_agent = RefineAgent(debug=settings.debug)
thesis_agent = ThesisAgent(debug=settings.debug)

# methods
def process_node(node: Node):
    """Processes a single node: runs debate and generates 3 children."""
    if node is None:
        return
    
    code_path = debug_first_code_path if settings.debug else first_code_path
    code = read_file(code_path)

    # Run the debate to get arguments
    node.thesis = thesis_agent.run_thesis_agent(
        code=code,
        thesis_prompt_path=thesis_prompt_path,
        anti_thesis_prompt_path=anti_thesis_prompt_path,
        limit=settings.thesis.limit
    )

    # Generate 3 refined versions of the code based on the debate results
    # RefineAgent.run metodu kodu ve tartışma sonucunu girdi olarak alır
    node.left = Node(
        code=refine_agent.run(
            node.code, 
            node.thesis, 
            prompt_file=refine_prompt_path
        ), depth=node.depth+1)
    
    node.mid = Node(
        code=refine_agent.run(
            node.code, 
            node.thesis, 
            prompt_file=refine_prompt_path
        ), depth=node.depth+1)
    
    node.right = Node(
        code=refine_agent.run(
            node.code, 
            node.thesis, 
            prompt_file=refine_prompt_path
        ), depth=node.depth+1)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conflict Driven Multi Agentic Idea Generation")

    parser.add_argument("--idea", action="store_true", help="run in idea generation mode.")
    parser.add_argument("--code", action="store_true", help="run in code optimisation mode.")

    args = parser.parse_args()

    if args.code:
        settings.mode = "code"
    elif args.idea:
        settings.mode = "idea"

    # --- BFS Tree Construction ---
    code_path = debug_first_code_path if settings.debug else first_code_path
    root = Node(code=read_file(code_path))

    # 2. Kuyruk (Queue) başlatılır ve root eklenir
    queue = deque([root])

    print("Starting Tree Expansion (BFS)...")

    while queue:
        current_node = queue.popleft()
        current_depth = current_node.depth
        
        # Derinlik kontrolü: Eğer hedeflenen derinliğe ulaştıysak çocuk üretme
        if current_depth < settings.tree.depth:
            process_node(current_node)
            
            # Yeni oluşan çocukları kuyruğa ekle (bir sonraki derinlik için)
            if current_node.left:
                queue.append(current_node.left)
            if current_node.mid:
                queue.append(current_node.mid)
            if current_node.right:
                queue.append(current_node.right)

    print("Tree construction completed.")
    print("Total requests: ", settings.requests)

    export_tree_to_json(root, settings.tree.json_file)
    
