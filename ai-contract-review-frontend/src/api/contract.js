import { apiRequest } from './request'
import { createContract, upsertContract } from '../mock/contracts'

export async function getContracts() {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    throw new Error('登录状态已失效，请重新登录')
  }

  const response = await apiRequest({
    url: '/contracts',
    type: 'GET',
    data: { user_id: userId },
  })

  const contracts = Array.isArray(response.data) ? response.data : []
  contracts.forEach((contract) => upsertContract(contract))

  return {
    ...response,
    data: contracts,
  }
}

export async function uploadContract({ title, contract_type, file }) {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    throw new Error('登录状态已失效，请重新登录')
  }

  const formData = new FormData()
  formData.append('user_id', userId)
  formData.append('title', title)
  formData.append('contract_type', contract_type)
  formData.append('file', file)

  const response = await apiRequest({
    url: '/contracts/upload',
    type: 'POST',
    data: formData,
    processData: false,
    contentType: false,
  })

  const responseData = response?.data || {}
  const contractId = response.contract_id
    ?? responseData.contract_id
    ?? responseData.id
    ?? response.id
    ?? Date.now()

  const contract = createContract({
    id: contractId,
    title,
    contract_type,
    fileName: file.name,
  })

  return {
    ...response,
    contract_id: contract.id,
    data: { ...contract, ...responseData },
  }
}

export async function getContract(id) {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    throw new Error('登录状态已失效，请重新登录')
  }

  const response = await apiRequest({
    url: `/contracts/${encodeURIComponent(id)}`,
    type: 'GET',
    data: { user_id: userId },
  })

  const contract = response.data || response.contract || null
  if (contract) {
    upsertContract(contract)
  }

  return {
    ...response,
    data: contract,
  }
}

export async function startReview(id) {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    throw new Error('登录状态已失效，请重新登录')
  }

  const response = await apiRequest({
    url: `/contracts/${encodeURIComponent(id)}/review`,
    type: 'POST',
    contentType: 'application/json; charset=UTF-8',
    data: JSON.stringify({
      user_id: Number(userId),
      review_perspective: 'neutral',
    }),
  })

  const responseData = response.data || null
  upsertContract({
    id,
    status: response.status || 'reviewed',
    overall_risk: response.overall_risk || responseData?.overall_risk || null,
  })

  return {
    ...response,
    data: responseData,
  }
}

export async function getReview(id) {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    throw new Error('登录状态已失效，请重新登录')
  }

  const response = await apiRequest({
    url: `/contracts/${encodeURIComponent(id)}/review`,
    type: 'GET',
    data: { user_id: userId },
  })

  return {
    ...response,
    data: response.data || null,
  }
}

export async function sendContractDingTalk(id) {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    throw new Error('登录状态已失效，请重新登录')
  }

  return apiRequest({
    url: `/contracts/${encodeURIComponent(id)}/dingtalk`,
    type: 'POST',
    contentType: 'application/json; charset=UTF-8',
    data: JSON.stringify({
      user_id: Number(userId),
    }),
  })
}
