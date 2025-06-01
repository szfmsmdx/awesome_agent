import logging

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

import requests
from fastapi import HTTPException

from api.request import InputRequest
from api.response import ProcessResponse
from llm.prompt import prompt
from utils.parse import BaseOutputParser
from config import Config
from typing import List


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
        logging.info("解析关键词...")
        chat_prompt = ChatPromptTemplate.from_template(prompt.parse_text_prompt)
        output_parse = StrOutputParser()
        chain = chat_prompt | self.llm | output_parse
        
        try:
            res = chain.invoke({"text": text})
            print("解析结果为：", res)
        except Exception as e:
            logging.error(f"解析关键词失败：{e}")
            return ProcessResponse(
                code=201,
                message="解析关键词失败"
            )
        
        # 检验一下 res 是否合规
        clean_res = self.parse.parse_prompt_response(res)    
        if len(clean_res) == 0:
            return ProcessResponse(
                code=202,
                message=["解析关键词失败"]
            )
        elif len(clean_res) > 1:
            return ProcessResponse(
                code=203,
                message=["关键词生成错误"]
            )
        else:
            return ProcessResponse(
                code=200,
                message=clean_res[0]
            )        

    def search_keyword(self, keywords:List[str], max_results=10):
        logging.info(f"搜索关键词为: {keywords}")
        
        # 构建 GitHub 查询参数
        headers = {
            'Authorization': f'token {CFG.github_access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        params = {
            'q': keywords,
            'sort': 'stars',  # 可选：按星数排序
            'order': 'desc',  # 可选：降序排列
            'per_page': max_results
        }
        try:
            response = requests.get(CFG.github_url, headers=headers, params=params)
        except Exception as e:
            print(e)
            return ProcessResponse(
                code=204,
                message=[f"could not get github url, code is {response.status_code}"]
            )
        if response.status_code != 200:
            return ProcessResponse(
                code=204,
                message=[f"could not get github url, code is {response.status_code}"]
            )
        
        repos = response.json().get('items', [])
        if not repos:
            return ProcessResponse(code=205, message=["No repositories found"])
            
        repo_details = []
        for repo in repos:
            repo_info = {
                'full_name': repo['full_name'],
                'description': repo['description'],
                'html_url': repo['html_url'],
                'stargazers_count': repo['stargazers_count'],
                'forks_count': repo['forks_count'],
                'open_issues_count': repo['open_issues_count'],
                # 'owner': {
                    # 'login': repo['owner']['login'],
                    # 'html_url': repo['owner']['html_url']
                # }
            }
            repo_details.append(repo_info)
        
        return ProcessResponse(
            code=200,
            message=repo_details
        )