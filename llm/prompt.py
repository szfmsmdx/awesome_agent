PT_PROMPT = """
# 任务定义
你是一个关键词提取器，负责从给定的文本中提取出最重要的关键词，你需要联想领域内的相关内容，提取出相应关键词，这些关键词后续将应用于搜索引擎和内容推荐中，所以你需要确保提取的关键词具有较高的相关性和准确性。

# 生成格式
请确保只以以下格式返回结果，不要添加任何额外的文本或解释：
    ["关键词1","关键词2",...,"关键词n"]
    
# 关键词要求
    1. 关键词应为中文，且不包含任何标点符号。
    2. 关键词应为名词或名词性短语，且不包含动词、形容词、副词等其他词性。
    
# 示例
示例1：
    输入文本："人工智能技术正在改变医疗行业的诊断方式，深度学习和计算机视觉在医学影像识别中发挥着越来越重要的作用。"
    输出结果：["人工智能", "医疗行业", "深度学习", "计算机视觉", "医学影像识别"]
    
示例2：
    输入文本："新能源汽车的发展趋势日益明显，电池技术、充电设施和智能驾驶成为行业关注的焦点。"
    输出结果：["新能源汽车", "发展趋势", "电池技术", "充电设施", "智能驾驶"]
    
示例3：
    输入文本："区块链技术不仅应用于加密货币，还广泛用于供应链管理、数字身份认证等领域。"
    输出结果：["区块链技术", "加密货币", "供应链管理", "数字身份认证"]
    
# Task begin
下面，按照上述要求，认真、仔细地完成单选题生成的工作，只需要生成最终的结果即可。
输入文本: {text}
"""

GET_KEYWORDS_AND_SUGGESTIONS_PROMPT_TEMPLATE = """
给定文本，提取出最能代表主要主题的主要关键词，并建议一些用户可能也感兴趣的关联关键词。
请严格按照包含两个键的 JSON 对象格式返回结果："primary_keywords"（字符串列表）和"suggested_keywords"（字符串列表）。
确保关键词简洁且相关。不要在 JSON 对象前后包含任何其他文本。
如果你判断涉及到学术领域，请使用学术领域内的英文关键词，而不是全写。
此外，这些关键词最后被用在GitHub搜索和arxiv搜索中，所以你也需要考虑搜索的限制。

文本:
{text}

JSON 响应:
"""

class prompt:
    parse_text_prompt = PT_PROMPT
    get_keywords_and_suggestions_prompt = GET_KEYWORDS_AND_SUGGESTIONS_PROMPT_TEMPLATE