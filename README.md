# Planit - Project Task Manager

A simple task manager for projects that stores all information in `.planit/db.json`.

## Installation

1. Clone or copy the project
2. Make sure the `planit` script is executable:
   ```bash
   chmod +x planit
   ```

## Autocompletion Setup

To enable TAB autocompletion, add this to your `.bashrc` or `.zshrc`:

```bash
source /full/path/to/arrangit/completions.sh
```

## Usage

### Available Commands

- `./planit list` - List all tasks
- `./planit task "name"` - Create or select task
- `./planit subtask "name"` - Create or select subtask
- `./planit active` - Show active task
- `./planit done "name"` - Mark task as completed
- `./planit delete "name"` - Delete task

### Examples

```bash
# Create a new task
./planit task "Develop API" -d "Create user endpoints"

# Create a subtask (you'll select the parent task)
./planit subtask "Authentication"

# Mark task as completed
./planit done "Develop API"

# Delete task
./planit delete "Old task"

# View active task
./planit active

# List all tasks
./planit list
```

## Features

- **Name-based search**: No need to remember IDs
- **Autocompletion**: Use TAB to complete task names
- **Subtasks**: Create task hierarchies
- **Active task**: Always have an active task to work on
- **Persistence**: Everything is automatically saved in `.planit/db.json`

## File Structure

- `src/` - Program source code
- `.planit/db.json` - Task database
- `planit` - Main script
- `completions.sh` - Autocompletion script

