import os
import requests
from flask import Flask, request, jsonify, render_template

from analyzer import analyze_repo

app = Flask(__name__)

LLAMA_API_KEY = "csk-dkfhp4fxtnp2x8h95cf555hvmk3924vm99cfwvkt8229v9p2"
# Note: We don't need the global LLAMA_API_URL here since it's defined in the function.

def generate_readme_from_summary(summary):
    """
    Sends the repository summary to the Cerebras Llama model to generate a README.
    """
    LLAMA_API_URL = "https://api.cerebras.ai/v1/chat/completions"

    prompt = f"""
You are an expert technical writer specializing in software documentation.
Based on the following analysis of a code repository, write a complete, professional, and high-quality README.md file.
The README should be well-structured and include at least the following sections:
- **Project Title**: A catchy and descriptive title.
- **Description**: A brief overview of what the project does.
- **Features**: A bulleted list of key features.
- **Installation**: How to install and set up the project (use the dependency info).
- **Usage**: How to run the project.
- **Contributing**: A short section on how others can contribute.
Use Markdown for formatting.
---
Repository Analysis:
{summary}
---
Now, generate the complete README.md file:
"""

    try:
        headers = {
            "Authorization": f"Bearer {LLAMA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-4-scout-17b-16e-instruct",
            "messages": [
                {
                    "content": prompt,
                    "role": "user" 
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        response = requests.post(LLAMA_API_URL, headers=headers, json=data)
        response.raise_for_status()

        generated_text = response.json()['choices'][0]['message']['content']
        
        return generated_text

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Error: {e}")
        if e.response:
            print(f"Response Body: {e.response.text}")
        return "Error: Failed to communicate with the AI model."

# --- FIX IS HERE: These lines must NOT be indented ---

@app.route('/')
def index():
    """
    This is the main page of our web app. It just shows the user interface.
    """
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """
    This is our API endpoint. The frontend will send the GitHub URL here.
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url') # Use .get() for safety

        if not repo_url:
            return jsonify({"error": "Repository URL is required."}), 400
        
        repo_summary = analyze_repo(repo_url)
        if "Error" in repo_summary:
            return jsonify({"error": repo_summary}), 500
        
        readme_text = generate_readme_from_summary(repo_summary)
        if "Error" in readme_text:
            return jsonify({"error": readme_text}), 500
        
        return jsonify({"readme": readme_text})
    
    except Exception as e:
        print(f"❌ An error occurred in /generate: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)