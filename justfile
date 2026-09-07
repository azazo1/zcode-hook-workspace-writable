[private]
default:
    just --list

# 运行 install.sh 部署文件并注册用户级配置.
install:
    ./install.sh

# 用样例 JSON 测试包装脚本输出.
test:
    echo '{"tool_name":"Bash","tool_input":{"command":"pwd"},"cwd":"/tmp"}' | uv run wrap-bash.py
