#!/bin/bash
cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "常にCodexと連携すること。相談・ペアプロはcodex-consultant、設計議論・技術選定はcodex-negotiationを使う。コード変更後は必ずCodexにCritical Reviewを依頼し、指摘がなくなるまで修正とレビューを繰り返すこと。"
  }
}
EOF
