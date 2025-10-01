document.addEventListener('DOMContentLoaded', () => {
    const generateButton = document.getElementById('generate-button');
    const repoUrlInput = document.getElementById('repo-url-input');
    const loader = document.getElementById('loader');
    const output = document.querySelector('#output code');
    const copyButton = document.getElementById('copy-button');

    generateButton.addEventListener('click', async () => {
        const repoUrl = repoUrlInput.value.trim();

        if (!repoUrl) {
            alert('Please enter a GitHub repository URL.');
            return;
        }

        // Show loader, hide copy button, and clear previous output
        loader.style.display = 'block';
        copyButton.style.display = 'none';
        output.textContent = '';

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ repo_url: repoUrl }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'An unknown error occurred.');
            }

            output.textContent = result.readme;
            copyButton.style.display = 'block'; // Show copy button on success

        } catch (error) {
            output.textContent = `Error: ${error.message}`;
            copyButton.style.display = 'none';
        } finally {
            // Hide loader
            loader.style.display = 'none';
        }
    });

    copyButton.addEventListener('click', () => {
        navigator.clipboard.writeText(output.textContent).then(() => {
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = 'Copy';
            }, 2000); // Reset text after 2 seconds
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    });
});