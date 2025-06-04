from typing import List, Union, Dict
from fastapi import APIRouter, Body, Request, HTTPException
import logging
from config import Config
from llm.llm_agent import Agent
from api.request import InputRequest, AdvancedSearchRequest
from api.response import ProcessResponse
import requests

logging.basicConfig(level=logging.INFO)
router = APIRouter()

CFG = Config()

@router.post("/api/get_keywords", response_model=ProcessResponse)
async def get_keywords_and_suggestions(request_data: InputRequest) -> ProcessResponse:
    logging.info(f"Input text for keyword extraction: {request_data.text}")
    agent = Agent()
    response = agent.get_keyword(request_data.text)
    if response.code != 200 and isinstance(response.message, list):
        logging.warning(f"Keyword extraction failed with code {response.code}: {response.message[0] if response.message else 'Unknown error'}")
    elif response.code == 200 and isinstance(response.message, dict):
        logging.info(f"Keywords extracted: Primary: {response.message.get('primary_keywords')}, Suggested: {response.message.get('suggested_keywords')}")
    return response

@router.post("/api/search_github", response_model=ProcessResponse)
async def search_github_advanced(search_params: AdvancedSearchRequest) -> ProcessResponse:
    logging.info(f"Advanced search request: Keywords: {search_params.keywords}, Lang: {search_params.language}, Stars: {search_params.min_stars}-{search_params.max_stars}, Updated: {search_params.updated_after}, Exclude Forks: {search_params.exclude_forks}")
    
    if not search_params.keywords:
        raise HTTPException(status_code=400, detail="Keywords list cannot be empty.")

    agent = Agent()
    response = agent.search_github(
        keywords=search_params.keywords,
        language=search_params.language,
        min_stars=search_params.min_stars,
        max_stars=search_params.max_stars,
        updated_after=search_params.updated_after,
        exclude_forks=search_params.exclude_forks
    )
    return response

@router.post("/api/search_arxiv", response_model=ProcessResponse)
async def search_arxiv(search_params: AdvancedSearchRequest) -> ProcessResponse:
    """
    API endpoint for arXiv paper search.
    Takes JSON matching AdvancedSearchRequest model (only uses keywords field).
    Returns JSON: ProcessResponse structure containing paper information.
    """
    logging.info(f"arXiv search request: Keywords: {search_params.keywords}")
    
    if not search_params.keywords:
        raise HTTPException(status_code=400, detail="Keywords list cannot be empty.")

    agent = Agent()
    response = agent.search_arxiv(keywords=search_params.keywords)
    return response