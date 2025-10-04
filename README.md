# Arrangit - Project Task Manager

A simple task manager for projects that stores all information in `.arrangit.json`.

## Installation

1. Clone or copy the project
2. Make sure the `arrangit` script is executable:
   ```bash
   chmod +x arrangit
   ```

## Autocompletion Setup

To enable TAB autocompletion, add this to your `.bashrc` or `.zshrc`:

```bash
source /full/path/to/arrangit/completions.sh
```

## Usage

### Available Commands

- `./arrangit list` - List all tasks
- `./arrangit task "name"` - Create or select task
- `./arrangit subtask "name"` - Create or select subtask
- `./arrangit active` - Show active task
- `./arrangit done "name"` - Mark task as completed
- `./arrangit delete "name"` - Delete task

### Examples

```bash
# Create a new task
./arrangit task "Develop API" -d "Create user endpoints"

# Create a subtask (you'll select the parent task)
./arrangit subtask "Authentication"

# Mark task as completed
./arrangit done "Develop API"

# Delete task
./arrangit delete "Old task"

# View active task
./arrangit active

# List all tasks
./arrangit list
```

## Features

- **Name-based search**: No need to remember IDs
- **Autocompletion**: Use TAB to complete task names
- **Subtasks**: Create task hierarchies
- **Active task**: Always have an active task to work on
- **Persistence**: Everything is automatically saved in `.arrangit.json`

## File Structure

- `src/` - Program source code
- `.arrangit.json` - Task database
- `arrangit` - Main script
- `completions.sh` - Autocompletion script

