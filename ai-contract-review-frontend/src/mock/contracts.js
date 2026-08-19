const STORAGE_KEY = 'demo_contracts'

export const mockContractText = `甲方（出租人）：张某
乙方（承租人）：李某

第一条 房屋基本情况
甲方将位于北京市朝阳区示例小区 1 号楼 1001 室的住宅出租给乙方居住使用。

第二条 租赁期限
租赁期限自 2026 年 9 月 1 日起至 2027 年 8 月 31 日止。

第三条 租金及押金
月租金为人民币 8000 元，乙方应于每月 5 日前支付当月租金。乙方支付押金人民币 8000 元。

第四条 提前解除
乙方提前退租的，押金不予退还，并应支付剩余租期全部租金。

第五条 房屋维修
租赁期间房屋及附属设施出现损坏的，由双方另行协商处理。`

export const defaultContracts = [
  {
    id: 1,
    title: '北京市住房租赁合同',
    contract_type: 'housing_lease',
    contract_type_name: '房屋租赁合同',
    created_at: '2026-08-19 15:00',
    status: 'reviewed',
    overall_risk: 'high',
    content: mockContractText,
  },
  {
    id: 2,
    title: '测试租赁合同',
    contract_type: 'housing_lease',
    contract_type_name: '房屋租赁合同',
    created_at: '2026-08-19 15:30',
    status: 'pending',
    overall_risk: null,
    content: mockContractText,
  },
]

export function readContracts() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (!saved) {
    writeContracts(defaultContracts)
    return defaultContracts
  }

  try {
    return JSON.parse(saved)
  } catch {
    writeContracts(defaultContracts)
    return defaultContracts
  }
}

export function writeContracts(contracts) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(contracts))
}

export function upsertContract(contract) {
  const contracts = readContracts()
  const index = contracts.findIndex((item) => Number(item.id) === Number(contract.id))

  if (index >= 0) {
    contracts.splice(index, 1, { ...contracts[index], ...contract })
  } else {
    contracts.unshift(contract)
  }

  writeContracts(contracts)
  return contract
}

export function createContract({ id = Date.now(), title, contract_type, fileName }) {
  const contract = {
    id,
    title,
    contract_type,
    contract_type_name: '房屋租赁合同',
    created_at: new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).replace(/\//g, '-'),
    status: 'pending',
    overall_risk: null,
    file_name: fileName,
    content: mockContractText,
  }

  return upsertContract(contract)
}
