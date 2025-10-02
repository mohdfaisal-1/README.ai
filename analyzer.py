import os
import json
import git
import shutil
import stat

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def generate_directory_tree(startpath):
    tree = []
    # Exclude venv and other common unnecessary folders from the tree
    exclude_dirs = ['.git', 'venv', '__pycache__', 'node_modules']
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree.append(f"{indent}├── {os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree.append(f"{subindent}└── {f}")
    return "\n".join(tree)


def analyze_repo(repo_url):
    temp_dir = "temp_repo_for_analysis"
    print(f"Cloning repository from {repo_url}...")

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, onerror=remove_readonly)

    try:
        git.Repo.clone_from(repo_url, temp_dir, depth=1)
        print("✅ Clone successful!")
        
        summary_parts = []
        # --- NEW: Variable to hold old README content ---
        old_readme_content = None
        language_extensions = {".py": 0, ".js": 0, ".java": 0, ".kt": 0, ".xml": 0, ".html": 0}

        for root, dirs, files in os.walk(temp_dir):
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # --- NEW: Find and read the existing README.md ---
                if file.lower() == 'readme.md':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            old_readme_content = f.read()
                    except Exception as e:
                        print(f"Could not read README.md: {e}")
                # --------------------------------------------------

                _, ext = os.path.splitext(file)
                if ext in language_extensions:
                    language_extensions[ext] += 1
                
                # (The rest of the file analysis logic remains the same)
                if file == 'requirements.txt':
                    # ... (rest of the analysis logic)
                    pass

        primary_language = max(language_extensions, key=language_extensions.get, default="N/A")
        summary_parts.insert(0, f"The primary language of the project appears to be {primary_language}.")
        
        tree_structure = generate_directory_tree(temp_dir)
        summary_parts.append(f"Project Directory Structure:\n```\n{tree_structure}\n```")

        unique_summary_parts = list(dict.fromkeys(summary_parts))
        
        # --- NEW: Return a dictionary with both analysis and old readme ---
        return {
            "analysis_summary": "\n\n".join(unique_summary_parts),
            "old_readme": old_readme_content
        }

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return {"error": f"Error: Failed to analyze the repository. {e}"}

    finally:
        if os.path.exists(temp_dir):
            print("Cleaning up temporary files...")
            shutil.rmtree(temp_dir, onerror=remove_readonly)
            print("Cleanup complete.")