import argparse
import sys
from .project_manager import ProjectManager


def main():
    manager = ProjectManager()

    parser = argparse.ArgumentParser(description="Project task manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    subparsers.add_parser('init', help='Initialize a new project')
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--done', action='store_true', help='Show only completed tasks')
    list_parser.add_argument('--undone', action='store_true', help='Show only incomplete tasks')
    list_parser.add_argument('--active', action='store_true', help='Show only active tasks')
    list_parser.add_argument('--clean', action='store_true', help='Show only clean tasks')
    list_parser.add_argument('--unclean', action='store_true', help='Show only non-clean tasks')
    list_parser.add_argument('--all', action='store_true', help='Show all tasks including clean')
    list_parser.add_argument('--full', action='store_true', help='Show detailed tabular output')
    
    task_parser = subparsers.add_parser('task', help='Create or select task')
    task_parser.add_argument('name', help='Task name')
    task_parser.add_argument('-d', '--description', help='Task description', default='')

    subparsers.add_parser('active', help='Show active task')

    done_parser = subparsers.add_parser('done', help='Mark task as completed')
    done_parser.add_argument('name', nargs='?', help='Task name (optional)')

    delete_parser = subparsers.add_parser('delete', help='Delete task')
    delete_parser.add_argument('name', nargs='?', help='Task name (optional)')

    move_parser = subparsers.add_parser('move', help='Move task to different parent')
    move_parser.add_argument('name', nargs='?', help='Task name to move (optional)')

    undone_parser = subparsers.add_parser('undone', help='Mark task as not completed')
    undone_parser.add_argument('name', nargs='?', help='Task name (optional)')

    clean_parser = subparsers.add_parser('clean', help='Mark task as clean')
    clean_parser.add_argument('name', nargs='?', help='Task name (optional)')

    unclean_parser = subparsers.add_parser('unclean', help='Mark task as not clean')
    unclean_parser.add_argument('name', nargs='?', help='Task name (optional)')

    take_parser = subparsers.add_parser('take', help='Activate a task')
    take_parser.add_argument('name', nargs='?', help='Task name to activate (optional)')

    untake_parser = subparsers.add_parser('untake', help='Deactivate a task')
    untake_parser.add_argument('name', nargs='?', help='Task name to deactivate (optional)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'init':
            manager.initialize_project()
            print(f"Project initialized in {manager.config_file}")
            return
        
        # For other commands, load existing project
        manager.load_project()
        
        if args.command == 'list':
            # Determine which tasks to show based on flags
            if args.done:
                hierarchical_tasks = manager.get_completed_tasks_hierarchically()
                title = "Completed tasks"
            elif args.undone:
                hierarchical_tasks = manager.get_tasks_hierarchically()
                title = "Incomplete tasks"
            elif args.active:
                hierarchical_tasks = manager.get_active_tasks_hierarchically()
                title = "Active tasks"
            elif args.clean:
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True, show_clean=True)
                # Filter to only show clean tasks
                hierarchical_tasks = [(task, level) for task, level in hierarchical_tasks if task.clean]
                title = "Clean tasks"
            elif args.unclean:
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True)
                # Filter to only show non-clean tasks
                hierarchical_tasks = [(task, level) for task, level in hierarchical_tasks if not task.clean]
                title = "Non-clean tasks"
            elif args.all:
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True, show_clean=True)
                title = "All tasks"
            else:
                # Default: show all non-clean tasks (same as --unclean)
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True)
                # Filter to only show non-clean tasks
                hierarchical_tasks = [(task, level) for task, level in hierarchical_tasks if not task.clean]
                title = "Tasks"
            
            if not hierarchical_tasks:
                if args.done:
                    print("No completed tasks in the project")
                elif args.undone:
                    print("No incomplete tasks in the project")
                elif args.active:
                    print("No active tasks in the project")
                elif args.clean:
                    print("No clean tasks in the project")
                elif args.unclean:
                    print("No non-clean tasks in the project")
                else:
                    print("No tasks in the project")
                return

            if args.full:
                # Tabular format with columns
                print(f"\n{title}:")
                print("-" * 120)
                
                # Print header
                print(f"{'':<2} {'':<1} {'Description':<70} {'Created':<12} {'Completed':<12} {'Cleaned':<12}")
                print("-" * 120)
                
                for task, level in hierarchical_tasks:
                    if task.id in manager.active_tasks:
                        status = "*"
                    elif task.clean:
                        status = "C"
                    else:
                        status = "✓" if task.completed else "◯"
                    
                    # Format dates
                    created_date = task.created_at[:10] if task.created_at else "-"
                    completed_date = task.completed_at[:10] if task.completed_at else "-"
                    cleaned_date = task.cleaned_at[:10] if task.cleaned_at else "-"
                    
                    # Create combined description with title and description
                    indent = "  " * level
                    combined_desc = f"{indent}{task.title}"
                    if task.description:
                        combined_desc += f": {task.description}"
                    
                    # Truncate if too long
                    if len(combined_desc) > 70:
                        combined_desc = combined_desc[:67] + "..."
                    
                    print(f"{'':<2} {status:<1} {combined_desc:<70} {created_date:<12} {completed_date:<12} {cleaned_date:<12}")
            else:
                # Default format
                print(f"\n{title}:")
                print("-" * 50)
                
                for task, level in hierarchical_tasks:
                    if task.id in manager.active_tasks:
                        status = "*"
                    elif task.clean:
                        status = "C"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    
                    # Show creation date instead of ID
                    created_date = task.created_at[:10] if task.created_at else "-"
                    print(f"  {status} {indent}{task.title} [{created_date}]")
                    if task.description:
                        print(f"     {indent}{task.description}")

        elif args.command == 'task':
            existing_task = manager.find_task_by_name(args.name)
            
            if existing_task:
                manager.add_active_task(existing_task.id)
                print(f"Task activated: {existing_task.title}")
            else:
                hierarchical_tasks = manager.get_tasks_hierarchically()
                
                print("\nSelect parent task (0 for root level):")
                print("-" * 50)
                print("0. Root level (no parent)")
                
                for i, (task, level) in enumerate(hierarchical_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    print(f"{i}.  {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelect the parent task number: ")
                    parent_index = int(choice)
                    
                    if parent_index == 0:
                        # Create root task
                        task_id = manager.create_task(args.name, args.description)
                        print(f"Task created: {args.name}")
                    elif 1 <= parent_index <= len(hierarchical_tasks):
                        parent_task, _ = hierarchical_tasks[parent_index - 1]
                        task_id = manager.create_task(args.name, args.description, parent_task.id)
                        print(f"Subtask created: {args.name} (of {parent_task.title})")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == 'active':
            hierarchical_tasks = manager.get_active_tasks_hierarchically()
            if not hierarchical_tasks:
                print("No active tasks")
                return
            
            print("\nActive tasks:")
            print("-" * 50)
            for task, level in hierarchical_tasks:
                if task.id in manager.active_tasks:
                    status = "*"
                else:
                    status = "✓" if task.completed else "◯"
                indent = "  " * level
                print(f"  {status} {indent}{task.title} [{task.id[:8]}]")
                if task.description:
                    print(f"     {indent}{task.description}")

        elif args.command == 'done':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.complete_task(task.id)
                    print(f"Task completed: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                hierarchical_tasks = manager.get_tasks_hierarchically()
                if not hierarchical_tasks:
                    print("No incomplete tasks in the project")
                    return

                print("\nAvailable tasks to mark as completed:")
                print("-" * 50)
                
                for i, (task, level) in enumerate(hierarchical_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    print(f"{i}.  {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelect the task number to complete: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(hierarchical_tasks):
                        task, _ = hierarchical_tasks[task_index]
                        manager.complete_task(task.id)
                        print(f"Task completed: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == 'delete':
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
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " if task.parent_id else ""
                    print(f"{i}.  {status} {indent}{task.title} [{task.id[:8]}]")
                
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

        elif args.command == 'move':
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
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " if task.parent_id else ""
                    print(f"{i}.  {status} {indent}{task.title} [{task.id[:8]}]")
                
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
                
                if parent_task.id in manager.active_tasks:
                    status = "*"
                else:
                    status = "✓" if parent_task.completed else "◯"
                indent = "  " * level
                print(f"{parent_counter}.  {status} {indent}{parent_task.title} [{parent_task.id[:8]}]")
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

        elif args.command == 'undone':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.uncomplete_task(task.id)
                    print(f"Task marked as not completed: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                hierarchical_tasks = manager.get_tasks_hierarchically(show_completed=True)
                if not hierarchical_tasks:
                    print("No completed tasks in the project")
                    return

                print("\nAvailable tasks to mark as not completed:")
                print("-" * 50)
                
                for i, (task, level) in enumerate(hierarchical_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    print(f"{i}.  {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelect the task number to mark as not completed: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(hierarchical_tasks):
                        task, _ = hierarchical_tasks[task_index]
                        manager.uncomplete_task(task.id)
                        print(f"Task marked as not completed: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == 'clean':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.clean_task(task.id)
                    print(f"Task marked as clean: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True)
                if not hierarchical_tasks:
                    print("No tasks in the project")
                    return

                print("\nAvailable tasks to mark as clean:")
                print("-" * 50)
                
                for i, (task, level) in enumerate(hierarchical_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    print(f"{i}.  {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelect the task number to mark as clean: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(hierarchical_tasks):
                        task, _ = hierarchical_tasks[task_index]
                        manager.clean_task(task.id)
                        print(f"Task marked as clean: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == 'unclean':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.unclean_task(task.id)
                    print(f"Task marked as not clean: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True, show_clean=True)
                if not hierarchical_tasks:
                    print("No clean tasks in the project")
                    return

                print("\nAvailable tasks to mark as not clean:")
                print("-" * 50)
                
                for i, (task, level) in enumerate(hierarchical_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    print(f"{i}.  {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelect the task number to mark as not clean: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(hierarchical_tasks):
                        task, _ = hierarchical_tasks[task_index]
                        manager.unclean_task(task.id)
                        print(f"Task marked as not clean: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == 'take':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    if task.completed:
                        print(f"Cannot activate completed task: {task.title}")
                    elif task.clean:
                        print(f"Cannot activate clean task: {task.title}")
                    else:
                        manager.add_active_task(task.id)
                        print(f"Task activated: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                takeable_tasks = manager.get_takeable_tasks_hierarchically()
                if not any(can_take for _, _, can_take in takeable_tasks):
                    print("No tasks available to activate")
                    return

                print("\nAvailable tasks to activate:")
                print("-" * 50)
                
                selectable_tasks = []
                counter = 1
                
                for task, level, can_take in takeable_tasks:
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    
                    if can_take:
                        print(f"{counter}.  {status} {indent}{task.title} [{task.id[:8]}]")
                        selectable_tasks.append(task)
                        counter += 1
                    else:
                        print(f"    {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelect the task number to activate: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(selectable_tasks):
                        task = selectable_tasks[task_index]
                        manager.add_active_task(task.id)
                        print(f"Task activated: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

        elif args.command == 'untake':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.remove_active_task(task.id)
                    print(f"Task deactivated: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                untakeable_tasks = manager.get_untakeable_tasks_hierarchically()
                if not any(can_untake for _, _, can_untake in untakeable_tasks):
                    print("No tasks available to deactivate")
                    return

                print("\nAvailable tasks to deactivate:")
                print("-" * 50)
                
                selectable_tasks = []
                counter = 1
                
                for task, level, can_untake in untakeable_tasks:
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    
                    if can_untake:
                        print(f"{counter}.  {status} {indent}{task.title} [{task.id[:8]}]")
                        selectable_tasks.append(task)
                        counter += 1
                    else:
                        print(f"    {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelect the task number to deactivate: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(selectable_tasks):
                        task = selectable_tasks[task_index]
                        manager.remove_active_task(task.id)
                        print(f"Task deactivated: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()