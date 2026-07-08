# Validation Notes

Before distribution, run:

```bash
python3 -m json.tool .claude-plugin/plugin.json >/dev/null
python3 -m json.tool hooks/hooks.json >/dev/null
python3 scripts/trace-hook.py session-start <<<'{}'
```

If Claude Code is available:

```bash
claude plugin validate /path/to/relational-design-plugin
```

The packaged zip has been checked for JSON syntax and executable script presence, but has not been executed inside a live Claude Code session in this environment.
