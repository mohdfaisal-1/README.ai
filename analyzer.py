import os
import json
import git
import shutil
import stat

# This is our "smarter cleanup" function to handle Windows permissions
def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def analyze_repo(repo_url):
    temp_dir = "temp_repo_for_analysis"
    print(f"Cloning repository from {repo_url}...")

    # Clean up any old directories first, just in case
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, onerror=remove_readonly)

    try:
        git.Repo.clone_from(repo_url, temp_dir)
        print("✅ Clone successful!")
        
        # --- NEW: Advanced Analysis ---
        summary_parts = []
        file_list = []
        language_extensions = {".py": 0, ".js": 0, ".java": 0, ".kt":0, ".xml":0, ".html": 0, ".css": 0}

        for root, dirs, files in os.walk(temp_dir):
            # Skip the .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)

                # Language detection
                _, ext = os.path.splitext(file)
                if ext in language_extensions:
                    language_extensions[ext] += 1
                
                # Dependency file analysis
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
                # -----------------------------

                elif file == 'pom.xml':
                    summary_parts.append("Java (Maven) project detected. The dependencies are listed in pom.xml.")


                # Code snippet extraction (from common files)
                # if file.lower() in ['app.py', 'index.js', 'main.py', 'server.js']:
                #     with open(file_path, 'r', errors='ignore') as f:
                #         snippet = f.read(500) # Read first 500 characters
                #         summary_parts.append(f"Code snippet from '{file}':\n---\n{snippet}\n---")

        # Determine primary language
        primary_language = max(language_extensions, key=language_extensions.get, default="N/A")
        summary_parts.insert(0, f"The primary language of the project appears to be {primary_language}.")
        
        # Add file structure overview
        root_contents = [item for item in os.listdir(temp_dir) if item != '.git']
        summary_parts.append(f"The root directory contains: {', '.join(root_contents)}")

        unique_summary_parts = list(dict.fromkeys(summary_parts))
        return "\n\n".join(unique_summary_parts)

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return f"Error: Failed to analyze the repository. {e}"

    finally:
        # This block ensures cleanup happens even if there's an error
        if os.path.exists(temp_dir):
            print("Cleaning up temporary files...")
            shutil.rmtree(temp_dir, onerror=remove_readonly)
            print("Cleanup complete.")

# This part allows us to run this file directly for testing
if __name__ == '__main__':
    # We'll test it with a simple, known repository
    test_url = 'https://github.com/realpython/flask-boilerplate'
    analyze_repo(test_url)