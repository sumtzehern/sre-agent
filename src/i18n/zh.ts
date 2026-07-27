const zh = {
  // Header
  "app.title": "可验证 RCA 智能体",
  "app.subtitle": "由 Apodex 驱动的、有据可查的根因分析",

  // Empty state
  "empty.title": "可验证 RCA 智能体",
  "empty.hint": "粘贴事件描述及其证据，我会逐步排查——每一条结论都会引用具体的 EVIDENCE-ID，绝不凭空假设。",
  "empty.features": "Apodex Deep Solve · 证据引用 · 可审计推理链",

  // Chat input
  "chat.placeholder": "粘贴事件描述与证据…  ⏎ 发送 · Shift+⏎ 换行",
  "chat.hint": "由 Apodex + EdgeOne Makers 驱动 · 仅供演示",

  // Preset
  "preset.incident": "加载 CDN 事件：Akamai→EdgeOne 迁移后查询参数丢失",

  // Status & errors
  "status.error": "⚠️ 请求失败，请检查后端服务是否启动。",
  "status.stopped": "⏹ *已停止生成*",
  "status.backendError": "⚠️ 后端中断请求失败，服务端可能仍在运行。",

  // Debug panel
  "debug.title": "传输流",
  "debug.events": "事件",
  "debug.clear": "清除",
  "debug.empty": "等待 SSE 事件...",
  "debug.emptyHint": "发送消息后，所有原始后端数据将在此处显示。",

  // Reasoning chain panel
  "reasoning.title": "推理链",
  "reasoning.steps": "步骤",
  "reasoning.step": "第",
  "reasoning.hypothesis": "假设",
  "reasoning.evidence": "已核对证据",
  "reasoning.conclusion": "结论",
  "reasoning.empty": "暂无可验证的推理链。",
  "reasoning.emptyHint": "粘贴带有标注 EVIDENCE 的事件描述，即可在此查看有据可查、可审计的根因分析。",

  // Conversation sidebar
  "sidebar.label": "会话列表",
  "sidebar.title": "会话",
  "sidebar.newChat": "新建聊天",
  "sidebar.loading": "正在加载会话...",
  "sidebar.loadMore": "加载更多",
  "sidebar.loadingMore": "加载中...",
  "sidebar.emptyTitle": "暂无会话",
  "sidebar.emptyHint": "点击「新建聊天」开始第一段对话。",
  "sidebar.delete": "删除会话",
  "sidebar.deleteConfirm": "确定要永久删除这个会话吗？此操作不可恢复。",

  // Aria labels (button hover/screen-reader)
  "aria.send": "发送",
  "aria.clearHistory": "清除历史",
  "aria.stopGeneration": "停止生成",

  // Language toggle
  "lang.switch": "English",

  // ─── Floating bottom-right action badges ─────────────────────────────
  "floatingLink.deploy": "一键部署",
  "floatingLink.github": "GitHub",
} as const;

export default zh;
