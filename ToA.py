from typing import List, Dict, Any
from scipy.spatial.distance import jensenshannon
from sklearn.feature_extraction.text import TfidfVectorizer

class Tree:
    """
    Tree储存历史行动
    """
    def __init__(self):
        self.tree = {}
        self.tfidf_vec = TfidfVectorizer()
    
    def expand_node(self, state: str, actions: List[str]):
        self.tree[state] = {action: None for action in actions}
    
    def update_tree(self, state: str, action: str, result: str):
        if state in self.tree and action in self.tree[state]:
            self.tree[state][action] = result
    
    # def get_best_action(self, state: str) -> str:
    #     if state in self.tree:
    #         return max(self.tree[state], key=lambda a: len(self.tree[state][a] or ""))
    #     return ""

    def select_action(self, actions: List[str]):
        if not actions:
            return None

        # 提取所有 plugin_return 并进行拼接
        all_returns = [action["plugin_return"] for action in actions]
        
        if len(all_returns) == 1:
            return actions[0]  # 只有一个 action，直接返回
        
        # 将除了最后一个 action 之外的所有 plugin_return 拼接
        first_part = " ".join(all_returns[:-1])
        # 仅使用最后一个 action 的 plugin_return
        last_part = all_returns[-1]

        # 计算 TF-IDF 向量
        tfidf_matrix = self.tfidf_vec.fit_transform([first_part, last_part])

        # 计算 JS 散度作为信息增益的衡量
        p, q = tfidf_matrix.toarray()
        js_div = jensenshannon(p, q)

        return {
            "first_part": first_part,
            "last_part": last_part,
            "information_gain": js_div
        }