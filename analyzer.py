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
    for root, dirs, files in os.walk(startpath):
        if '.git' in dirs:
            dirs.remove('.git')
        
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
        # --- THE FIX IS HERE: We added depth=1 ---
        git.Repo.clone_from(repo_url, temp_dir, depth=1)
        # -----------------------------------------
        
        print("✅ Clone successful!")
        
        summary_parts = []
        language_extensions = {".py": 0, ".js": 0, ".java": 0, ".kt": 0, ".xml": 0, ".html": 0}

        for root, dirs, files in os.walk(temp_dir):
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                if ext in language_extensions:
                    language_extensions[ext] += 1
                
                if file == 'requirements.txt':
                    with open(file_path, 'r') as f:
                        deps = f.read().strip().split('\n')
                        summary_parts.append(f"Python dependencies found: {', '.join(deps)}")
                elif file == 'package.json':
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        deps = data.get('dependencies', {}).keys()
                        summary_parts.append(f"JavaScript dependencies found: {', '.join(deps)}")
                elif file.endswith(('build.gradle', 'build.gradle.kts')):
                    summary_parts.append("Android (Gradle) project detected. Dependencies are defined in build.gradle files.")
                elif file == 'AndroidManifest.xml':
                    summary_parts.append("Found AndroidManifest.xml, which defines app components and permissions.")
                elif file == 'pom.xml':
                    summary_parts.append("Java (Maven) project detected. The dependencies are listed in pom.xml.")
        
        primary_language = max(language_extensions, key=language_extensions.get, default="N/A")
        summary_parts.insert(0, f"The primary language of the project appears to be {primary_language}.")
        
        tree_structure = generate_directory_tree(temp_dir)
        summary_parts.append(f"Project Directory Structure:\n```\n{tree_structure}\n```")

        unique_summary_parts = list(dict.fromkeys(summary_parts))
        return "\n\n".join(unique_summary_parts)

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return f"Error: Failed to analyze the repository. {e}"

    finally:
        if os.path.exists(temp_dir):
            print("Cleaning up temporary files...")
            shutil.rmtree(temp_dir, onerror=remove_readonly)
            print("Cleanup complete.")