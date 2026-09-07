#!/bin/sh
# 安装 ZCode Bash 沙箱钩子: 部署 profile 与包装脚本, 并注册用户级 hooks 配置.
# 可重复执行; 仓库可位于任意位置, 文件一律以本脚本所在目录为准.
set -eu

SRC_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEST_DIR="$HOME/.zcode/hooks"
CONFIG="$HOME/.zcode/cli/config.json"

mkdir -p "$DEST_DIR" "$(dirname -- "$CONFIG")"
if [ "$SRC_DIR" != "$DEST_DIR" ]; then
  cp "$SRC_DIR/workspace-write.sb" "$DEST_DIR/workspace-write.sb"
  cp "$SRC_DIR/wrap-bash.py" "$DEST_DIR/wrap-bash.py"
  cp "$SRC_DIR/guard-edit.py" "$DEST_DIR/guard-edit.py"
fi
chmod +x "$DEST_DIR/wrap-bash.py" "$DEST_DIR/guard-edit.py"

python3 - "$CONFIG" <<'EOF'
import json
import os
import sys

config_path = sys.argv[1]
fragment = {
    "enabled": True,
    "events": {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "process",
                        "command": os.path.expanduser("~/.zcode/hooks/wrap-bash.py"),
                        "timeoutMs": 5000,
                    }
                ],
            },
            {
                "matcher": "Write|Edit",
                "hooks": [
                    {
                        "type": "process",
                        "command": os.path.expanduser("~/.zcode/hooks/guard-edit.py"),
                        "args": ["${ZCODE_PROJECT_DIR}"],
                        "timeoutMs": 5000,
                    }
                ],
            },
        ]
    },
}
config = {}
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
if config.get("hooks") == fragment:
    print("hooks 配置已是最新, 跳过写入")
else:
    config["hooks"] = fragment
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("已写入 hooks 配置:", config_path)
EOF

echo "完成. 新建会话或重启 ZCode 后生效."
