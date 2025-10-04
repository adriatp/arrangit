import json
import os
from typing import Dict, List, Optional
from .task import Task


class ProjectManager:
    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        self.config_file = os.path.join(project_path, ".arrangit.json")
        self.tasks: Dict[str, Task] = {}
        self.active_task: Optional[str] = None
        
        # Don't load project automatically - let CLI handle initialization

    def initialize_project(self):
        """Initialize a new project with empty configuration"""
        if os.path.exists(self.config_file):
            raise FileExistsError(f"File {self.config_file} already exists")
        
        data = {
            "project_name": "arrangit",
            "tasks": {},
            "active_task": None,
            "created_at": __import__("datetime").datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Load the newly created project
        self.load_project()

    def load_project(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"{self.config_file} not found. Run from a valid project.")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.tasks = {}
        for task_id, task_data in data.get("tasks", {}).items():
            self.tasks[task_id] = Task.from_dict(task_data)
        
        self.active_task = data.get("active_task")

    def save_project(self):
        data = {
            "project_name": "arrangit",
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "active_task": self.active_task,
            "updated_at": __import__("datetime").datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_task(self, title: str, description: str = "", parent_id: Optional[str] = None) -> str:
        task = Task(title, description, parent_id)
        self.tasks[task.id] = task
        
        if parent_id and parent_id in self.tasks:
            self.tasks[parent_id].add_subtask(task.id)
        
        self.save_project()
        return task.id

    def set_active_task(self, task_id: str):
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        self.active_task = task_id
        self.save_project()

    def get_active_task(self) -> Optional[Task]:
        if self.active_task:
            return self.tasks.get(self.active_task)
        return None

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def find_task_by_name(self, name: str) -> Optional[Task]:
        for task in self.tasks.values():
            if task.title.lower() == name.lower():
                return task
        return None

    def find_tasks_by_partial_name(self, partial_name: str) -> List[Task]:
        matches = []
        for task in self.tasks.values():
            if partial_name.lower() in task.title.lower():
                matches.append(task)
        return matches

    def get_incomplete_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() if not task.completed]

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def get_subtasks(self, parent_id: str) -> List[Task]:
        parent = self.tasks.get(parent_id)
        if not parent:
            return []
        
        return [self.tasks[subtask_id] for subtask_id in parent.subtasks if subtask_id in self.tasks]

    def get_tasks_hierarchically(self) -> List[tuple[Task, int]]:
        """Get all tasks in hierarchical order (parent tasks first, then subtasks)"""
        root_tasks = [task for task in self.tasks.values() if not task.parent_id]
        all_tasks = []
        
        def add_task_and_subtasks(task: Task, level: int = 0):
            all_tasks.append((task, level))
            for subtask_id in task.subtasks:
                if subtask_id in self.tasks:
                    add_task_and_subtasks(self.tasks[subtask_id], level + 1)
        
        for root_task in root_tasks:
            add_task_and_subtasks(root_task)
        
        return all_tasks

    def complete_task(self, task_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].completed = True
            
            # Mark all subtasks as completed recursively
            for subtask_id in self.tasks[task_id].subtasks:
                if subtask_id in self.tasks:
                    self.complete_task(subtask_id)
            
            self.save_project()

    def delete_task(self, task_id: str):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            
            for subtask_id in task.subtasks:
                self.delete_task(subtask_id)
            
            if task.parent_id and task.parent_id in self.tasks:
                parent = self.tasks[task.parent_id]
                if task_id in parent.subtasks:
                    parent.subtasks.remove(task_id)
            
            if self.active_task == task_id:
                self.active_task = None
            
            del self.tasks[task_id]
            self.save_project()