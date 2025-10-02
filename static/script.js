document.addEventListener('DOMContentLoaded', () => {
    const generateButton = document.getElementById('generate-button');
    const repoUrlInput = document.getElementById('repo-url-input');
    const loader = document.getElementById('loader');
    const output = document.querySelector('#output code');
    const copyButton = document.getElementById('copy-button');
    const exampleLinks = document.querySelectorAll('.example-links a');

    // Function to create a typewriter effect
    const typeWriter = (element, text, speed = 10) => {
        let i = 0;
        element.textContent = '';
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        type();
    };

    const handleGeneration = async () => {
        const repoUrl = repoUrlInput.value.trim();
        if (!repoUrl) {
            alert('Please enter a GitHub repository URL.');
            return;
        }

        // Disable button and show loader
        generateButton.disabled = true;
        generateButton.textContent = 'Generating...';
        loader.style.display = 'block';
        copyButton.style.display = 'none';
        output.textContent = '';

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ repo_url: repoUrl }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'An unknown error occurred.');
            }

            typeWriter(output, result.readme); // Use typewriter effect
            copyButton.style.display = 'block';

        } catch (error) {
            output.textContent = `Error: ${error.message}`;
            copyButton.style.display = 'none';
        } finally {
            // Re-enable button and hide loader
            generateButton.disabled = false;
            generateButton.textContent = '✨ Generate README';
            loader.style.display = 'none';
        }
    };

    generateButton.addEventListener('click', handleGeneration);

    copyButton.addEventListener('click', () => {
        navigator.clipboard.writeText(output.textContent).then(() => {
            copyButton.textContent = 'Copied!';
            setTimeout(() => { copyButton.textContent = 'Copy'; }, 2000);
        }).catch(err => console.error('Failed to copy text: ', err));
    });

    // Add functionality to example links
    exampleLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            repoUrlInput.value = link.dataset.url;
            // Optionally, trigger generation automatically
            // handleGeneration();
        });
    });
});