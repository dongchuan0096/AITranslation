from django.utils.deprecation import MiddlewareMixin

class PrintRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(f"收到请求: {request.method} {request.path}")
        # 只打印有 body 的请求
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # 检查是否是文件上传请求
                if hasattr(request, 'FILES') and request.FILES:
                    print(f"文件上传请求: {len(request.FILES)} 个文件")
                    for field_name, uploaded_file in request.FILES.items():
                        print(f"  - {field_name}: {uploaded_file.name} ({uploaded_file.size} 字节)")
                else:
                    # 尝试读取请求体内容
                    body = request.body
                    if body:
                        # 尝试UTF-8解码，如果失败则显示为二进制数据
                        try:
                            body_text = body.decode('utf-8')
                            print(f"请求体内容: {body_text[:500]}...")
                        except UnicodeDecodeError:
                            print(f"请求体内容: [二进制数据，{len(body)} 字节]")
                    else:
                        print("请求体内容: 空")
            except Exception as e:
                print(f"请求体内容读取失败: {e}")
        return None

    def process_response(self, request, response):
        # 打印响应内容（只打印前500字符，防止内容过大）
        try:
            if hasattr(response, 'content'):
                content = response.content
                if content:
                    try:
                        content_text = content.decode('utf-8')
                        print(f"返回内容: {content_text[:500]}...")
                    except UnicodeDecodeError:
                        print(f"返回内容: [二进制数据，{len(content)} 字节]")
                else:
                    print("返回内容: 空")
        except Exception as e:
            print(f"返回内容读取失败: {e}")
        return response 