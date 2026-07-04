#!/bin/sh
# PCE 3.0: no canonical change without a Warrant.
# PreToolUse guard on Bash. If the command performs a canonical change
# (git commit / push / merge), ask the operator to confirm a Warrant exists.
# On any other command, stay silent and allow it.

input=$(cat)

case "$input" in
  *"git "*commit* | *"git "*push* | *"git "*merge*)
    cat <<'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "PCE: this is a canonical change. Confirm the Warrant before proceeding -- goal fit / scope compliance / evidence / authority / risk acceptance / recoverability / freshness. If there is no Warrant, stop."
  }
}
JSON
    ;;
esac

exit 0
