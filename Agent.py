import json5
from LLM import *
from API_KETS import *
from tools import Tools
from ToA import Tree

## 工具描述文本,与Tools中的toolConfig对应,告诉Agent某个工具的作用
TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""
## 行动prompt,调用LLM的prompt文本
REACT_PROMPT = """You have access to the following tools:
{tool_names}

The following is a description of the tools:
{tool_descs}

The dialogue that follows will contain the following:
'''
QUESTION: Questions raised by users
THOUGHT: you should always think about what to do
ACTION: The action to take must be selected from the list [{tool_names}] and no additional descriptions are allowed
ACTION INPUT: the input format for the selected tool in ACTION must follow the schema in the tool description
OBSERVATION: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
FINAL ANSWER: the final answer to the original input question
'''

After receiving the QUESTION or the previous OBSERVATION, you must perform one of the following two actions:
1. After THOUGHT, provide the chosen ACTION and simultaneously give the ACTION INPUT.
2. After THOUGHT, if you can perfectly answer the original QUESTION, then provide the FINAL ANSWER

That is to say, your answer can only be in the following format:
1.
THOUGHT: your thought
ACTION: one of [{tool_names}]
ACTION INPUT: the corresponding input, refer to the description of the tool.
2.
THOUGHT: I now know the final answer
FINAL ANSWER: the final answer to the original input question



Strictly output according to the requirements, and do not output any other content. Let's Begin!
"""

MULTI_REACT_PROMPT = """
You are an intelligent hierarchical agent operating within the HARF framework for automated README generation.
Your task is to systematically explore the software repository, analyze available information, and optimize action sequences using the Entropy Optimized Action Tree (EOAT) model.

The following tools are available to you:
{tool_names}

### Tool Descriptions:
{tool_descs}

### Decision-Making Protocol:
The dialogue that follows adheres to the structured decision-making process of the EOAT model:

'''
QUESTION: User-provided input that requires README generation.
THOUGHT: You must analyze the repository state and determine the most optimal action to take based on entropy optimization.
ACTION: The chosen action must be selected from [{tool_names}] to maximize information gain and minimize redundancy.
ACTION INPUT: Provide the input for the selected tool in accordance with the tool description schema.
OBSERVATION: The result of the executed action, updating the current repository state.

... (This Thought/Action/Action Input/Observation loop can repeat multiple times as the EOAT model expands the action tree.)

FINAL ANSWER: The final README content generated after optimal action sequences have been executed.
'''

### Execution Strategy:
Upon receiving a QUESTION or an OBSERVATION, you must perform one of the following actions:
1. Analyze the repository structure and dynamically select an optimal ACTION that maximizes entropy-based information gain.
2. If sufficient information has been collected, generate the FINAL ANSWER, ensuring comprehensive and structured README documentation.

Your response must strictly follow one of the two formats below:
1.
THOUGHT: Your reasoning based on entropy evaluation.
ACTION: One of [{tool_names}]
ACTION INPUT: The corresponding input following the tool description schema.
2.
THOUGHT: The README generation process is complete.
FINAL ANSWER: The generated README document.

### Guidelines:
- Always select actions that yield the highest information gain, following EOAT's hierarchical action expansion mechanism.
- Ensure decisions align with repository structure and the user's documentation requirements.
- Avoid redundant or low-value actions that do not contribute significantly to README generation.

Strictly output according to the requirements, and do not output any other content. Let's Begin!
"""

class Agent:
    def __init__(self, path: str) -> None:
        self.path = path
        self.tool = Tools()
        self.system_prompt = self.build_system_input()
        # self.model = GLMChat(path)
        self.model = DeepSeekChat(DEEPSEEK_API_KEY)
    
    def build_system_input(self):
        tool_descs, tool_names = [], []
        for tool in self.tool.toolConfig:
            tool_descs.append(TOOL_DESC.format(**tool))
            tool_names.append(tool["name_for_model"])
        tool_descs = "\n\n".join(tool_descs)
        tool_names = ",".join(tool_names)
        sys_prompt = REACT_PROMPT.format(tool_descs=tool_descs, tool_names=tool_names)
        return sys_prompt

    def parse_latest_plugin_call(self, text):
        plugin_name, plugin_args = '', ''
        i = text.rfind("\nACTION:")
        j = text.rfind("\nACTION INPUT:")
        k = text.rfind("\nOBSERVATION:")
        if 0 <= i < j:  # 当text中含有'ACTION'和'ACTION INPUT'时
            if k < j:  # 但是不包含'OBSERVATION'时
                text = text.rstrip() + "\nOBSERVATION:"  # 增加OBSERVATION
            k = text.rfind("\nOBSERVATION:")
            plugin_name = text[i + len('\nACTION:') : j].strip()  # 获取Action要调用的插件名称
            plugin_args = text[j + len('\nACTION INPUT') : k].strip()  # 获取对应插件的参数Action Input
            text = text[:k]
        return plugin_name, plugin_args, text
    
    def multi_plugin_call(self, text):
        """
        从 text 中检测 ACTION 以及 ACTION INPUT 的位置，
        截取其后面的文本，并且将其按照逗号 "," 分隔，变为列表并返回。
        """
        i = text.rfind("\nACTION:")
        j = text.rfind("\nACTION INPUT:")
        
        if 0 <= i < j:  # 确保 ACTION 和 ACTION INPUT 存在且顺序正确
            plugin_name_text = text[i + len('\nACTION:'):].strip()
            plugin_name_list = [arg.strip() for arg in plugin_name_text.split(',') if arg.strip()]
            plugin_args_text = text[j + len('\nACTION INPUT:'):].strip()
            plugin_args_list = [arg.strip() for arg in plugin_args_text.split(',') if arg.strip()]
            return plugin_name_list, plugin_args_list

    def call_plugin(self, plugin_name, plugin_args):
        if not isinstance(plugin_args, str):
            plugin_args = json5.loads(plugin_args)
        if plugin_name == "google_search":
            return "\nObservation:" + self.tool.google_search(**plugin_args)
        elif plugin_name == "github_get_user_info":
            return "\nObservation:" + self.tool.github_get_user_info(**plugin_args)
        elif plugin_name == "github_get_repo_info":
            return "\nObservation:" + self.tool.github_get_repo_info(**plugin_args)
        elif plugin_name == "get_local_repo_code":
            return "\nObservation:" + self.tool.get_local_repo_code(**plugin_args)
        else:
            raise ValueError

    # def text_completion(self, text, history=[]):
    #     text = self.system_prompt + "\nQuestion:" + text
    #     response, his = self.model.chat(text, history)
    #     # print("\n------Response:\n")
    #     print(response)
    #     plugin_name, plugin_args, response = self.parse_latest_plugin_call(response)
    #     if plugin_name:
    #         response += self.call_plugin(plugin_name, plugin_args)
    #     # print("\n-----第二次query:\n")
    #     # print(response)
    #     response, his = self.model.chat(response, his)
    #     return response, his

    def multi_plugin_call(self, text):
        """
        解析文本中的 ACTION 和 ACTION INPUT，
        存入 Tree 并选择最优的 ACTION 及其 INPUT。
        """
        i = text.rfind("\nACTION:")
        j = text.rfind("\nACTION INPUT:")
        
        if 0 <= i < j:
            plugin_name_text = text[i + len('\nACTION:'):].strip()
            plugin_name_list = [arg.strip() for arg in plugin_name_text.split(',') if arg.strip()]
            plugin_args_text = text[j + len('\nACTION INPUT:'):].strip()
            plugin_args_list = [arg.strip() for arg in plugin_args_text.split(',') if arg.strip()]
            
            actions = [{"plugin_name": name, "plugin_return": args} for name, args in zip(plugin_name_list, plugin_args_list)]
            best_action = self.action_tree.select_action(actions)  # 选择信息增益最高的行动
            return best_action
    
    def text_completion(self, text, history=[]):
        """ 多轮Agent对话 """

        query = self.system_prompt + "\nQUESTION: " + text
        
        while True:
            response, history = self.model.chat(query, history)
            print("\n------Response:\n", response)

            # 解析最新的行动
            best_action = self.multi_plugin_call(response)
            
            if best_action:
                plugin_name = best_action["plugin_name"]
                plugin_args = best_action["plugin_return"]
                
                # 存储到行动树
                self.action_tree.update_tree(text, plugin_name, plugin_args)
                
                observation = self.call_plugin(plugin_name, plugin_args)
                query = response + observation  # 添加最新的观察结果
                if "ERROR" == observation[:5]:  # 当遇到call_plugin 调用错误时
                    # 读取行动树上的历史行动并重新选择节点
                    previous_actions = [f"ACTION: {a}, ACTION INPUT: {self.action_tree.tree[text][a]}" for a in self.action_tree.tree.get(text, {})]
                    retry_prompt = "\nEncountered an error. Please select a previous action:\n" + "\n".join(previous_actions)
                    query = self.system_prompt + "\nQUESTION: " + text + retry_prompt
            else:
                break  # 没有新行动则退出

        return response, history