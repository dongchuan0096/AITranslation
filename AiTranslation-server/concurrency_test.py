#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django应用并发测试脚本
测试多线程支持能力
"""

import requests
import threading
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# 配置
BASE_URL = "http://localhost:8000"
TEST_ENDPOINTS = [
    "/api/file-upload/info/",  # 文件上传信息
    "/api/speech-recognition-info/",  # 语音识别信息
    "/admin/",  # 管理后台
]

# 测试配置
CONCURRENT_REQUESTS = 10  # 并发请求数
TOTAL_REQUESTS = 100  # 总请求数
REQUEST_TIMEOUT = 30  # 请求超时时间

class ConcurrencyTester:
    def __init__(self, base_url, endpoints):
        self.base_url = base_url
        self.endpoints = endpoints
        self.results = []
        self.lock = threading.Lock()
    
    def make_request(self, endpoint, request_id):
        """发送单个请求"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            end_time = time.time()
            
            result = {
                'request_id': request_id,
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200,
                'error': None
            }
            
        except requests.exceptions.Timeout:
            end_time = time.time()
            result = {
                'request_id': request_id,
                'endpoint': endpoint,
                'status_code': None,
                'response_time': end_time - start_time,
                'success': False,
                'error': 'Timeout'
            }
            
        except Exception as e:
            end_time = time.time()
            result = {
                'request_id': request_id,
                'endpoint': endpoint,
                'status_code': None,
                'response_time': end_time - start_time,
                'success': False,
                'error': str(e)
            }
        
        # 线程安全地添加结果
        with self.lock:
            self.results.append(result)
        
        return result
    
    def test_concurrent_requests(self, concurrent_requests, total_requests):
        """测试并发请求"""
        print(f"开始并发测试: {concurrent_requests} 并发, {total_requests} 总请求")
        print("=" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            # 提交所有任务
            futures = []
            for i in range(total_requests):
                endpoint = self.endpoints[i % len(self.endpoints)]
                future = executor.submit(self.make_request, endpoint, i + 1)
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result['success']:
                        print(f"✅ 请求 {result['request_id']:3d} 成功 - {result['endpoint']} ({result['response_time']:.3f}s)")
                    else:
                        print(f"❌ 请求 {result['request_id']:3d} 失败 - {result['endpoint']} ({result['error']})")
                except Exception as e:
                    print(f"❌ 请求异常: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return self.analyze_results(total_time)
    
    def analyze_results(self, total_time):
        """分析测试结果"""
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = median_response_time = 0
        
        success_rate = len(successful_requests) / len(self.results) * 100
        requests_per_second = len(self.results) / total_time
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': success_rate,
            'total_time': total_time,
            'requests_per_second': requests_per_second,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'median_response_time': median_response_time,
            'failed_errors': [r['error'] for r in failed_requests if r['error']]
        }
    
    def print_results(self, results):
        """打印测试结果"""
        print("\n" + "=" * 60)
        print("📊 并发测试结果")
        print("=" * 60)
        print(f"总请求数: {results['total_requests']}")
        print(f"成功请求: {results['successful_requests']}")
        print(f"失败请求: {results['failed_requests']}")
        print(f"成功率: {results['success_rate']:.2f}%")
        print(f"总耗时: {results['total_time']:.3f}秒")
        print(f"每秒请求数: {results['requests_per_second']:.2f} req/s")
        print(f"平均响应时间: {results['avg_response_time']:.3f}秒")
        print(f"最小响应时间: {results['min_response_time']:.3f}秒")
        print(f"最大响应时间: {results['max_response_time']:.3f}秒")
        print(f"中位数响应时间: {results['median_response_time']:.3f}秒")
        
        if results['failed_errors']:
            print(f"\n失败原因统计:")
            error_counts = {}
            for error in results['failed_errors']:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"  {error}: {count}次")

def test_different_concurrency_levels():
    """测试不同并发级别"""
    tester = ConcurrencyTester(BASE_URL, TEST_ENDPOINTS)
    
    concurrency_levels = [1, 5, 10, 20, 50]
    results_summary = []
    
    for concurrent_requests in concurrency_levels:
        print(f"\n🔍 测试并发级别: {concurrent_requests}")
        print("-" * 40)
        
        # 重置结果
        tester.results = []
        
        # 执行测试
        results = tester.test_concurrent_requests(concurrent_requests, TOTAL_REQUESTS)
        tester.print_results(results)
        
        results_summary.append({
            'concurrent_requests': concurrent_requests,
            'success_rate': results['success_rate'],
            'requests_per_second': results['requests_per_second'],
            'avg_response_time': results['avg_response_time']
        })
    
    # 打印总结
    print("\n" + "=" * 60)
    print("📈 并发性能总结")
    print("=" * 60)
    print(f"{'并发数':<8} {'成功率':<8} {'QPS':<8} {'平均响应时间':<12}")
    print("-" * 40)
    
    for summary in results_summary:
        print(f"{summary['concurrent_requests']:<8} "
              f"{summary['success_rate']:<8.1f}% "
              f"{summary['requests_per_second']:<8.1f} "
              f"{summary['avg_response_time']:<12.3f}s")

def main():
    """主函数"""
    print("🚀 Django应用并发测试")
    print("=" * 60)
    print(f"目标服务器: {BASE_URL}")
    print(f"测试端点: {TEST_ENDPOINTS}")
    print(f"总请求数: {TOTAL_REQUESTS}")
    print(f"默认并发数: {CONCURRENT_REQUESTS}")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
        else:
            print(f"⚠️  服务器响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保Django服务器正在运行: python manage.py runserver")
        return
    
    # 执行并发测试
    test_different_concurrency_levels()

if __name__ == "__main__":
    main() 