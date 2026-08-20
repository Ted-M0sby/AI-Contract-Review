import $ from 'jquery'

const DEFAULT_API_BASE_URL = import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8888'
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '')
const API_TIMEOUT = 900000

function getValidationMessage(detail) {
  if (typeof detail === 'string') {
    return detail
  }

  if (!Array.isArray(detail)) {
    return ''
  }

  return detail.map((item) => item.msg).filter(Boolean).join('；')
}

export function apiRequest(options) {
  return new Promise((resolve, reject) => {
    $.ajax({
      timeout: API_TIMEOUT,
      dataType: 'json',
      ...options,
      url: `${API_BASE_URL}${options.url}`,
      success(response) {
        if (response?.code != null && Number(response.code) !== 200) {
          reject(new Error(response.message || '请求失败，请稍后重试'))
          return
        }

        resolve(response)
      },
      error(xhr, textStatus) {
        const response = xhr.responseJSON
        const message = response?.message
          || getValidationMessage(response?.detail)
          || (textStatus === 'timeout' ? '请求超时，请检查后端服务' : '')
          || (xhr.status ? `请求失败（${xhr.status}）` : '无法连接后端服务')

        reject(new Error(message))
      },
    })
  })
}

export { API_BASE_URL }
