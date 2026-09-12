import os

# ============================================================
# CONFIGURATION
# Change this to the directory you want to inspect
# ============================================================

DIRECTORY = "."


# ============================================================
# DIRECTORY TREE GENERATOR
# ============================================================

def generate_tree(directory):
    directory = os.path.abspath(directory)

    if not os.path.isdir(directory):
        return f"ERROR: '{directory}' is not a valid directory."

    lines = []
    root_name = os.path.basename(directory.rstrip(os.sep))
    lines.append(f"{root_name}/")

    def add_directory(path, prefix=""):
        entries = sorted(os.listdir(path))

        # Separate directories and files
        directories = []
        files = []

        for entry in entries:
            full_path = os.path.join(path, entry)

            if os.path.isdir(full_path):
                directories.append(entry)
            else:
                files.append(entry)

        # Directories first, then files
        entries = directories + files

        for i, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            is_last = i == len(entries) - 1

            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + entry + ("/" if os.path.isdir(full_path) else ""))

            if os.path.isdir(full_path):
                new_prefix = prefix + ("    " if is_last else "│   ")
                add_directory(full_path, new_prefix)

    add_directory(directory)

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    tree = generate_tree(DIRECTORY)

    print(tree)