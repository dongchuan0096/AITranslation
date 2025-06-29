#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件上传功能测试脚本
"""

import requests
import json
import os
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
TOKEN = "your_jwt_token_here"  # 请替换为实际的JWT token

def test_file_upload_info():
    """测试获取文件上传配置信息"""
    print("=== 测试获取文件上传配置信息 ===")
    
    url = f"{BASE_URL}/api/file-upload/info/"
    response = requests.get(url)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_file_upload():
    """测试文件上传"""
    print("=== 测试文件上传 ===")
    
    # 创建一个测试文件
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("这是一个测试文件，用于测试文件上传功能。")
        f.write(f"\n创建时间: {datetime.now()}")
    
    try:
        url = f"{BASE_URL}/api/file-upload/upload/"
        
        with open(test_file_path, "rb") as f:
            files = {"file": f}
            headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN != "your_jwt_token_here" else {}
            
            response = requests.post(url, files=files, headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 文件上传成功!")
                return result["data"]["file_record_id"]
            else:
                print("❌ 文件上传失败!")
                return None
        else:
            print("❌ 请求失败!")
            return None
            
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    print()

def test_file_list():
    """测试文件列表查询"""
    print("=== 测试文件列表查询 ===")
    
    url = f"{BASE_URL}/api/file-upload/list/"
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN != "your_jwt_token_here" else {}
    params = {"page": 1, "page_size": 10}
    
    response = requests.get(url, headers=headers, params=params)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_file_detail(file_id):
    """测试文件详情查询"""
    if not file_id:
        print("❌ 没有文件ID，跳过详情查询测试")
        return
    
    print("=== 测试文件详情查询 ===")
    
    url = f"{BASE_URL}/api/file-upload/detail/{file_id}/"
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN != "your_jwt_token_here" else {}
    
    response = requests.get(url, headers=headers)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_file_statistics():
    """测试文件上传统计"""
    print("=== 测试文件上传统计 ===")
    
    url = f"{BASE_URL}/api/file-upload/statistics/"
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN != "your_jwt_token_here" else {}
    
    response = requests.get(url, headers=headers)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_file_delete(file_id):
    """测试文件删除"""
    if not file_id:
        print("❌ 没有文件ID，跳过删除测试")
        return
    
    print("=== 测试文件删除 ===")
    
    url = f"{BASE_URL}/api/file-upload/delete/{file_id}/"
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN != "your_jwt_token_here" else {}
    
    response = requests.delete(url, headers=headers)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ 文件删除成功!")
        else:
            print("❌ 文件删除失败!")
    else:
        print("❌ 请求失败!")
    
    print()

def test_batch_delete():
    """测试批量删除"""
    print("=== 测试批量删除 ===")
    
    url = f"{BASE_URL}/api/file-upload/batch-delete/"
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN != "your_jwt_token_here" else {}
    data = {"file_ids": [1, 2, 3]}  # 测试用的文件ID
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def main():
    """主函数"""
    print("🚀 开始测试文件上传功能")
    print("=" * 50)
    
    # 测试获取配置信息
    test_file_upload_info()
    
    # 测试文件上传
    file_id = test_file_upload()
    
    # 测试文件列表
    test_file_list()
    
    # 测试文件详情
    test_file_detail(file_id)
    
    # 测试文件统计
    test_file_statistics()
    
    # 测试批量删除
    test_batch_delete()
    
    # 测试文件删除
    test_file_delete(file_id)
    
    print("=" * 50)
    print("✅ 文件上传功能测试完成!")

if __name__ == "__main__":
    main() 