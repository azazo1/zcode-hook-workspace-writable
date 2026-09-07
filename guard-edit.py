#!/usr/bin/env python3
"""PreToolUse 钩子: 按项目边界放行文件编辑.

Write/Edit 的目标文件在当前项目内则返回 allow 免询问; 项目之外不拦截,
交回默认权限流程由用户确认.
项目目录取自第一个命令行参数 (安装时传入 ZCODE_PROJECT_DIR), 缺省回退到事件 cwd.
"""

import json
import os
import sys


def emit_allow(tool_input: dict) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": tool_input,
        }
    }))


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(data, dict):
        return
    tool_input = dict(data.get("tool_input") or {})
    path = str(tool_input.get("file_path", "")).strip()
    if not path:
        return
    workspace = (sys.argv[1] if len(sys.argv) > 1 else "") or str(data.get("cwd") or os.getcwd())
    if not workspace or not os.path.isdir(workspace):
        return
    candidate = os.path.expanduser(path)
    if not os.path.isabs(candidate):
        candidate = os.path.join(workspace, candidate)
    real = os.path.realpath(candidate)
    root = os.path.realpath(workspace)
    if ".git" in real.split(os.sep):
        return
    if real == root or real.startswith(root + os.sep):
        emit_allow(tool_input)


if __name__ == "__main__":
    main()
