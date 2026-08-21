import { apiRequest } from './request'

export async function getAdminOverview() {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    throw new Error('登录状态已失效，请重新登录')
  }

  const response = await apiRequest({
    url: '/admin/overview',
    type: 'GET',
    data: { user_id: userId },
  })

  return {
    ...response,
    data: response.data || null,
  }
}
