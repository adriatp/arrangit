import json
import os
from typing import Dict, List, Optional
from .task import Task


class ProjectManager:
    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        self.config_file = os.path.join(project_path, ".arrangit.json")
        self.tasks: Dict[str, Task] = {}
        self.active_tasks: List[str] = []
        
        # Don't load project automatically - let CLI handle initialization

    def initialize_project(self):
        """Initialize a new project with empty configuration"""
        if os.path.exists(self.config_file):
            raise FileExistsError(f"File {self.config_file} already exists")
        
        data = {
            "project_name": "arrangit",
            "tasks": {},
            "active_tasks": [],
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
        
        # Handle migration from single active_task to active_tasks list
        old_active_task = data.get("active_task")
        if old_active_task:
            self.active_tasks = [old_active_task]
        else:
            self.active_tasks = data.get("active_tasks", [])

    def save_project(self):
        data = {
            "project_name": "arrangit",
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "active_tasks": self.active_tasks,
            "updated_at": __import__("datetime").datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_task(self, title: str, description: str = "", parent_id: Optional[str] = None) -> str:
        task = Task(title, description, parent_id)
        self.tasks[task.id] = task
        
        if parent_id and parent_id in self.tasks:
            parent_task = self.tasks[parent_id]
            if parent_task.clean:
                raise ValueError("Cannot add subtasks to clean tasks")
            parent_task.add_subtask(task.id)
        
        self.save_project()
        return task.id

    def add_active_task(self, task_id: str):
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        task = self.tasks[task_id]
        if task.clean:
            raise ValueError("Cannot activate clean tasks")
        
        if task_id not in self.active_tasks:
            self.active_tasks.append(task_id)
            self.save_project()

    def remove_active_task(self, task_id: str):
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)
            self.save_project()

    def get_active_tasks(self) -> List[Task]:
        return [self.tasks[task_id] for task_id in self.active_tasks if task_id in self.tasks]

    def get_inactive_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() if task.id not in self.active_tasks and not task.completed and not task.clean]

    def get_active_tasks_hierarchically(self) -> List[tuple[Task, int]]:
        """Get active tasks with their hierarchical structure including parent tasks"""
        # Get all tasks that are active or are parents of active tasks
        relevant_tasks = set()
        
        def add_task_and_parents(task_id: str):
            """Add task and all its parents to relevant_tasks"""
            task = self.get_task(task_id)
            if task and task.id not in relevant_tasks and not task.clean:
                relevant_tasks.add(task.id)
                if task.parent_id:
                    add_task_and_parents(task.parent_id)
        
        # Add all active tasks and their parents
        for task_id in self.active_tasks:
            add_task_and_parents(task_id)
        
        # Build hierarchical structure
        all_tasks = []
        
        def add_task_and_subtasks(task: Task, level: int = 0):
            """Add task and its subtasks to the list if they are relevant"""
            if task.id in relevant_tasks:
                all_tasks.append((task, level))
                
                # Add subtasks that are relevant
                for subtask_id in task.subtasks:
                    if subtask_id in self.tasks and self.tasks[subtask_id].id in relevant_tasks:
                        add_task_and_subtasks(self.tasks[subtask_id], level + 1)
        
        # Start from root tasks
        root_tasks = [task for task in self.tasks.values() if not task.parent_id]
        
        for root_task in root_tasks:
            add_task_and_subtasks(root_task)
        
        return all_tasks

    def get_takeable_tasks_hierarchically(self) -> List[tuple[Task, int, bool]]:
        """Get tasks that can be activated with hierarchical structure
        Returns list of (task, level, can_take)"""
        # Get only incomplete and inactive tasks
        hierarchical_tasks = self.get_tasks_hierarchically(show_all=False)
        result = []
        
        for task, level in hierarchical_tasks:
            # Task can be taken if it's not completed, not clean, and not already active
            can_take = not task.completed and not task.clean and task.id not in self.active_tasks
            result.append((task, level, can_take))
        
        return result

    def get_untakeable_tasks_hierarchically(self) -> List[tuple[Task, int, bool]]:
        """Get tasks that can be deactivated with hierarchical structure
        Returns list of (task, level, can_untake)"""
        # Get only active tasks and their parents up to root
        hierarchical_tasks = self.get_active_tasks_hierarchically()
        result = []
        
        for task, level in hierarchical_tasks:
            # Task can be untaken if it's currently active and not clean
            can_untake = task.id in self.active_tasks and not task.clean
            result.append((task, level, can_untake))
        
        return result

    def get_completed_tasks_hierarchically(self) -> List[tuple[Task, int]]:
        """Get only completed tasks with hierarchical structure"""
        hierarchical_tasks = self.get_tasks_hierarchically(show_all=True)
        result = []
        
        for task, level in hierarchical_tasks:
            if task.completed and not task.clean:
                result.append((task, level))
        
        return result

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
        return [task for task in self.tasks.values() if not task.completed and not task.clean]

    def get_completed_tasks(self) -> List[Task]:
        return [task for task in self.tasks.values() if task.completed and not task.clean]

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def get_subtasks(self, parent_id: str) -> List[Task]:
        parent = self.tasks.get(parent_id)
        if not parent:
            return []
        
        return [self.tasks[subtask_id] for subtask_id in parent.subtasks if subtask_id in self.tasks]

    def _get_min_linux_date(self) -> str:
        """Returns the minimum possible date in Linux (Unix epoch)"""
        return __import__("datetime").datetime(1970, 1, 1, 0, 0, 0).isoformat()

    def _get_task_priority(self, task: Task) -> tuple:
        """Get priority tuple for sorting: (priority_category, date_priority)"""
        # Priority categories: 0=taken, 1=undone, 2=done, 3=clean
        if task.id in self.active_tasks:
            priority_category = 0
        elif task.clean:
            priority_category = 3
        elif task.completed:
            priority_category = 2
        else:
            priority_category = 1
        
        # Date priority: clean_date > completed_date > created_date
        date_priority = (
            task.cleaned_at or 
            task.completed_at or 
            task.created_at or 
            self._get_min_linux_date()
        )
        
        return (priority_category, date_priority)

    def get_tasks_hierarchically(self, show_completed: bool = False, show_all: bool = False, show_clean: bool = False) -> List[tuple[Task, int]]:
        """Get tasks in hierarchical order (parent tasks first, then subtasks)
        
        Args:
            show_completed: If True, show structure with completed tasks highlighted
            show_all: If True, show all tasks regardless of completion status
            show_clean: If True, show clean tasks (default: False)
        """
        # Always start with all root tasks to maintain structure
        root_tasks = [task for task in self.tasks.values() if not task.parent_id]
        
        all_tasks = []
        
        def add_task_and_subtasks(task: Task, level: int = 0):
            # Skip clean tasks unless explicitly requested
            if not show_clean and task.clean:
                return
                
            # For show_completed mode, only add tasks that are completed or have completed descendants
            if show_completed:
                # Check if this task or any of its descendants are completed
                def has_completed_descendants(t: Task) -> bool:
                    if t.completed:
                        return True
                    for subtask_id in t.subtasks:
                        if subtask_id in self.tasks:
                            if has_completed_descendants(self.tasks[subtask_id]):
                                return True
                    return False
                
                if not has_completed_descendants(task):
                    return
            elif not show_all and task.completed:
                # For default mode, skip completed tasks
                return
            
            all_tasks.append((task, level))
            
            # Always add all subtasks to maintain structure
            for subtask_id in task.subtasks:
                if subtask_id in self.tasks:
                    add_task_and_subtasks(self.tasks[subtask_id], level + 1)
        
        for root_task in root_tasks:
            add_task_and_subtasks(root_task)
        
        # Sort tasks by priority
        all_tasks.sort(key=lambda x: self._get_task_priority(x[0]))
        
        return all_tasks

    def complete_task(self, task_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].mark_completed()
            
            # Remove from active tasks
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            
            # Mark all subtasks as completed recursively
            for subtask_id in self.tasks[task_id].subtasks:
                if subtask_id in self.tasks:
                    self.complete_task(subtask_id)
            
            self.save_project()

    def uncomplete_task(self, task_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].mark_uncompleted()
            
            # Mark all subtasks as uncompleted recursively
            for subtask_id in self.tasks[task_id].subtasks:
                if subtask_id in self.tasks:
                    self.uncomplete_task(subtask_id)
            
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
            
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            
            del self.tasks[task_id]
            self.save_project()

    def clean_task(self, task_id: str):
        """Mark a task and all its subtasks as clean"""
        if task_id in self.tasks:
            self.tasks[task_id].mark_clean()
            
            # Remove from active tasks
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)
            
            # Mark all subtasks as clean recursively
            for subtask_id in self.tasks[task_id].subtasks:
                if subtask_id in self.tasks:
                    self.clean_task(subtask_id)
            
            self.save_project()

    def unclean_task(self, task_id: str):
        """Mark a task and all its subtasks as unclean"""
        if task_id in self.tasks:
            self.tasks[task_id].mark_unclean()
            
            # Mark all subtasks as unclean recursively
            for subtask_id in self.tasks[task_id].subtasks:
                if subtask_id in self.tasks:
                    self.unclean_task(subtask_id)
            
            self.save_project()

    def move_task(self, task_id: str, new_parent_id: Optional[str] = None):
        """Move a task to a new parent (None for root level)"""
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        task = self.tasks[task_id]
        
        # Check if moving to itself or creating a circular dependency
        if new_parent_id == task_id:
            raise ValueError("Cannot move task to itself")
        
        if new_parent_id:
            if new_parent_id not in self.tasks:
                raise ValueError(f"Parent task with ID {new_parent_id} not found")
            
            # Check for circular dependency
            def is_descendant(parent_id: str, child_id: str) -> bool:
                parent = self.tasks.get(parent_id)
                if not parent:
                    return False
                for subtask_id in parent.subtasks:
                    if subtask_id == child_id:
                        return True
                    if is_descendant(subtask_id, child_id):
                        return True
                return False
            
            if is_descendant(task_id, new_parent_id):
                raise ValueError("Cannot move task to its own descendant")
            
            # Check if parent is clean
            parent_task = self.tasks[new_parent_id]
            if parent_task.clean:
                raise ValueError("Cannot move task to clean parent")
        
        # Remove from current parent
        if task.parent_id and task.parent_id in self.tasks:
            current_parent = self.tasks[task.parent_id]
            if task_id in current_parent.subtasks:
                current_parent.subtasks.remove(task_id)
        
        # Add to new parent
        if new_parent_id:
            new_parent = self.tasks[new_parent_id]
            new_parent.add_subtask(task_id)
            task.parent_id = new_parent_id
        else:
            task.parent_id = None
        
        task.updated_at = __import__("datetime").datetime.now().isoformat()
        self.save_project()