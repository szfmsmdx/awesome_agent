from llm.llm_agent import Agent
from utils.parse import BaseOutputParser

if __name__ == "__main__":
    agent = Agent()
    res = agent.get_keyword("人工智能技术正在改变医疗行业的诊断方式，深度学习和计算机视觉在医学影像识别中发挥着越来越重要的作用。")
    print(res)    
