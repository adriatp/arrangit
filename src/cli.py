import argparse
import sys
from .project_manager import ProjectManager


def main():
    manager = ProjectManager()

    parser = argparse.ArgumentParser(description="Gestor de tareas del proyecto")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    subparsers.add_parser('init', help='Inicializar un nuevo proyecto')
    subparsers.add_parser('list', help='Listar todas las tareas')
    
    task_parser = subparsers.add_parser('task', help='Crear o seleccionar tarea')
    task_parser.add_argument('name', help='Nombre de la tarea')
    task_parser.add_argument('-d', '--description', help='Descripción de la tarea', default='')

    subtask_parser = subparsers.add_parser('subtask', help='Crear o seleccionar subtarea')
    subtask_parser.add_argument('name', help='Nombre de la subtarea')

    subparsers.add_parser('active', help='Mostrar tarea activa')

    done_parser = subparsers.add_parser('done', help='Marcar tarea como completada')
    done_parser.add_argument('name', nargs='?', help='Nombre de la tarea (opcional)')

    delete_parser = subparsers.add_parser('delete', help='Eliminar tarea')
    delete_parser.add_argument('name', nargs='?', help='Nombre de la tarea (opcional)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'init':
            manager.initialize_project()
            print(f"Proyecto inicializado en {manager.config_file}")
            return
        
        # For other commands, load existing project
        manager.load_project()
        
        if args.command == 'list':
            tasks = manager.get_all_tasks()
            if not tasks:
                print("No hay tareas en el proyecto")
                return

            print("\nTareas del proyecto:")
            print("-" * 50)
            
            for task in tasks:
                status = "✓" if task.completed else "◯"
                active = "*" if task.id == manager.active_task else " "
                indent = "  " if task.parent_id else ""
                print(f"{active} {status} {indent}{task.title} [{task.id[:8]}]")
                if task.description:
                    print(f"     {task.description}")

        elif args.command == 'task':
            existing_task = manager.find_task_by_name(args.name)
            
            if existing_task:
                manager.set_active_task(existing_task.id)
                print(f"Tarea activa: {existing_task.title}")
            else:
                task_id = manager.create_task(args.name, args.description)
                manager.set_active_task(task_id)
                print(f"Tarea creada y activa: {args.name}")

        elif args.command == 'subtask':
            existing_task = manager.find_task_by_name(args.name)
            
            if existing_task:
                manager.set_active_task(existing_task.id)
                print(f"Subtarea activa: {existing_task.title}")
            else:
                hierarchical_tasks = manager.get_tasks_hierarchically()
                
                if not hierarchical_tasks:
                    print("No hay tareas disponibles para crear subtareas")
                    return
                
                print("\nTareas disponibles para subtarea:")
                print("-" * 50)
                for i, (task, level) in enumerate(hierarchical_tasks, 1):
                    status = "✓" if task.completed else "◯"
                    active = "*" if task.id == manager.active_task else " "
                    indent = "  " * level
                    print(f"{i}. {active} {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelecciona el número de la tarea padre: ")
                    parent_index = int(choice) - 1
                    
                    if 0 <= parent_index < len(hierarchical_tasks):
                        parent_task, _ = hierarchical_tasks[parent_index]
                        task_id = manager.create_task(args.name, "", parent_task.id)
                        manager.set_active_task(task_id)
                        print(f"Subtarea creada y activa: {args.name} (de {parent_task.title})")
                    else:
                        print("Selección inválida")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperación cancelada")

        elif args.command == 'active':
            active_task = manager.get_active_task()
            if active_task:
                print(f"Tarea activa: {active_task.title}")
                if active_task.description:
                    print(f"Descripción: {active_task.description}")
            else:
                print("No hay tarea activa")

        elif args.command == 'done':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.complete_task(task.id)
                    print(f"Tarea completada: {task.title}")
                else:
                    print(f"Tarea '{args.name}' no encontrada")
            else:
                tasks = manager.get_all_tasks()
                if not tasks:
                    print("No hay tareas en el proyecto")
                    return

                print("\nTareas disponibles para marcar como completadas:")
                print("-" * 50)
                
                for i, task in enumerate(tasks, 1):
                    status = "✓" if task.completed else "◯"
                    active = "*" if task.id == manager.active_task else " "
                    indent = "  " if task.parent_id else ""
                    print(f"{i}. {active} {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelecciona el número de la tarea a completar: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(tasks):
                        task = tasks[task_index]
                        manager.complete_task(task.id)
                        print(f"Tarea completada: {task.title}")
                    else:
                        print("Selección inválida")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperación cancelada")

        elif args.command == 'delete':
            if args.name:
                task = manager.find_task_by_name(args.name)
                if task:
                    manager.delete_task(task.id)
                    print(f"Tarea eliminada: {task.title}")
                else:
                    print(f"Tarea '{args.name}' no encontrada")
            else:
                tasks = manager.get_all_tasks()
                if not tasks:
                    print("No hay tareas en el proyecto")
                    return

                print("\nTareas disponibles para eliminar:")
                print("-" * 50)
                
                for i, task in enumerate(tasks, 1):
                    status = "✓" if task.completed else "◯"
                    active = "*" if task.id == manager.active_task else " "
                    indent = "  " if task.parent_id else ""
                    print(f"{i}. {active} {status} {indent}{task.title} [{task.id[:8]}]")
                
                try:
                    choice = input("\nSelecciona el número de la tarea a eliminar: ")
                    task_index = int(choice) - 1
                    
                    if 0 <= task_index < len(tasks):
                        task = tasks[task_index]
                        manager.delete_task(task.id)
                        print(f"Tarea eliminada: {task.title}")
                    else:
                        print("Selección inválida")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperación cancelada")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()