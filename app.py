import os
import requests
from flask import Flask, request, jsonify, render_template

from analyzer import analyze_repo

app = Flask(__name__)

LLAMA_API_KEY = "csk-dkfhp4fxtnp2x8h95cf555hvmk3924vm99cfwvkt8229v9p2"

def generate_readme_from_summary(summary):
    """
    Sends the repository summary to the Cerebras Llama model to generate a README.
    """
    LLAMA_API_URL = "https://api.cerebras.ai/v1/chat/completions"

    prompt = f"""
You are "ReadmeBot", an expert AI technical writer and developer assistant. Your mission is to create the highest quality README.md file for the given repository.

**Analysis of the repository is as follows:**
{summary}

**Your Task:**
Based *only* on the analysis provided, generate a complete, well-structured, and professional README.md file.

**Instructions & Rules:**
1.  **Structure:** The README must have the following sections:
    - A short, catchy Project Title.
    - A "Description" section that explains the project's purpose and what it does.
    - A "Key Features" section with a bulleted list.
    - A "Technologies Used" section listing the primary language and key libraries/frameworks found in the analysis.
    - An "Installation" section with a code block showing the necessary steps. If dependencies are listed, assume they are installed with `pip` or `npm`.
    - A "Usage" section explaining how to run the application, with a code block if possible.
2.  **Infer intelligently:**
    - From the file names and dependencies, infer the project's main purpose. (e.g., if you see Flask and `app.py`, it's a Python web application).
    - If you see `build.gradle` and `.kt` files, it's an Android application.
    - Create logical installation and usage steps. If it's a Python app with a `requirements.txt`, the installation is `pip install -r requirements.txt`. If it has an `app.py`, the usage is likely `python app.py`.
3.  **Be concise and clear:** Use Markdown for formatting (headings, bold text, code blocks, lists). The tone should be professional and welcoming to new developers.
4.  **Do not invent information:** Base the entire README *only* on the analysis provided above. Do not add features or instructions that cannot be inferred from the context.
5.  **Formatting:** All section titles **must be level-two Markdown headings (##)** and **must start with a relevant emoji**. For example: "## 🚀 Description", "## 🛠️ Installation", "## ⚙️ Usage".

Now, generate the complete README.md file.
"""

    try:
        headers = {
            "Authorization": f"Bearer {LLAMA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.3-70b",
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
        repo_url = data.get('repo_url')

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