import argparse
import sys
from .project_manager import ProjectManager


def format_numbered_item(number: int, total_items: int, content: str) -> str:
    """Format a numbered item with proper alignment based on total items"""
    # Simple approach: add spaces at the beginning for alignment
    max_digits = len(str(total_items))
    current_digits = len(str(number))
    spaces = " " * (max_digits - current_digits)
    return f"{spaces}{number}. {content}"


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
    list_parser.add_argument('--simple', action='store_true', help='Show simplified output')
    
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

            if args.simple:
                # Simple format
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
            else:
                # Default: Tabular format with columns
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
                    content = f"{status} {indent}{task.title} [{task.id[:8]}]"
                    print(format_numbered_item(i, len(hierarchical_tasks), content))
                
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

        elif args.command == 'unclean':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.unclean_task(task.id)
                    print(f"Task marked as not clean: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                # Show only clean tasks to mark them as unclean
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True, show_clean=True)
                clean_tasks = [(task, level) for task, level in hierarchical_tasks if task.clean]
                
                if not clean_tasks:
                    print("No clean tasks in the project")
                    return

                print("\nAvailable tasks to mark as not clean:")
                print("-" * 50)
                
                for i, (task, level) in enumerate(clean_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    content = f"{status} {indent}{task.title} [{task.id[:8]}]"
                    print(format_numbered_item(i, len(clean_tasks), content))
                
                try:
                    choice = input("\nSelect the task number to mark as not clean: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(clean_tasks):
                        task, _ = clean_tasks[task_index]
                        manager.unclean_task(task.id)
                        print(f"Task marked as not clean: {task.title}")
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
                # Show only unclean tasks to mark them as clean
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True)
                unclean_tasks = [(task, level) for task, level in hierarchical_tasks if not task.clean]
                
                if not unclean_tasks:
                    print("No unclean tasks in the project")
                    return

                print("\nAvailable tasks to mark as clean:")
                print("-" * 50)
                
                for i, (task, level) in enumerate(unclean_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓" if task.completed else "◯"
                    indent = "  " * level
                    content = f"{status} {indent}{task.title} [{task.id[:8]}]"
                    print(format_numbered_item(i, len(unclean_tasks), content))
                
                try:
                    choice = input("\nSelect the task number to mark as clean: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(unclean_tasks):
                        task, _ = unclean_tasks[task_index]
                        manager.clean_task(task.id)
                        print(f"Task marked as clean: {task.title}")
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
                    if can_take:
                        status = "✓" if task.completed else "◯"
                        indent = "  " * level
                        content = f"{status} {indent}{task.title} [{task.id[:8]}]"
                        print(format_numbered_item(counter, len([t for t in takeable_tasks if t[2]]), content))
                        selectable_tasks.append(task)
                        counter += 1
                    else:
                        # Don't show tasks that can't be taken
                        pass
                
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
                        content = f"{status} {indent}{task.title} [{task.id[:8]}]"
                        print(format_numbered_item(counter, len([t for t in untakeable_tasks if t[2]]), content))
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

        elif args.command == 'done':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.complete_task(task.id)
                    print(f"Task marked as completed: {task.title}")
                else:
                    print(f"Task '{args.name}' not found")
            else:
                # Show only incomplete tasks to mark them as done
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True)
                incomplete_tasks = [(task, level) for task, level in hierarchical_tasks if not task.completed and not task.clean]
                
                if not incomplete_tasks:
                    print("No incomplete tasks in the project")
                    return

                print("\nAvailable tasks to mark as completed:")
                print("-" * 50)
                
                for i, (task, level) in enumerate(incomplete_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "◯"
                    indent = "  " * level
                    content = f"{status} {indent}{task.title} [{task.id[:8]}]"
                    print(format_numbered_item(i, len(incomplete_tasks), content))
                
                try:
                    choice = input("\nSelect the task number to mark as completed: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(incomplete_tasks):
                        task, _ = incomplete_tasks[task_index]
                        manager.complete_task(task.id)
                        print(f"Task marked as completed: {task.title}")
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
                # Show only completed tasks to mark them as undone
                hierarchical_tasks = manager.get_tasks_hierarchically(show_all=True, show_clean=True)
                completed_tasks = [(task, level) for task, level in hierarchical_tasks if task.completed and not task.clean]
                
                if not completed_tasks:
                    print("No completed tasks in the project")
                    return

                print("\nAvailable tasks to mark as not completed:")
                print("-" * 50)
                
                for i, (task, level) in enumerate(completed_tasks, 1):
                    if task.id in manager.active_tasks:
                        status = "*"
                    else:
                        status = "✓"
                    indent = "  " * level
                    content = f"{status} {indent}{task.title} [{task.id[:8]}]"
                    print(format_numbered_item(i, len(completed_tasks), content))
                
                try:
                    choice = input("\nSelect the task number to mark as not completed: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(completed_tasks):
                        task, _ = completed_tasks[task_index]
                        manager.uncomplete_task(task.id)
                        print(f"Task marked as not completed: {task.title}")
                    else:
                        print("Invalid selection")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()