from typing import List
from fastapi import APIRouter, Body, Request, HTTPException
import logging
from config import Config
from llm.llm_agent import Agent
from api.request import InputRequest, KeyWordRequest
from api.response import ProcessResponse
import requests

logging.basicConfig(level=logging.INFO)
router = APIRouter()

CFG = Config()

@router.post("/api/get_keywords")
async def get_keywords(request1: Request, request: InputRequest) -> ProcessResponse:
    logging.info(f"输入文本: {request.text}")
    agent = Agent()
    response = agent.get_keyword(request.text)
    return response

@router.post("/api/search_github")
# async def search_github(request1: Request, keyword_list: KeyWordRequest) -> ProcessResponse:
async def search_github(request1: Request, request: InputRequest) -> ProcessResponse:
    logging.info(f"输入文本: {request.text}")
    agent = Agent()
    keywords_response = agent.get_keyword(request.text)
    # print(keywords_response.message)
    search_response = agent.search_keyword(keywords_response.message)
    return search_response