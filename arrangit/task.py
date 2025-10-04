import json
import uuid
from datetime import datetime
from typing import List, Optional


class Task:
    def __init__(self, title: str, description: str = "", parent_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.parent_id = parent_id
        self.subtasks: List[str] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.completed = False

    def add_subtask(self, subtask_id: str):
        self.subtasks.append(subtask_id)
        self.updated_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "parent_id": self.parent_id,
            "subtasks": self.subtasks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data: dict):
        task = cls(data["title"], data.get("description", ""), data.get("parent_id"))
        task.id = data["id"]
        task.subtasks = data.get("subtasks", [])
        task.created_at = data["created_at"]
        task.updated_at = data["updated_at"]
        task.completed = data.get("completed", False)
        return task