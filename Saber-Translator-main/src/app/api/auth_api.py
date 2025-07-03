from flask import Blueprint, request, jsonify
import json
from src.shared.request_logger import log_request

# 创建蓝图实例
auth_bp = Blueprint('auth_api', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
@log_request
def login():
    """
    登录接口示例：不做任何 token、session 校验，前端无论带不带 token 都能访问。
    实际项目中可根据需要返回用户信息、token等，这里仅返回登录成功。
    """
    # 获取前端传递的用户名、密码等参数（可选）
    data = request.get_json() or {}
    username = data.get('username', '')
    # 这里不做任何校验，直接返回成功
    return jsonify({
        'code': '0000',
        'msg': '登录成功',
        'data': {
            'token': 'xxx',
            'refreshToken': 'yyy'
        }
    })

@auth_bp.route('/getUserInfo', methods=['GET'])
@log_request
def get_user_info():
    """
    获取用户信息接口，mock 风格返回。
    """
    return jsonify({
        "code": "0000",
        "msg": "操作成功",
        "data": {
            "userId": "10001",
            "username": "test_user",
            "nickname": "测试用户",
            "avatar": "https://cdn.apifox.cn/avatar.png",
            "email": "test_user@example.com",
            "roles": ["admin"],
            "permissions": ["read", "write", "delete"]
        }
    }) 