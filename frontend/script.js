document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const textInput = document.getElementById('textInput');
    const getKeywordsButton = document.getElementById('getKeywordsButton');
    const keywordsLoadingIndicator = document.getElementById('keywordsLoadingIndicator');
    
    const searchSection = document.getElementById('searchSection');
    const primaryKeywordsContainer = document.getElementById('primaryKeywordsContainer');
    const primaryKeywordsInput = document.getElementById('primaryKeywordsInput');
    const suggestedKeywordsArea = document.getElementById('suggestedKeywordsArea');
    const suggestedKeywordsContainer = document.getElementById('suggestedKeywordsContainer');
    const updatedAfterInput = document.getElementById('updatedAfterInput');
    const searchButton = document.getElementById('searchButton');
    const searchLoadingIndicator = document.getElementById('searchLoadingIndicator');

    const resultsContainer = document.getElementById('resultsContainer');
    const githubResultsArea = document.getElementById('githubResultsArea');
    const arxivResultsArea = document.getElementById('arxivResultsArea');
    const themeToggleButton = document.getElementById('themeToggleButton');

    // --- API Endpoints ---
    const API_BASE_URL = 'http://localhost:7111/api';
    const GET_KEYWORDS_URL = `${API_BASE_URL}/get_keywords`;
    const SEARCH_GITHUB_URL = `${API_BASE_URL}/search_github`;
    const SEARCH_ARXIV_URL = `${API_BASE_URL}/search_arxiv`;

    // --- Event Listeners ---
    getKeywordsButton.addEventListener('click', fetchKeywords);
    searchButton.addEventListener('click', performSearch);
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

    function renderPrimaryKeywords(keywords) {
        primaryKeywordsContainer.innerHTML = '';
        keywords.forEach(keyword => {
            const button = document.createElement('span');
            button.className = 'keyword-button';
            button.innerHTML = `
                ${escapeHTML(keyword)}
                <span class="remove-keyword" title="移除关键词">×</span>
            `;
            
            button.querySelector('.remove-keyword').addEventListener('click', (e) => {
                e.stopPropagation();
                removeKeyword(keyword);
            });
            
            primaryKeywordsContainer.appendChild(button);
        });
        
        // Update hidden input with current keywords
        primaryKeywordsInput.value = keywords.join(',');
    }

    function removeKeyword(keywordToRemove) {
        const currentKeywords = primaryKeywordsInput.value.split(',')
            .map(k => k.trim())
            .filter(k => k.length > 0 && k !== keywordToRemove);
        
        renderPrimaryKeywords(currentKeywords);
    }

    function addKeywordToPrimary(keyword) {
        const currentKeywords = primaryKeywordsInput.value.split(',')
            .map(k => k.trim())
            .filter(k => k.length > 0);
            
        if (!currentKeywords.includes(keyword)) {
            currentKeywords.push(keyword);
            renderPrimaryKeywords(currentKeywords);
        }
    }

    async function fetchKeywords() {
        const text = textInput.value.trim();
        if (!text) {
            displayError(githubResultsArea, '请输入描述。');
            displayError(arxivResultsArea, '请输入描述。');
            return;
        }

        keywordsLoadingIndicator.style.display = 'block';
        searchSection.style.display = 'none';
        resultsContainer.style.display = 'none';
        githubResultsArea.innerHTML = '';
        arxivResultsArea.innerHTML = '';

        try {
            const response = await fetch(GET_KEYWORDS_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text }),
            });

            const data = await response.json();

            if (!response.ok || data.code !== 200) {
                const errorMsg = (Array.isArray(data.message) && data.message.length > 0) ? data.message.join(', ') : (data.detail || '获取关键词失败。');
                displayError(githubResultsArea, `错误 ${data.code || response.status}: ${errorMsg}`);
                displayError(arxivResultsArea, `错误 ${data.code || response.status}: ${errorMsg}`);
                return;
            }
            
            if (typeof data.message === 'object' && data.message !== null) {
                renderPrimaryKeywords(data.message.primary_keywords);
                renderSuggestedKeywords(data.message.suggested_keywords);
                searchSection.style.display = 'block';
            } else {
                displayError(githubResultsArea, '从服务器收到意外的关键词数据格式。');
                displayError(arxivResultsArea, '从服务器收到意外的关键词数据格式。');
            }

        } catch (error) {
            console.error('Fetch keywords error:', error);
            displayError(githubResultsArea, `发生错误: ${error.message}`);
            displayError(arxivResultsArea, `发生错误: ${error.message}`);
        } finally {
            keywordsLoadingIndicator.style.display = 'none';
        }
    }

    function renderSuggestedKeywords(keywords) {
        suggestedKeywordsContainer.innerHTML = '';
        if (!keywords || keywords.length === 0) {
            suggestedKeywordsContainer.innerHTML = '<p>没有建议。</p>';
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

    async function performSearch() {
        const primaryKws = primaryKeywordsInput.value.split(',')
                                .map(k => k.trim())
                                .filter(k => k.length > 0);

        if (primaryKws.length === 0) {
            displayError(githubResultsArea, '请提供至少一个主要关键词。');
            displayError(arxivResultsArea, '请提供至少一个主要关键词。');
            return;
        }

        const updatedAfter = updatedAfterInput.value.trim();
        if (updatedAfter && !/^\d{4}-\d{2}-\d{2}$/.test(updatedAfter)) {
            displayError(githubResultsArea, '更新时间格式无效。请使用 YYYY-MM-DD 格式。');
            displayError(arxivResultsArea, '更新时间格式无效。请使用 YYYY-MM-DD 格式。');
            return;
        }

        searchLoadingIndicator.style.display = 'block';
        resultsContainer.style.display = 'flex';
        githubResultsArea.innerHTML = '<p>正在搜索 GitHub 仓库...</p>';
        arxivResultsArea.innerHTML = '<p>正在搜索 arXiv 论文...</p>';

        // 并行执行两个搜索
        try {
            const [githubResponse, arxivResponse] = await Promise.all([
                fetch(SEARCH_GITHUB_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        keywords: primaryKws,
                        updated_after: updatedAfter || null,
                        exclude_forks: true, // 默认排除fork的仓库
                        min_stars: 10 // 默认只显示10星以上的仓库
                    }),
                }),
                fetch(SEARCH_ARXIV_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        keywords: primaryKws
                    }),
                })
            ]);

            const [githubData, arxivData] = await Promise.all([
                githubResponse.json(),
                arxivResponse.json()
            ]);

            // 处理 GitHub 结果
            if (!githubResponse.ok || githubData.code !== 200) {
                const errorMsg = (Array.isArray(githubData.message) && githubData.message.length > 0) ? 
                    githubData.message.join(', ') : (githubData.detail || 'GitHub 搜索失败。');
                displayError(githubResultsArea, `错误 ${githubData.code || githubResponse.status}: ${errorMsg}`);
            } else if (Array.isArray(githubData.message)) {
                displayGitHubResults(githubData.message);
            } else {
                displayError(githubResultsArea, '从服务器收到意外的搜索结果格式。');
            }

            // 处理 arXiv 结果
            if (!arxivResponse.ok || arxivData.code !== 200) {
                const errorMsg = (Array.isArray(arxivData.message) && arxivData.message.length > 0) ? 
                    arxivData.message.join(', ') : (arxivData.detail || 'arXiv 搜索失败。');
                displayError(arxivResultsArea, `错误 ${arxivData.code || arxivResponse.status}: ${errorMsg}`);
            } else if (Array.isArray(arxivData.message)) {
                displayArxivResults(arxivData.message);
            } else {
                displayError(arxivResultsArea, '从服务器收到意外的搜索结果格式。');
            }

        } catch (error) {
            console.error('Search error:', error);
            displayError(githubResultsArea, `搜索时发生错误: ${error.message}`);
            displayError(arxivResultsArea, `搜索时发生错误: ${error.message}`);
        } finally {
            searchLoadingIndicator.style.display = 'none';
        }
    }

    function truncateText(text, maxLength = 50) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    }

    function createDescriptionElement(description, isArxiv = false) {
        if (!description) return '<p>暂无描述</p>';
        
        const fullText = description;
        if (fullText.length <= 50) {
            return `<p>${isArxiv ? renderLatex(escapeHTML(fullText)) : escapeHTML(fullText)}</p>`;
        }

        const shortText = truncateText(fullText, 50);
        const containerId = `desc-${Math.random().toString(36).substr(2, 9)}`;
        
        return `
            <div class="description-container" id="${containerId}">
                <p class="description-short">${isArxiv ? renderLatex(escapeHTML(shortText)) : escapeHTML(shortText)}
                    <button class="read-more-btn" onclick="toggleDescription('${containerId}')">阅读更多</button>
                </p>
                <p class="description-full" style="display: none">${isArxiv ? renderLatex(escapeHTML(fullText)) : escapeHTML(fullText)}
                    <button class="read-more-btn" onclick="toggleDescription('${containerId}')">收起</button>
                </p>
            </div>
        `;
    }

    // Add this to the window object so it can be called from inline onclick
    window.toggleDescription = function(containerId) {
        const container = document.getElementById(containerId);
        const shortDesc = container.querySelector('.description-short');
        const fullDesc = container.querySelector('.description-full');
        
        if (shortDesc.style.display !== 'none') {
            shortDesc.style.display = 'none';
            fullDesc.style.display = 'block';
        } else {
            shortDesc.style.display = 'block';
            fullDesc.style.display = 'none';
        }
    };

    function renderLatex(text) {
        // Replace $...$ with rendered LaTeX
        return text.replace(/\$(.*?)\$/g, (match, latex) => {
            try {
                return katex.renderToString(latex, {
                    throwOnError: false,
                    displayMode: false
                });
            } catch (e) {
                console.error('LaTeX rendering error:', e);
                return match; // Return original text if rendering fails
            }
        });
    }

    function displayGitHubResults(repos) {
        if (!repos.length) {
            githubResultsArea.innerHTML = '<p>未找到匹配的仓库。</p>';
            return;
        }

        const resultsHTML = repos.map(repo => `
            <div class="github-result">
                <h3><a href="${escapeHTML(repo.html_url)}" target="_blank">${escapeHTML(repo.full_name)}</a></h3>
                ${createDescriptionElement(repo.description)}
                <div class="github-result-stats">
                    <span>⭐ ${repo.stargazers_count}</span>
                    <span>🔄 ${repo.forks_count}</span>
                    <span>⚠️ ${repo.open_issues_count}</span>
                </div>
            </div>
        `).join('');

        githubResultsArea.innerHTML = resultsHTML;
    }

    function displayArxivResults(papers) {
        if (!papers.length) {
            arxivResultsArea.innerHTML = '<p>未找到匹配的论文。</p>';
            return;
        }

        const resultsHTML = papers.map(paper => `
            <div class="arxiv-result">
                <h3><a href="${escapeHTML(paper.pdf_url)}" target="_blank">${escapeHTML(paper.title)}</a></h3>
                <div class="arxiv-result-authors">
                    ${escapeHTML(paper.authors.join(', '))}
                </div>
                <div class="arxiv-result-meta">
                    发布日期: ${escapeHTML(paper.published)}
                    ${paper.journal_ref ? `<br>期刊引用: ${escapeHTML(paper.journal_ref)}` : ''}
                    ${paper.doi ? `<br>DOI: ${escapeHTML(paper.doi)}` : ''}
                </div>
                ${createDescriptionElement(paper.summary, true)}
                <div class="arxiv-result-categories">
                    ${paper.categories.map(cat => `<span class="arxiv-category">${escapeHTML(cat)}</span>`).join('')}
                </div>
            </div>
        `).join('');

        arxivResultsArea.innerHTML = resultsHTML;
    }
});
