import argparse
import sys
from .project_manager import ProjectManager


def main():
    manager = ProjectManager()

    parser = argparse.ArgumentParser(description="Project task manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("init", help="Initialize a new project")
    subparsers.add_parser("list", help="List all tasks")

    task_parser = subparsers.add_parser("task", help="Create or select task")
    task_parser.add_argument("name", help="Task name")
    task_parser.add_argument("-d", "--description", help="Task description", default="")

    subtask_parser = subparsers.add_parser("subtask", help="Create or select subtask")
    subtask_parser.add_argument("name", help="Subtask name")

    subparsers.add_parser("active", help="Show active task")

    done_parser = subparsers.add_parser("done", help="Mark task as completed")
    done_parser.add_argument("name", nargs="?", help="Task name (optional)")

    delete_parser = subparsers.add_parser("delete", help="Delete task")
    delete_parser.add_argument("name", nargs="?", help="Task name (optional)")

    move_parser = subparsers.add_parser("move", help="Move task to different parent")
    move_parser.add_argument("name", nargs="?", help="Task name to move (optional)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "init":
            manager.initialize_project()
            print(f"Project initialized in {manager.config_file}")
            return

        # For other commands, load existing project
        manager.load_project()

        if args.command == "list":
            hierarchical_tasks = manager.get_tasks_hierarchically()
            if not hierarchical_tasks:
                print("No tasks in the project")
                return

            for task, level in hierarchical_tasks:
                status = "✓" if task.completed else "◯"
                active = "*" if task.id == manager.active_task else " "
                indent = "  " * level
                print(f"{active} {status} {indent}{task.title} [{task.id[:8]}]")
                if task.description:
                    print(f"     {indent}{task.description}")

        elif args.command == "task":
            existing_task = manager.find_task_by_name(args.name)

            if existing_task:
                manager.set_active_task(existing_task.id)
                print(f"Active task: {existing_task.title}")
            else:
                task_id = manager.create_task(args.name, args.description)
                manager.set_active_task(task_id)
                print(f"Task created and active: {args.name}")

        elif args.command == "subtask":
            existing_task = manager.find_task_by_name(args.name)

            if existing_task:
                manager.set_active_task(existing_task.id)
                print(f"Active subtask: {existing_task.title}")
            else:
                hierarchical_tasks = manager.get_tasks_hierarchically()

                if not hierarchical_tasks:
                    print("No tasks available to create subtasks")
                    return

                print("\nAvailable tasks for subtask:")
                print("-" * 50)
                for i, (task, level) in enumerate(hierarchical_tasks, 1):
                    status = "✓" if task.completed else "◯"
                    active = "*" if task.id == manager.active_task else " "
                    indent = "  " * level
                    print(
                        f"{i}. {active} {status} {indent}{task.title} [{task.id[:8]}]"
                    )

                try:
                    choice = input("\nSelect the parent task number: ")
                    parent_index = int(choice) - 1

                    if 0 <= parent_index < len(hierarchical_tasks):
                        parent_task, _ = hierarchical_tasks[parent_index]
                        task_id = manager.create_task(args.name, "", parent_task.id)
                        manager.set_active_task(task_id)
                        print(
                            f"Subtask created and active: {args.name} (of {parent_task.title})"
                        )
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == "active":
            active_task = manager.get_active_task()
            if active_task:
                print(f"Active task: {active_task.title}")
                if active_task.description:
                    print(f"Description: {active_task.description}")
            else:
                print("No active task")

        elif args.command == "done":
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.complete_task(task.id)
                    print(f"Task completed: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                tasks = manager.get_all_tasks()
                if not tasks:
                    print("No tasks in the project")
                    return

                print("\nAvailable tasks to mark as completed:")
                print("-" * 50)

                for i, task in enumerate(tasks, 1):
                    status = "✓" if task.completed else "◯"
                    active = "*" if task.id == manager.active_task else " "
                    indent = "  " if task.parent_id else ""
                    print(
                        f"{i}. {active} {status} {indent}{task.title} [{task.id[:8]}]"
                    )

                try:
                    choice = input("\nSelect the task number to complete: ")
                    task_index = int(choice) - 1

                    if 0 <= task_index < len(tasks):
                        task = tasks[task_index]
                        manager.complete_task(task.id)
                        print(f"Task completed: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == "delete":
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.delete_task(task.id)
                    print(f"Task deleted: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                tasks = manager.get_all_tasks()
                if not tasks:
                    print("No tasks in the project")
                    return

                print("\nAvailable tasks to delete:")
                print("-" * 50)

                for i, task in enumerate(tasks, 1):
                    status = "✓" if task.completed else "◯"
                    active = "*" if task.id == manager.active_task else " "
                    indent = "  " if task.parent_id else ""
                    print(
                        f"{i}. {active} {status} {indent}{task.title} [{task.id[:8]}]"
                    )

                try:
                    choice = input("\nSelect the task number to delete: ")
                    task_index = int(choice) - 1

                    if 0 <= task_index < len(tasks):
                        task = tasks[task_index]
                        manager.delete_task(task.id)
                        print(f"Task deleted: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == "move":
            if args.name:
                task = manager.find_task_by_name(args.name)
                if not task:
                    print(f"Task '{args.name}' not found")
                    return
            else:
                tasks = manager.get_all_tasks()
                if not tasks:
                    print("No tasks in the project")
                    return

                print("\nAvailable tasks to move:")
                print("-" * 50)

                for i, task in enumerate(tasks, 1):
                    status = "✓" if task.completed else "◯"
                    active = "*" if task.id == manager.active_task else " "
                    indent = "  " if task.parent_id else ""
                    print(
                        f"{i}. {active} {status} {indent}{task.title} [{task.id[:8]}]"
                    )

                try:
                    choice = input("\nSelect the task number to move: ")
                    task_index = int(choice) - 1

                    if 0 <= task_index < len(tasks):
                        task = tasks[task_index]
                    else:
                        print("Invalid selection")
                        return
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")
                    return

            # Select new parent
            hierarchical_tasks = manager.get_tasks_hierarchically()

            print(f"\nMoving task: {task.title}")
            print("\nSelect new parent (0 for root level):")
            print("-" * 50)
            print("0. Root level (no parent)")

            available_parents = []
            parent_counter = 1
            for parent_task, level in hierarchical_tasks:
                # Skip the task being moved and its descendants
                if parent_task.id == task.id:
                    continue

                # Check if parent_task is a descendant of task
                def is_descendant(parent_id: str, child_id: str) -> bool:
                    parent = manager.get_task(parent_id)
                    if not parent:
                        return False
                    for subtask_id in parent.subtasks:
                        if subtask_id == child_id:
                            return True
                        if is_descendant(subtask_id, child_id):
                            return True
                    return False

                if is_descendant(task.id, parent_task.id):
                    continue

                status = "✓" if parent_task.completed else "◯"
                active = "*" if parent_task.id == manager.active_task else " "
                indent = "  " * level
                print(
                    f"{parent_counter}. {active} {status} {indent}{parent_task.title} [{parent_task.id[:8]}]"
                )
                available_parents.append(parent_task)
                parent_counter += 1

            try:
                choice = input("\nSelect the new parent number: ")
                parent_index = int(choice)

                if parent_index == 0:
                    # Move to root level
                    manager.move_task(task.id, None)
                    print(f"Task moved to root level: {task.title}")
                elif 1 <= parent_index <= len(available_parents):
                    parent_task = available_parents[parent_index - 1]
                    manager.move_task(task.id, parent_task.id)
                    print(f"Task moved to: {parent_task.title}")
                else:
                    print("Invalid selection")
            except (ValueError, KeyboardInterrupt):
                print("\nOperation cancelled")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

