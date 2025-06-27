from rest_framework.response import Response

class APIResponse:
    @staticmethod
    def success(msg="成功", data=None, code="0000"):
        return Response({
            "code": code,
            "msg": msg,
            "data": data or {}
        })

    @staticmethod
    def fail(msg="失败", code="1000", data=None):
        return Response({
            "code": code,
            "msg": msg,
            "data": data or {}
        }) 