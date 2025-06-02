POLITICAL_KEYWORDS_EN = [
    "politics", "election", "government", "senate", "congress", "parliament",
    "president", "prime minister", "democracy", "republican", "democrat",
    "liberal", "conservative", "socialism", "communism", "revolution",
    "protest", "activism", "geopolitics", "foreign policy", "legislation",
    "ballot", "campaign", "candidate", "regime", "coup", "dictator",
    "sovereignty", "nationalism", "ideology", "propaganda", "political party",
    "state-sponsored", "censorship", "human rights violation", "political prisoner",
    "authoritarian", "totalitarian", "oppression", "political dissent",
    "insurrection", "rebellion", "separatist",
]

POLITICAL_KEYWORDS_ZH = [
    "政治", "选举", "政府", "参议院", "国会", "议会",
    "总统", "总理", "民主", "共和党", "民主党",
    "自由主义", "保守主义", "社会主义", "共产主义", "革命",
    "抗议", "激进主义", "地缘政治", "外交政策", "立法",
    "投票", "竞选", "候选人", "政权", "政变", "独裁者",
    "主权", "民族主义", "意识形态", "宣传", "政党",
    "国家支持", "审查", "人权侵犯", "政治犯",
    "威权主义", "极权主义", "压迫", "政治异议",
    "暴动", "叛乱", "分裂主义",
]

COMBINED_FILTER_KEYWORDS = [kw.lower() for kw in POLITICAL_KEYWORDS_EN] + POLITICAL_KEYWORDS_ZH

class FilterKeywords:
    def __init__(self):
        self.filter_keywords_zh = POLITICAL_KEYWORDS_ZH
        self.filter_keywords_en = POLITICAL_KEYWORDS_EN
        self.combined_filter_keywords = COMBINED_FILTER_KEYWORDS
