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
