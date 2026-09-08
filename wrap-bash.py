#!/usr/bin/env python3
"""PreToolUse 钩子: 把 Bash 命令包进 Seatbelt workspace-write 沙箱并自动放行.

输入 (stdin): ZCode 钩子事件 JSON, 含 tool_name 和 tool_input.
输出 (stdout): 带 updatedInput 的 allow 决定, 让命令免询问直接执行.
以下两种情况不拦截, 交回默认权限流程: 模型显式请求提权 (dangerouslyDisableSandbox);
命中敏感命令模式 (sudo/ssh 族).
"""

import json
import os
import re
import shlex
import sys

PROFILE = os.path.expanduser("~/.zcode/hooks/workspace-write.sb")

SENSITIVE = re.compile(r"(^|[;&|]\s*)(sudo|ssh|scp|sftp|rsync|ssh-copy-id)\b", re.MULTILINE)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(data, dict) or data.get("tool_name") != "Bash":
        return
    tool_input = dict(data.get("tool_input") or {})
    command = str(tool_input.get("command", ""))
    if not command.strip():
        return
    if tool_input.get("dangerouslyDisableSandbox"):
        return
    if SENSITIVE.search(command):
        return
    workspace = data.get("cwd") or os.getcwd()
    tool_input["command"] = "sandbox-exec -f {} -D WORKSPACE={} sh -c {}".format(
        shlex.quote(PROFILE), shlex.quote(workspace), shlex.quote(command)
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": tool_input,
        }
    }))


if __name__ == "__main__":
    main()
