from __future__ import annotations
from uuid import uuid4
import json
from collections import deque

class Node:

	def __init__(self, code="", thesis="", depth=0):
		self.id = uuid4()
		self.code : str = code
		self.thesis : str = thesis
		self.left : Node = None
		self.mid : Node = None
		self.right :Node = None
		self.depth: int = depth

def get_leaf_nodes(root):
    if root is None:
        return []
    
    # Check if the node is a leaf (all children are None)
    if root.left is None and root.mid is None and root.right is None:
        return [root]
    
    leaves = []
    
    # Recursively traverse each branch
    if root.left:
        leaves.extend(get_leaf_nodes(root.left))
    if root.mid:
        leaves.extend(get_leaf_nodes(root.mid))
    if root.right:
        leaves.extend(get_leaf_nodes(root.right))
        
    return leaves



def export_tree_to_json(root, filepath="tree_output.json"):
    if not root:
        return

    tree_export = {}
    node_registry = {}
    id_counter = 0

    def assign_id(node):
        nonlocal id_counter
        if node not in node_registry:
            node_registry[node] = f"node_{id_counter}"
            id_counter += 1
        return node_registry[node]

    queue = deque([root])

    while queue:
        current = queue.popleft()
        current_id = assign_id(current)

        left_node = getattr(current, "left", None)
        mid_node = getattr(current, "mid", None)
        right_node = getattr(current, "right", None)

        tree_export[current_id] = {
            "id": current_id,
            "code": getattr(current, "code", ""),
            "thesis": getattr(current, "thesis", ""),
            "left_id": assign_id(left_node) if left_node else None,
            "mid_id": assign_id(mid_node) if mid_node else None,
            "right_id": assign_id(right_node) if right_node else None
        }

        if left_node:
            queue.append(left_node)
        if mid_node:
            queue.append(mid_node)
        if right_node:
            queue.append(right_node)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(tree_export, file, indent=4, ensure_ascii=False)


def import_tree_from_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not data:
        return None

    # Step 1: Create all node instances and store them in a registry
    node_registry = {}
    for node_id, content in data.items():
        new_node = Node(
            code=content.get("code", ""),
            thesis=content.get("thesis", "")
        )
        new_node.id = node_id
        node_registry[node_id] = new_node

    # Step 2: Link nodes based on the ID references
    root = None
    for node_id, content in data.items():
        current_node = node_registry[node_id]
        
        # Identify the root (usually node_0, but let's be safe)
        if node_id == "node_0":
            root = current_node

        # Assign children using the registry
        if content.get("left_id"):
            current_node.left = node_registry[content["left_id"]]
        if content.get("mid_id"):
            current_node.mid = node_registry[content["mid_id"]]
        if content.get("right_id"):
            current_node.right = node_registry[content["right_id"]]

    return root


if __name__ == "__main__":
    root = import_tree_from_json("/home/furkan/projects/langchain-tutorial/llm-council/out/debug-tree.json")
    leaves = get_leaf_nodes(root)
    print(leaves)



    