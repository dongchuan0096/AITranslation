from flask import request

def log_request(func):
    def wrapper(*args, **kwargs):
        print(f"\n--- 前端请求 {request.method} {request.path} ---")
        if request.method == 'GET':
            print(f"Query: {request.args}")
        else:
            try:
                print(f"Body: {request.get_json()}")
            except Exception:
                print(f"Raw data: {request.data}")
        print("-----------------------------")
        result = func(*args, **kwargs)
        # 尝试打印返回内容
        try:
            if hasattr(result, 'data'):
                print("返回内容:", result.data.decode('utf-8'))
            else:
                print("返回内容:", result)
        except Exception as e:
            print(f"返回内容打印异常: {e}")
        print("=============================\n")
        return result
    wrapper.__name__ = func.__name__
    return wrapper 