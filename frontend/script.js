document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const textInput = document.getElementById('textInput');
    const getKeywordsButton = document.getElementById('getKeywordsButton');
    const keywordsLoadingIndicator = document.getElementById('keywordsLoadingIndicator');
    
    const keywordManagementSection = document.getElementById('keywordManagementSection');
    const primaryKeywordsInput = document.getElementById('primaryKeywordsInput');
    const suggestedKeywordsArea = document.getElementById('suggestedKeywordsArea');
    const suggestedKeywordsContainer = document.getElementById('suggestedKeywordsContainer');

    const advancedSearchSection = document.getElementById('advancedSearchSection');
    const languageInput = document.getElementById('languageInput');
    const minStarsInput = document.getElementById('minStarsInput');
    const maxStarsInput = document.getElementById('maxStarsInput');
    const updatedAfterInput = document.getElementById('updatedAfterInput');
    const excludeForksCheckbox = document.getElementById('excludeForksCheckbox');
    const searchGitHubButton = document.getElementById('searchGitHubButton');
    const searchLoadingIndicator = document.getElementById('searchLoadingIndicator');

    const resultsArea = document.getElementById('resultsArea');
    const themeToggleButton = document.getElementById('themeToggleButton');

    // --- API Endpoints ---
    // Ensure these match your FastAPI server's host and port
    const API_BASE_URL = 'http://localhost:7111/api'; 
    const GET_KEYWORDS_URL = `${API_BASE_URL}/get_keywords`;
    const SEARCH_GITHUB_URL = `${API_BASE_URL}/search_github`;

    // --- Event Listeners ---
    getKeywordsButton.addEventListener('click', fetchKeywords);
    searchGitHubButton.addEventListener('click', performGitHubSearch);
    themeToggleButton.addEventListener('click', toggleTheme);

    // Initialize theme
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
    
    // --- Functions ---
    function toggleTheme() {
        document.body.classList.toggle('dark-mode');
        let theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
    }

    function escapeHTML(str) {
        if (typeof str !== 'string') return '';
        return str.replace(/[&<>"']/g, match => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[match]));
    }

    function displayError(area, message) {
        area.innerHTML = `<p class="error">${escapeHTML(message)}</p>`;
    }

    async function fetchKeywords() {
        const text = textInput.value.trim();
        if (!text) {
            displayError(resultsArea, 'Please enter a description.');
            return;
        }

        keywordsLoadingIndicator.style.display = 'block';
        keywordManagementSection.style.display = 'none';
        advancedSearchSection.style.display = 'none';
        resultsArea.innerHTML = '';

        try {
            const response = await fetch(GET_KEYWORDS_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text }),
            });

            const data = await response.json(); // This is ProcessResponse

            if (!response.ok || data.code !== 200) {
                const errorMsg = (Array.isArray(data.message) && data.message.length > 0) ? data.message.join(', ') : (data.detail || 'Failed to fetch keywords.');
                displayError(resultsArea, `Error ${data.code || response.status}: ${errorMsg}`);
                return;
            }
            
            // data.message should be { primary_keywords: [], suggested_keywords: [] }
            if (typeof data.message === 'object' && data.message !== null) {
                primaryKeywordsInput.value = data.message.primary_keywords.join(', ');
                renderSuggestedKeywords(data.message.suggested_keywords);
                keywordManagementSection.style.display = 'block';
                advancedSearchSection.style.display = 'block';
            } else {
                 displayError(resultsArea, 'Received unexpected keyword data format from server.');
            }

        } catch (error) {
            console.error('Fetch keywords error:', error);
            displayError(resultsArea, `An error occurred: ${error.message}`);
        } finally {
            keywordsLoadingIndicator.style.display = 'none';
        }
    }

    function renderSuggestedKeywords(keywords) {
        suggestedKeywordsContainer.innerHTML = '';
        if (!keywords || keywords.length === 0) {
            suggestedKeywordsContainer.innerHTML = '<p>No suggestions.</p>';
            return;
        }
        keywords.forEach(kw => {
            const button = document.createElement('button');
            button.classList.add('suggested-keyword-button');
            button.textContent = escapeHTML(kw);
            button.addEventListener('click', () => addKeywordToPrimary(kw));
            suggestedKeywordsContainer.appendChild(button);
        });
    }

    function addKeywordToPrimary(keyword) {
        let currentKeywords = primaryKeywordsInput.value.split(',')
                                .map(k => k.trim())
                                .filter(k => k.length > 0);
        if (!currentKeywords.includes(keyword)) {
            currentKeywords.push(keyword);
            primaryKeywordsInput.value = currentKeywords.join(', ');
        }
    }

    async function performGitHubSearch() {
        const primaryKws = primaryKeywordsInput.value.split(',')
                                .map(k => k.trim())
                                .filter(k => k.length > 0);

        if (primaryKws.length === 0) {
            displayError(resultsArea, 'Please provide at least one primary keyword.');
            return;
        }

        const searchPayload = {
            keywords: primaryKws,
            language: languageInput.value.trim() || null,
            min_stars: minStarsInput.value ? parseInt(minStarsInput.value) : null,
            max_stars: maxStarsInput.value ? parseInt(maxStarsInput.value) : null,
            updated_after: updatedAfterInput.value.trim() || null,
            exclude_forks: excludeForksCheckbox.checked,
        };
        
        // Basic validation for updated_after format (YYYY-MM-DD)
        if (searchPayload.updated_after && !/^\d{4}-\d{2}-\d{2}$/.test(searchPayload.updated_after)) {
            displayError(resultsArea, 'Invalid date format for "Updated After". Please use YYYY-MM-DD.');
            return;
        }


        searchLoadingIndicator.style.display = 'block';
        resultsArea.innerHTML = '';

        try {
            const response = await fetch(SEARCH_GITHUB_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(searchPayload),
            });

            const data = await response.json(); // ProcessResponse

            if (!response.ok || data.code !== 200) {
                 const errorMsg = (Array.isArray(data.message) && data.message.length > 0) ? data.message.join(', ') : (data.detail || 'GitHub search failed.');
                displayError(resultsArea, `Error ${data.code || response.status}: ${errorMsg}`);
                return;
            }

            // data.message should be the list of repositories
            if (Array.isArray(data.message)) {
                displayResults(data.message);
            } else {
                displayError(resultsArea, 'Received unexpected search result format from server.');
            }

        } catch (error) {
            console.error('GitHub search error:', error);
            displayError(resultsArea, `An error occurred during search: ${error.message}`);
        } finally {
            searchLoadingIndicator.style.display = 'none';
        }
    }

    function displayResults(repositories) {
        resultsArea.innerHTML = ''; // Clear previous results or error messages
        if (!repositories || repositories.length === 0) {
            resultsArea.innerHTML = '<p>No repositories found matching your criteria.</p>';
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
});
