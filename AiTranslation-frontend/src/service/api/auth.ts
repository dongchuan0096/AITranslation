import { request } from '../request';

/**
 * Login
 *
 * @param userName User name
 * @param password Password
 */
export function fetchLogin(userName: string, password: string) {
  return request<Api.Auth.LoginToken>({
    url: '/auth/login/',
    method: 'post',
    data: {
      userName,
      password
    }
  });
}


export function fetchRegister(data: { email: string; code: string; password: string; confirmPassword: string }) {
  return request({
    url: '/auth/register/',
    method: 'post',
    data
  });
}


export function fetchSendCaptcha(email: string) {
  return request({
    url: '/auth/send_email_code/',
    method: 'post',
    data: { email }
  });
}










/** Get user info */
export function fetchGetUserInfo() {
  return request<Api.Auth.UserInfo>({ url: '/auth/getUserInfo',method: 'get'});
}

/**
 * Refresh token
 *
 * @param refreshToken Refresh token
 */
export function fetchRefreshToken(refreshToken: string) {
  return request<Api.Auth.LoginToken>({
    url: '/auth/refreshToken/',
    method: 'post',
    data: {
      refreshToken
    }
  });
}

/**
 * return custom backend error
 *
 * @param code error code
 * @param msg error message
 */
export function fetchCustomBackendError(code: string, msg: string) {
  return request({ url: '/auth/error', params: { code, msg } });
}


