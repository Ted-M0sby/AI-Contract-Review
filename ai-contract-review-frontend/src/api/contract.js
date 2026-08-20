import { apiRequest } from './request'
import { createContract, readContracts, upsertContract } from '../mock/contracts'
import { mockReview } from '../mock/review'

function wait(ms = 300) {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

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
  const contract = readContracts().find((item) => String(item.id) === String(id))
  if (!contract) {
    return { code: 404, message: '合同不存在' }
  }

  upsertContract({ ...contract, status: 'reviewing' })
  await wait(2000)
  upsertContract({ ...contract, status: 'reviewed', overall_risk: mockReview.overall_risk })

  return {
    code: 200,
    data: mockReview,
  }
}

export async function getReview(id) {
  await wait()
  const contract = readContracts().find((item) => String(item.id) === String(id))
  return {
    code: contract ? 200 : 404,
    data: contract ? mockReview : null,
  }
}
