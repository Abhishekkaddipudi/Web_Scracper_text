import os

# Folders to ignore
IGNORE_DIRS = {
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".env",
    ".git",
    ".mypy_cache",
    ".idea",
    ".pytest_cache",
}


def print_tree(start_path=".", prefix=""):
    try:
        entries = sorted(os.listdir(start_path))
    except PermissionError:
        return  # Skip directories we don't have permission to access

    entries = [e for e in entries if e not in IGNORE_DIRS]
    entries_count = len(entries)

    for index, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        connector = "├── " if index < entries_count - 1 else "└── "
        print(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "│   " if index < entries_count - 1 else "    "
            print_tree(path, prefix + extension)


if __name__ == "__main__":
    cwd = os.getcwd()
    print(f"Project structure of: {cwd}")
    print_tree(cwd)
