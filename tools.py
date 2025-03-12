import os
import json
import requests
from urllib import response
from API_KETS import *

class Tools:
    def __init__(self) -> None:
        self.toolConfig = self._tools()
    
    def _tools(self):
        tools = [
            {
                "name_for_human": "google_search",  # 谷歌搜索
                "name_for_model": "google_search",
                "description_for_model": "Google Search is a general-purpose search engine that can be used to access the internet, look up encyclopedic knowledge, and stay informed about current events.",
                "parameters": [
                    {
                        "name": "search_query",
                        "description": "Search for a keyword or phrase",
                        "schema": {"type": "string"},
                    }
                ],
            },
            {
                "name_for_human": "github_get_user_info",  # 访问github api获取用户信息
                "name_for_model": "github_get_user_info",
                "description_for_model": "You can access user information via github_get_user_info.You can access user information via github_get_user_info. This includes the warehouse owned by the user, the followers of the user, and the following of the user.",
                "parameters": [
                    {
                        "name": "user_info",
                        "description": "Get user information",
                        "schema": {"username": "string"}
                    }
                ]
            },
            {
                "name_for_human": "github_get_repo_info",  # 访问github api获取仓库信息
                "name_for_model": "github_get_repo_info",
                "description_for_model": "You can access the repository information using github_get_repo_info.Including the repository's ID, name, owner, URL, description, primary programming language, and more.",
                "parameters": [
                    {
                        "name": "repo_info",
                        "description": "Get repo information",
                        "schema": {"owner": "string", "repo_name": "string"}
                    }
                ]
            },
            {
                "name_for_human": "github_get_repo_info",  # 访问github api获取用户信息
                "name_for_model": "github_get_repo_info",
                "description_for_model": "You can access the repository information using github_get_repo_info.Including the repository's ID, name, owner, URL, description, primary programming language, and more.",
                "parameters": [
                    {
                        "name": "repo_info",
                        "description": "Get repo information",
                        "schema": {"owner": "string", "repo_name": "string"}
                    }
                ]
            },
            {
                "name_for_human": "get_local_repo_code",  # 访问下载到本地的github仓库代码
                "name_for_model": "get_local_repo_code",
                "description_for_model": "You can access the downloaded local code files using get_local_repo_code. You need to provide the file path, and you will receive the file's text content as the output.",
                "parameters": [
                    {
                        "name": "get_local_code",
                        "description": "Get local code",
                        "schema": {"code_path": "string"}
                    }
                ]
            }
        ]

        return tools

    def google_search(self, search_query: str):
        """ 调用谷歌搜索 """
        # print("调用了google_search")
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": search_query})
        headers = {
            'X-API-KEY': X_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload).json()
        if response.status_code == 200:
            return response['organic'][0]['snippet']
        else:
            return f"ERROR:调用谷歌搜索失败,状态码:{response.status_code}"
    
    def github_get_user_info(self, username: str):
        """ 访问GitHub API获取用户信息 """
        # print(f"调用了github_get_user_info,用户名:{username}")
        url = f"https://api.github.com/users/{username}"
        headers = {
            "Authorization": GITHUB_API_KEY,
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            return {
                "login": user_data.get("login"),
                "id": user_data.get("id"),
                "name": user_data.get("name"),
                "company": user_data.get("company"),
                "blog": user_data.get("blog"),
                "location": user_data.get("location"),
                "email": user_data.get("email"),
                "bio": user_data.get("bio"),
                "public_repos": user_data.get("public_repos"),
                "followers": user_data.get("followers"),
                "following": user_data.get("following"),
                "created_at": user_data.get("created_at"),
                "updated_at": user_data.get("updated_at"),
                "avatar_url": user_data.get("avatar_url"),
                "html_url": user_data.get("html_url")
            }
        else:
            return f"ERROR:无法获取用户信息,状态码:{response.status_code}"
    
    def github_get_repo_info(self, owner: str, repo_name:str):
        """ 访问GitHub API获取仓库信息 """
        url = f"https://api.github.com/repos/{owner}/{repo_name}"
        headers = {
            "Authorization": GITHUB_API_KEY,
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            repo_data = response.json()
            return {
                "id": repo_data.get("id"),
                "name": repo_data.get("name"),
                "full_name": repo_data.get("full_name"),
                "owner": repo_data["owner"]["login"],
                "html_url": repo_data.get("html_url"),
                "description": repo_data.get("description"),
                "language": repo_data.get("language"),
                "stargazers_count": repo_data.get("stargazers_count"),
                "forks_count": repo_data.get("forks_count"),
                "open_issues_count": repo_data.get("open_issues_count"),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "license": repo_data["license"]["name"] if repo_data.get("license") else "No License"
            }
        else:
            return f"ERROR:无法获取仓库信息,状态码:{response.status_code}"

    def get_local_repo_code(self, code_path: str):
        """ 通过Linux命令访问本地代码文件,返回文本内容 """
        if not os.path.exists(code_path):
            return {"error": "文件路径不存在"}
        
        try:
            # 使用 Linux cat 命令读取文件内容
            command = f"cat {code_path}"
            file_content = os.popen(command).read()
            
            if not file_content:
                return f"ERROR:文件为空或无法读取"
            
            return {"file_content": file_content}
        except Exception as e:
            return f"ERROR:读取文件出错: {str(e)}"

if __name__ == "__main__":
    tool = Tools()