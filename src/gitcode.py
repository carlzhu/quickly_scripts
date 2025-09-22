#!/usr/bin/env python3
import requests
import os
import subprocess
from pathlib import Path

# GitLab服务器地址和Token配置
gitlab_url = "http://192.168.1.132:9090"
token = "V18-yvszx68xMvY7RYtv"

# 基础目录
base_dir = "D:\\dev\\code\\gw"

def git_clone_or_pull(repo_url, project_path):
    """克隆新仓库或更新已存在的仓库"""
    full_path = os.path.join(base_dir, project_path)
    
    try:
        if not os.path.exists(full_path):
            # 创建目录（如果需要）
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            print(f"克隆仓库: {project_path}")
            # 使用token进行克隆
            clone_url = repo_url.replace('http://', f'http://oauth2:{token}@')
            subprocess.run(['git', 'clone', clone_url, full_path], check=True)
        else:
            print(f"更新仓库: {project_path}")
            # 更新已存在的仓库
            subprocess.run(['git', 'fetch'], cwd=full_path, check=True)
            subprocess.run(['git', 'pull'], cwd=full_path, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {project_path} - {str(e)}")
        return False

# 设置请求头
headers = {
    'PRIVATE-TOKEN': token
}

# 存储所有项目
all_projects = []
page = 1
per_page = 100

print(f"正在连接到 GitLab 服务器: {gitlab_url}")

while True:
    # 获取当前页的项目列表
    response = requests.get(
        f"{gitlab_url}/api/v4/projects",
        headers=headers,
        params={
            'page': page,
            'per_page': per_page
        }
    )
    
    if response.status_code != 200:
        print(f"获取项目列表失败，状态码：{response.status_code}")
        print(f"错误信息：{response.text}")
        break
        
    projects = response.json()
    if not projects:  # 如果没有更多项目了
        break
        
    all_projects.extend(projects)
    page += 1

print(f"\n总共找到 {len(all_projects)} 个项目：\n")

success_count = 0
fail_count = 0

for i, project in enumerate(all_projects, 1):
    print(f"\n{i}. 项目名称: {project['name']}")
    print(f"   项目路径: {project['path_with_namespace']}")
    print(f"   克隆地址: {project['http_url_to_repo']}")
    print(f"   创建时间: {project['created_at']}")
    
    # 克隆或更新仓库
    if git_clone_or_pull(project['http_url_to_repo'], project['path_with_namespace']):
        success_count += 1
    else:
        fail_count += 1
    
    print("   " + "-"*50)

print(f"\n操作完成！成功: {success_count}, 失败: {fail_count}")
