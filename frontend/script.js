document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const resultsArea = document.getElementById('resultsArea');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const themeToggleButton = document.getElementById('themeToggleButton');

    // Configure your backend URL here
    // It should match the host and port your FastAPI backend is running on.
    // CFG.server_post is 7111 and CFG.host is "0.0.0.0"
    // If running locally, "http://localhost:7111" or "http://127.0.0.1:7111" should work.
    const backendUrl = 'http://localhost:7111/api/search_github';

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent new line in textarea
            performSearch();
        }
    });

    async function performSearch() {
        const queryText = searchInput.value.trim();
        if (!queryText) {
            resultsArea.innerHTML = '<p class="error">Please enter some text to search.</p>';
            return;
        }

        resultsArea.innerHTML = ''; // Clear previous results
        loadingIndicator.style.display = 'block'; // Show loading indicator

        try {
            const response = await fetch(backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: queryText }),
            });

            loadingIndicator.style.display = 'none'; // Hide loading indicator

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: `HTTP error! status: ${response.status}` }));
                resultsArea.innerHTML = `<p class="error">Error: ${errorData.message || response.statusText}</p>`;
                return;
            }

            const data = await response.json(); // This is your ProcessResponse

            if (data.code === 200 && data.message && data.message.length > 0) {
                displayResults(data.message);
            } else if (data.code !== 200) {
                // Handle specific error codes from your backend if needed
                let errorMessage = "Search failed.";
                if (Array.isArray(data.message) && data.message.length > 0) {
                    errorMessage = data.message.join(', ');
                } else if (typeof data.message === 'string') {
                    errorMessage = data.message;
                }
                resultsArea.innerHTML = `<p class="error">Error ${data.code}: ${errorMessage}</p>`;
            } 
            else {
                resultsArea.innerHTML = '<p>No repositories found for your query.</p>';
            }

        } catch (error) {
            loadingIndicator.style.display = 'none'; // Hide loading indicator
            console.error('Search API call failed:', error);
            resultsArea.innerHTML = `<p class="error">An error occurred while trying to reach the server: ${error.message}</p>`;
        }
    }

    function displayResults(repositories) {
        if (!repositories || repositories.length === 0) {
            resultsArea.innerHTML = '<p>No repositories found.</p>';
            return;
        }

        const ul = document.createElement('ul');
        ul.style.listStyleType = 'none';
        ul.style.paddingLeft = '0';

        repositories.forEach(repo => {
            const item = document.createElement('li');
            item.classList.add('result-item');

            const description = repo.description || 'N/A';
            let descriptionHTML = '';
            const maxLength = 100;

            if (description.length > maxLength) {
                const shortDesc = description.substring(0, maxLength) + '...';
                descriptionHTML = `
                    <p class="repo-description">
                        <span class="short-desc">${escapeHTML(shortDesc)}</span>
                        <span class="full-desc" style="display:none;">${escapeHTML(description)}</span>
                        <a href="#" class="read-more">Read more</a>
                    </p>`;
            } else {
                descriptionHTML = `<p class="repo-description">${escapeHTML(description)}</p>`;
            }

            item.innerHTML = `
                <h3><a href="${repo.html_url}" target="_blank">${escapeHTML(repo.full_name)}</a></h3>
                ${descriptionHTML}
                <p><strong>Stars:</strong> ${repo.stargazers_count} | <strong>Forks:</strong> ${repo.forks_count} | <strong>Open Issues:</strong> ${repo.open_issues_count}</p>
            `;
            ul.appendChild(item);
        });
        resultsArea.appendChild(ul);

        // Add event listeners for "Read more/less" links
        resultsArea.querySelectorAll('.read-more').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const parentP = this.closest('.repo-description');
                const shortDesc = parentP.querySelector('.short-desc');
                const fullDesc = parentP.querySelector('.full-desc');

                if (fullDesc.style.display === 'none') {
                    shortDesc.style.display = 'none';
                    fullDesc.style.display = 'inline';
                    this.textContent = 'Read less';
                } else {
                    shortDesc.style.display = 'inline';
                    fullDesc.style.display = 'none';
                    this.textContent = 'Read more';
                }
            });
        });
    }

    // Helper function to escape HTML special characters
    function escapeHTML(str) {
        if (typeof str !== 'string') return '';
        return str.replace(/[&<>"']/g, function (match) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            }[match];
        });
    }

    // Theme Toggle Logic
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }

    themeToggleButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        let theme = 'light';
        if (document.body.classList.contains('dark-mode')) {
            theme = 'dark';
        }
        localStorage.setItem('theme', theme);
    });
});
