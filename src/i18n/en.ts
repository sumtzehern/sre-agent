const en = {
  // Header
  "app.title": "Verified RCA Agent",
  "app.subtitle": "Evidence-grounded root-cause analysis, powered by Apodex",

  // Empty state
  "empty.title": "Verified RCA Agent",
  "empty.hint": "Paste in an incident plus its evidence and I'll investigate step by step — every conclusion cites a specific EVIDENCE-ID, never assumed.",
  "empty.features": "Apodex Deep Solve · Evidence Citations · Auditable Reasoning Chain",

  // Chat input
  "chat.placeholder": "Paste an incident + evidence...  ⏎ Send · Shift+⏎ Newline",
  "chat.hint": "Powered by Apodex + EdgeOne Makers · Demo only",

  // Preset
  "preset.incident": "Load CDN incident: dropped query params after Akamai→EdgeOne migration",

  // Status & errors
  "status.error": "Request failed. Please check if the backend service is running.",
  "status.stopped": "⏹ *Generation stopped*",
  "status.backendError": "Backend abort request failed. The server may still be running.",

  // Debug panel
  "debug.title": "Trace",
  "debug.events": "events",
  "debug.clear": "Clear",
  "debug.empty": "Waiting for SSE events...",
  "debug.emptyHint": "After sending a message, all raw backend data will be displayed here.",

  // Reasoning chain panel
  "reasoning.title": "Reasoning Chain",
  "reasoning.steps": "steps",
  "reasoning.step": "Step",
  "reasoning.hypothesis": "Hypothesis",
  "reasoning.evidence": "Evidence checked",
  "reasoning.conclusion": "Conclusion",
  "reasoning.empty": "No verified reasoning chain yet.",
  "reasoning.emptyHint": "Paste an incident with labeled EVIDENCE blocks to see an auditable, citation-backed RCA here.",

  // Conversation sidebar
  "sidebar.label": "Conversation list",
  "sidebar.title": "Chats",
  "sidebar.newChat": "New chat",
  "sidebar.loading": "Loading conversations...",
  "sidebar.loadMore": "Load more",
  "sidebar.loadingMore": "Loading...",
  "sidebar.emptyTitle": "No conversations yet",
  "sidebar.emptyHint": "Click \"New chat\" to start your first conversation.",
  "sidebar.delete": "Delete conversation",
  "sidebar.deleteConfirm": "Permanently delete this conversation? This cannot be undone.",

  // Aria labels (button hover/screen-reader)
  "aria.send": "Send",
  "aria.clearHistory": "Clear history",
  "aria.stopGeneration": "Stop generation",

  // Language toggle
  "lang.switch": "中文",

  // ─── Floating bottom-right action badges ─────────────────────────────
  "floatingLink.deploy": "Deploy",
  "floatingLink.github": "GitHub",
} as const;

export default en;
