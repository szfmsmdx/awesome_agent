from typing import List
from fastapi import APIRouter, Body, Request
import logging
from config import Config
from llm.llm_agent import Agent
from api.request import InputRequest
from api.response import ProcessResponse

logging.basicConfig(level=logging.INFO)
router = APIRouter()

CFG = Config()

@router.post("/api/get_keywords")
async def get_keywords(request1: Request, request:InputRequest) -> ProcessResponse:
    logging.info(f"输入文本: {request.text}")
    agent = Agent()
    response = agent.get_keyword(request.text)
    return response