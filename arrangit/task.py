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
        self.clean = False
        self.completed_at: Optional[str] = None
        self.cleaned_at: Optional[str] = None

    def add_subtask(self, subtask_id: str):
        if self.clean:
            raise ValueError("Cannot add subtasks to clean tasks")
        self.subtasks.append(subtask_id)
        self.updated_at = datetime.now().isoformat()

    def mark_completed(self):
        self.completed = True
        self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def mark_uncompleted(self):
        self.completed = False
        self.completed_at = None
        self.updated_at = datetime.now().isoformat()

    def mark_clean(self):
        self.clean = True
        self.cleaned_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def mark_unclean(self):
        self.clean = False
        self.cleaned_at = None
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
            "completed": self.completed,
            "clean": self.clean,
            "completed_at": self.completed_at,
            "cleaned_at": self.cleaned_at
        }

    @staticmethod
    def _get_min_linux_date() -> str:
        """Returns the minimum possible date in Linux (Unix epoch)"""
        return datetime(1970, 1, 1, 0, 0, 0).isoformat()

    @classmethod
    def from_dict(cls, data: dict):
        task = cls(data["title"], data.get("description", ""), data.get("parent_id"))
        task.id = data["id"]
        task.subtasks = data.get("subtasks", [])
        
        # Handle missing timestamps with minimum Linux date
        min_date = cls._get_min_linux_date()
        task.created_at = data.get("created_at", min_date)
        task.updated_at = data.get("updated_at", min_date)
        
        task.completed = data.get("completed", False)
        task.clean = data.get("clean", False)
        task.completed_at = data.get("completed_at")
        task.cleaned_at = data.get("cleaned_at")
        return task