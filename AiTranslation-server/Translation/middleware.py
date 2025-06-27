from django.utils.deprecation import MiddlewareMixin

class PrintRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(f"收到请求: {request.method} {request.path}")
        # 只打印有 body 的请求
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # 打印原始body内容
                body = request.body.decode('utf-8')
                print(f"请求体内容: {body}")
            except Exception as e:
                print(f"请求体内容读取失败: {e}")
        return None

    def process_response(self, request, response):
        # 打印响应内容（只打印前500字符，防止内容过大）
        try:
            content = response.content.decode('utf-8')
            print(f"返回内容: {content[:500]}")
        except Exception as e:
            print(f"返回内容读取失败: {e}")
        return response 