export const mockReview = {
  contract_type: 'housing_lease',
  contract_type_name: '房屋租赁合同',
  contract_confidence: 0.95,
  summary: '这是一份住宅房屋租赁合同，约定了租赁期限、租金、押金、提前解除和维修责任等事项。',
  overall_risk: 'high',
  risks: [
    {
      risk_id: 'R001',
      category: 'termination',
      title: '承租人提前解除合同责任可能过重',
      risk_level: 'high',
      original_text: '乙方提前退租的，押金不予退还，并应支付剩余租期全部租金。',
      reason: '该条款可能导致承租人承担明显较重的违约责任，且没有区分违约情形、通知期限和房屋再次出租后的损失范围。',
      evidence: [
        {
          source_name: '相关法律或示范合同',
          source_type: 'law',
          content: '相关依据摘要',
          relevance: 0.91,
        },
      ],
      suggestion: '建议重新约定提前解约通知期限以及合理的违约责任范围，避免“一刀切”要求支付剩余租期全部租金。',
      recommended_clause: '乙方需要提前解除合同的，应提前 30 日通知甲方，并按照双方约定承担相应违约责任；甲方应采取合理措施减少损失。',
      confidence: 0.88,
    },
    {
      risk_id: 'R002',
      category: 'deposit',
      title: '押金退还条件不够明确',
      risk_level: 'medium',
      original_text: '乙方支付押金人民币 8000 元。',
      reason: '合同仅写明押金金额，未明确退还时间、扣除条件和结算流程，后续容易产生争议。',
      evidence: [
        {
          source_name: '住房租赁合同常见条款',
          source_type: 'template',
          content: '押金条款通常需明确退还时间、扣除范围和交接条件。',
          relevance: 0.86,
        },
      ],
      suggestion: '补充押金退还时间、可扣除费用范围，以及房屋交还后的验收流程。',
      recommended_clause: '租赁期满或合同解除后，乙方结清应付费用并完成房屋交接的，甲方应在 7 日内无息退还剩余押金。',
      confidence: 0.84,
    },
    {
      risk_id: 'R003',
      category: 'payment',
      title: '租金支付节点约定较清晰',
      risk_level: 'low',
      original_text: '月租金为人民币 8000 元，乙方应于每月 5 日前支付当月租金。',
      reason: '该条款明确了租金金额和付款时间，基础履行规则较清楚。',
      evidence: [
        {
          source_name: '合同文本自身',
          source_type: 'contract',
          content: '租金金额与付款周期已经在同一条款中载明。',
          relevance: 0.8,
        },
      ],
      suggestion: '可以进一步补充收款账户和逾期支付处理方式。',
      recommended_clause: '乙方应于每月 5 日前向甲方指定账户支付当月租金，具体账户以双方书面确认信息为准。',
      confidence: 0.79,
    },
  ],
  missing_items: [
    {
      category: 'repair',
      title: '维修责任约定不明确',
      risk_level: 'medium',
      reason: '合同未明确正常损耗、房屋主体、家电设施及人为损坏分别由哪一方承担维修责任。',
    },
  ],
  conflicts: [
    {
      title: '租赁期限存在潜在冲突',
      location_a: '第二条',
      text_a: '租赁期限自 2026 年 9 月 1 日起至 2027 年 8 月 31 日止。',
      location_b: '补充约定',
      text_b: '乙方最低租赁期限为两年。',
      risk_level: 'high',
    },
  ],
  positive_findings: [
    '租金金额及支付周期约定较明确',
    '房屋地址和用途信息已经在合同中载明',
  ],
  review_summary: '本合同存在部分需要重点关注的风险条款，尤其是提前退租责任、押金退还和维修责任约定。建议在签署前补充关键条款并调整明显偏重的违约责任。',
}
