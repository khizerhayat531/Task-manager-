
import json
import os

class Task:
    """Represents a single task with an id, title, priority, and status."""

    VALID_PRIORITIES = ("Low", "Medium", "High")

    def __init__(self, task_id: int, title: str, priority: str, completed: bool = False):
        self.id = task_id
        self.title = title
        self.priority = priority
        self.completed = completed

    # ── Serialisation helpers ──────────────────

    def to_dict(self) -> dict:
        """Convert the task to a plain dictionary (for JSON storage)."""
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create a Task instance from a plain dictionary."""
        return cls(
            task_id=data["id"],
            title=data["title"],
            priority=data["priority"],
            completed=data["completed"],
        )

   

    def __str__(self) -> str:
        status = "✔ Complete" if self.completed else "✗ Incomplete"
        return (
            f"  ID: {self.id:<4} | "
            f"Title: {self.title:<30} | "
            f"Priority: {self.priority:<6} | "
            f"Status: {status}"
        )



class TaskManager:
    """
    Manages a collection of Task objects.
    Handles add, view, update, delete, filter, load, and save operations.
    """

    FILE_PATH = "tasks.txt"

    def __init__(self):
        self._tasks: list[Task] = []
        self._next_id: int = 1
        self.load_tasks()


    def _find_task(self, task_id: int) -> Task | None:
        """Return the Task with the given ID, or None if not found."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def _display_task_list(self, tasks: list[Task]) -> None:
        """Print a formatted list of tasks."""
        if not tasks:
            print("\n  No tasks to display.")
            return
        print()
        print("  " + "-" * 75)
        for task in tasks:
            print(task)
        print("  " + "-" * 75)

    def _pick_task_id(self, prompt: str = "Enter Task ID: ") -> int | None:
        """
        Prompt the user for a Task ID.
        Returns the integer ID, or None if the input is invalid or cancelled.
        """
        raw = input(prompt).strip()
        if not raw:
            print("  No ID entered. Operation cancelled.")
            return None
        try:
            return int(raw)
        except ValueError:
            print("  Invalid input — please enter a numeric Task ID.")
            return None

    @staticmethod
    def _pick_priority(current: str = "") -> str:
        """
        Prompt the user to choose a priority level.
        Returns the chosen priority, or the current value if the user skips.
        """
        hint = f" (current: {current})" if current else ""
        print(f"  Select priority{hint}:")
        for i, p in enumerate(Task.VALID_PRIORITIES, start=1):
            print(f"    {i}. {p}")
        raw = input("  Enter number (or press Enter to keep current): ").strip()
        if not raw:
            return current
        try:
            index = int(raw) - 1
            if 0 <= index < len(Task.VALID_PRIORITIES):
                return Task.VALID_PRIORITIES[index]
            print("  Choice out of range — keeping current priority.")
            return current
        except ValueError:
            print("  Invalid input — keeping current priority.")
            return current


    def add_task(self) -> None:
        """Prompt the user for task details and add a new task to the list."""
        print("\n--- Add a Task ---")

        title = input("  Enter task title: ").strip()
        if not title:
            print("  Title cannot be empty. Task not added.")
            return
        
        priority = self._pick_priority()
        if not priority:
            print("  Priority not selected. Task not added.")
            return

        task = Task(self._next_id, title, priority)
        self._tasks.append(task)
        self._next_id += 1
        print(f"\n  ✔ Task '{task.title}' added with ID {task.id}.")

    def view_tasks(self) -> None:
        """Display all tasks in a readable format."""
        print("\n--- All Tasks ---")
        if not self._tasks:
            print("  No tasks found. Start by adding a task!")
            return
        self._display_task_list(self._tasks)

    def update_task(self) -> None:
        """Allow the user to update the title and/or priority of an existing task."""
        print("\n--- Update a Task ---")
        self.view_tasks()

        task_id = self._pick_task_id()
        if task_id is None:
            return

        task = self._find_task(task_id)
        if task is None:
            print(f"  No task found with ID {task_id}.")
            return

        new_title = input(
            f"  New title (current: '{task.title}', press Enter to keep): "
        ).strip()
        if new_title:
            task.title = new_title

        task.priority = self._pick_priority(current=task.priority)

        print(f"\n  ✔ Task {task.id} updated successfully.")

    def mark_complete(self) -> None:
        """Mark a selected task as complete."""
        print("\n--- Mark a Task as Complete ---")
        self.view_tasks()

        task_id = self._pick_task_id()
        if task_id is None:
            return

        task = self._find_task(task_id)
        if task is None:
            print(f"  No task found with ID {task_id}.")
            return

        if task.completed:
            print(f"  Task {task_id} is already marked as complete.")
            return

        task.completed = True
        print(f"\n  ✔ Task '{task.title}' marked as complete.")

    def delete_task(self) -> None:
        """Delete a task selected by the user."""
        print("\n--- Delete a Task ---")
        self.view_tasks()

        task_id = self._pick_task_id()
        if task_id is None:
            return

        task = self._find_task(task_id)
        if task is None:
            print(f"  No task found with ID {task_id}.")
            return

        confirm = input(
            f"  Are you sure you want to delete '{task.title}'? (yes/no): "
        ).strip().lower()

        if confirm in ("yes", "y"):
            self._tasks.remove(task)
            print(f"\n  ✔ Task '{task.title}' (ID {task_id}) has been deleted.")
        else:
            print("  Deletion cancelled.")

    def filter_tasks(self) -> None:
        """Filter and display tasks by status or priority."""
        print("\n--- Filter Tasks ---")
        print("  Filter by:")
        print("    1. Status  (Complete / Incomplete)")
        print("    2. Priority (Low / Medium / High)")

        choice = input("  Enter your choice: ").strip()

        if choice == "1":
            self._filter_by_status()
        elif choice == "2":
            self._filter_by_priority()
        else:
            print("  Invalid choice. Returning to menu.")

    def _filter_by_status(self) -> None:
        """Show tasks filtered by their completion status."""
        print("  Show:")
        print("    1. Complete tasks")
        print("    2. Incomplete tasks")

        choice = input("  Enter your choice: ").strip()

        if choice == "1":
            results = [t for t in self._tasks if t.completed]
            label = "Complete"
        elif choice == "2":
            results = [t for t in self._tasks if not t.completed]
            label = "Incomplete"
        else:
            print("  Invalid choice.")
            return

        print(f"\n--- {label} Tasks ---")
        if not results:
            print(f"  No {label.lower()} tasks found.")
        else:
            self._display_task_list(results)

    def _filter_by_priority(self) -> None:
        """Show tasks filtered by priority level."""
        print("  Select priority:")
        for i, p in enumerate(Task.VALID_PRIORITIES, start=1):
            print(f"    {i}. {p}")

        raw = input("  Enter your choice: ").strip()
        try:
            index = int(raw) - 1
            if index < 0 or index >= len(Task.VALID_PRIORITIES):
                raise IndexError
            priority = Task.VALID_PRIORITIES[index]
        except (ValueError, IndexError):
            print("  Invalid choice.")
            return

        results = [t for t in self._tasks if t.priority == priority]
        print(f"\n--- {priority} Priority Tasks ---")
        if not results:
            print(f"  No tasks with '{priority}' priority found.")
        else:
            self._display_task_list(results)

    def save_tasks(self) -> None:
        """Save all tasks to tasks.txt as JSON."""
        try:
            data = {
                "next_id": self._next_id,
                "tasks": [task.to_dict() for task in self._tasks],
            }
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"\n  ✔ Tasks saved to '{self.FILE_PATH}'.")
        except OSError as e:
            print(f"\n  ✘ Could not save tasks: {e}")

    def load_tasks(self) -> None:
        """Load tasks from tasks.txt on startup, if the file exists."""
        if not os.path.exists(self.FILE_PATH):
            return 
        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._tasks = [Task.from_dict(d) for d in data.get("tasks", [])]
            self._next_id = data.get("next_id", len(self._tasks) + 1)
            print(f"  ✔ Loaded {len(self._tasks)} task(s) from '{self.FILE_PATH}'.")
        except (OSError, json.JSONDecodeError, KeyError) as e:
            print(f"  ✘ Could not load tasks from file: {e}")
            print("  Starting with an empty task list.")
            self._tasks = []
            self._next_id = 1

MENU = """
===== Task Manager =====
  1. Add a task
  2. View all tasks
  3. Update a task
  4. Mark a task as complete
  5. Delete a task
  6. Filter tasks
  7. Exit
========================
"""


def run() -> None:
    """Main loop — display the menu and dispatch user choices."""
    manager = TaskManager()

    actions = {
        "1": manager.add_task,
        "2": manager.view_tasks,
        "3": manager.update_task,
        "4": manager.mark_complete,
        "5": manager.delete_task,
        "6": manager.filter_tasks,
    }

    while True:
        print(MENU)
        choice = input("Enter your choice: ").strip()

        if choice == "7":
            manager.save_tasks()
            print("\n  Goodbye! See you next time.\n")
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("  Invalid choice — please enter a number between 1 and 7.")


if __name__ == "__main__":
    run()