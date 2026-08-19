import { apiRequest } from './request'

function postJson(url, data) {
  return apiRequest({
    url,
    type: 'POST',
    contentType: 'application/json; charset=UTF-8',
    data: JSON.stringify(data),
  })
}

export function sendCode({ email }) {
  return postJson('/auth/send-code', { email })
}

export function register({ email, password, code }) {
  return postJson('/auth/register', { email, password, code })
}

export function login({ email, password }) {
  return postJson('/auth/login', { email, password })
}
