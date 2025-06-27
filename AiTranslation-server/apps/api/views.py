from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.utils.response import APIResponse

#spark接口
SPARK_API_HOST = "127.0.0.1:5000"

class TextTranslateView(APIView):
    def post(self, request):
        # 直接将收到的参数转发到本地后端的 /api/spark/text-translate
        spark_url = f"http://{SPARK_API_HOST}/api/text-translate"
        try:
            resp = requests.post(spark_url, json=request.data, timeout=100)
            return Response(resp.json(), status=resp.status_code)
        except Exception as e:
            return APIResponse.fail(msg=f"Spark接口调用异常: {str(e)}", code="4003")
