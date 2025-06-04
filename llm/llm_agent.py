import logging
import json

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import arxiv
import requests

from api.response import ProcessResponse
from llm.prompt import prompt
from utils.parse import BaseOutputParser
from config import Config
from typing import List, Dict, Union
from llm.filter_keywords import FilterKeywords


CFG = Config()

class Agent:
    def __init__(self):
        self.llm = ChatOpenAI(
            streaming=False,
            verbose=True,
            model_name = CFG.llm_model,
            temperature=CFG.temperature,
            openai_api_key=CFG.api_key,
            openai_api_base=CFG.llm_url,
            max_tokens=CFG.llm_max_tokens,
            openai_proxy=None
        )
        self.parse = BaseOutputParser()
        logging.info("llm agent init successfully!!!")
        
    def get_keyword(self, text: str) -> ProcessResponse:
        logging.info("解析关键词及建议...")
        # Use the new prompt template
        chat_prompt = PromptTemplate.from_template(prompt().get_keywords_and_suggestions_prompt)
        output_parser = StrOutputParser() # We'll parse JSON manually
        chain = chat_prompt | self.llm | output_parser
        
        try:
            raw_res = chain.invoke({"text": text})
            logging.debug(f"LLM raw response for keywords: {raw_res}")
            
            cleaned_res_str = raw_res.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
            
            parsed_res = json.loads(cleaned_res_str)
            
            primary_keywords = parsed_res.get("primary_keywords", [])
            suggested_keywords = parsed_res.get("suggested_keywords", [])

            if not isinstance(primary_keywords, list) or not all(isinstance(kw, str) for kw in primary_keywords):
                raise ValueError("Primary keywords are not a list of strings.")
            if not isinstance(suggested_keywords, list) or not all(isinstance(kw, str) for kw in suggested_keywords):
                raise ValueError("Suggested keywords are not a list of strings.")

            logging.info(f"解析成功: 主要关键词: {primary_keywords}, 建议关键词: {suggested_keywords}")
            return ProcessResponse(
                code=200,
                message={
                    "primary_keywords": primary_keywords,
                    "suggested_keywords": suggested_keywords
                }
            )

        except json.JSONDecodeError as e:
            logging.error(f"解析关键词JSON失败: {e}. Raw response: {raw_res}")
            return ProcessResponse(code=201, message=["Failed to parse keywords from LLM response (JSON format error)."])
        except ValueError as e: # Handles incorrect types within JSON
            logging.error(f"关键词数据类型错误: {e}. Parsed response: {parsed_res if 'parsed_res' in locals() else 'N/A'}")
            return ProcessResponse(code=202, message=[f"Keyword data format error: {e}"])
        except Exception as e:
            logging.error(f"解析关键词时发生未知错误: {e}")
            return ProcessResponse(code=203, message=["An unexpected error occurred while parsing keywords."])

    def search_github(self, 
                       keywords: List[str], 
                       language: str = None,
                       min_stars: int = None,
                       max_stars: int = None,
                       updated_after: str = None, # Expected format YYYY-MM-DD
                       exclude_forks: bool = False,
                       max_results=10) -> ProcessResponse: # Added type hint for ProcessResponse
        
        if not keywords:
            return ProcessResponse(code=400, message=["Keywords list cannot be empty for search."])

        logging.info(f"搜索关键词为: {keywords}, 语言: {language}, Star范围: {min_stars}-{max_stars}, 更新于: {updated_after}, 排除Forks: {exclude_forks}")
        
        query_parts = [kw.strip() for kw in keywords if kw.strip()] # Clean and join keywords
        
        if language:
            query_parts.append(f"language:{language.strip()}")
        
        if min_stars is not None and max_stars is not None:
            query_parts.append(f"stars:{min_stars}..{max_stars}")
        elif min_stars is not None:
            query_parts.append(f"stars:>={min_stars}")
        elif max_stars is not None:
            query_parts.append(f"stars:<={max_stars}")

        if updated_after: # Basic validation, more robust date validation could be added
            import re
            if re.match(r"^\d{4}-\d{2}-\d{2}$", updated_after):
                query_parts.append(f"pushed:>{updated_after}")
            else:
                logging.warning(f"Invalid updated_after date format: {updated_after}. Ignoring.")
        
        if exclude_forks:
            query_parts.append("fork:false")

        github_query = " ".join(query_parts)
        logging.info(f"Constructed GitHub query: {github_query}")

        headers = {
            'Authorization': f'token {CFG.github_access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        params = {
            'q': github_query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': max_results
        }
        
        try:
            response = requests.get(CFG.github_url, headers=headers, params=params)
            response.raise_for_status() # Raise HTTPError for bad responses (4XX or 5XX)
        except requests.exceptions.HTTPError as e:
            logging.error(f"GitHub API HTTP error: {e.response.status_code} - {e.response.text}")
            return ProcessResponse(
                code=e.response.status_code, # Use GitHub's status code
                message=[f"GitHub API error: {e.response.status_code} - {e.response.json().get('message', e.response.text)}"]
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"Could not connect to GitHub API: {e}")
            return ProcessResponse(
                code=503, 
                message=[f"Could not connect to GitHub API: {e}"]
            )
        
        raw_repos = response.json().get('items', [])
        if not raw_repos:
            return ProcessResponse(code=205, message=["No repositories found for the given criteria."])
            
        logging.info(f"从GitHub获取到 {len(raw_repos)} 个仓库，开始过滤...")
        
        
        filtered_repos = []
        for repo in raw_repos:
            repo_name_str = repo.get('full_name', '')
            repo_desc_str = repo.get('description') or '' 

            repo_name_lower = repo_name_str.lower()
            repo_desc_lower = repo_desc_str.lower()

            is_political = False
            for p_kw in FilterKeywords().combined_filter_keywords:
                is_english_kw = all(ord(char) < 128 for char in p_kw) and any(char.isalpha() for char in p_kw)

                if is_english_kw: 
                    if p_kw in repo_name_lower or p_kw in repo_desc_lower:
                        is_political = True
                        logging.info(f"Filtering out political repo (EN match): {repo.get('full_name')} due to keyword '{p_kw}'")
                        break
                else: 
                    if p_kw in repo_name_str or p_kw in repo_desc_str or \
                       p_kw in repo_name_lower or p_kw in repo_desc_lower: 
                        is_political = True
                        logging.info(f"Filtering out political repo (ZH/Mixed match): {repo.get('full_name')} due to keyword '{p_kw}'")
                        break
            
            if not is_political:
                repo_info = {
                    'full_name': repo['full_name'],
                    'description': repo['description'],
                    'html_url': repo['html_url'],
                    'stargazers_count': repo['stargazers_count'],
                    'forks_count': repo['forks_count'],
                    'open_issues_count': repo['open_issues_count'],
                }
                filtered_repos.append(repo_info)
            
        logging.info(f"过滤后剩余 {len(filtered_repos)} 个仓库")
        if not filtered_repos:
             return ProcessResponse(code=206, message=["No repositories found after filtering."])

        return ProcessResponse(
            code=200,
            message=filtered_repos
        )

    def search_arxiv(self, keywords: List[str], max_results: int = 10) -> ProcessResponse:
        """
        Search arXiv for papers based on keywords.
        
        Args:
            keywords: List of keywords to search for
            max_results: Maximum number of results to return (default 10)
            
        Returns:
            ProcessResponse containing list of paper information
        """
        logging.info(f"搜索arXiv，关键词: {keywords}")
        
        if not keywords:
            return ProcessResponse(code=400, message=["Keywords list cannot be empty for search."])

        try:
            # Construct the query string - join keywords with AND
            query = ' AND '.join(f'all:"{kw}"' for kw in keywords)
            
            # Search arXiv
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            papers = []
            for result in search.results():
                paper_info = {
                    'title': result.title,
                    'summary': result.summary,
                    'authors': [author.name for author in result.authors],
                    'published': result.published.strftime("%Y-%m-%d"),
                    'pdf_url': result.pdf_url,
                    'entry_id': result.entry_id,
                    'primary_category': result.primary_category,
                    'categories': result.categories,
                    'comment': result.comment,
                    'journal_ref': result.journal_ref,
                    'doi': result.doi
                }
                papers.append(paper_info)

            if not papers:
                return ProcessResponse(code=205, message=["No papers found matching the search criteria."])

            logging.info(f"找到 {len(papers)} 篇相关论文")
            return ProcessResponse(code=200, message=papers)

        except Exception as e:
            logging.error(f"arXiv搜索出错: {e}")
            return ProcessResponse(code=503, message=[f"Error searching arXiv: {str(e)}"])