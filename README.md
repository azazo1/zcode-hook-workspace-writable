# workspace-writable

给 ZCode 的 Bash 工具加一层 macOS Seatbelt 沙箱 (workspace-write 语义), 并让沙箱内的命令免询问执行.

## 原理

- PreToolUse 钩子拦截所有 Bash 调用, 把命令包装成 `sandbox-exec -f workspace-write.sb -D WORKSPACE=<cwd> sh -c '<原命令>'`, 并通过 allow + updatedInput 跳过权限询问.
- profile 默认允许读, 网络和进程, 只收紧文件写入: 可写范围 = 当前工作区 + /tmp + 系统临时目录 + 常见包管理缓存目录.
- 两类调用不包装, 交回 ZCode 原有权限流程: 模型显式提权请求 (dangerouslyDisableSandbox), 以及敏感命令 (sudo / ssh 族 / rsync / 递归 rm).

## 安装

```shell
./install.sh
```

脚本可重复执行. 若仓库被克隆到任意位置, install.sh 会把两个文件复制到 `~/.zcode/hooks/` 并合并用户级配置; 若仓库本身就放在 `~/.zcode/hooks/`, 则原地即部署位. 安装后新建会话生效.

## 调整

- 放行更多可写目录: 编辑 workspace-write.sb 的 `allow file-write*` 列表.
- 调整免询问与人工确认的命令分界: 编辑 wrap-bash.py 的 SENSITIVE 正则.
- 回滚: 删除 `~/.zcode/cli/config.json` 中的 `hooks` 键, 或将其中的 `enabled` 置为 false.

## 限制

- 仅适用于 macOS. `sandbox-exec` 已被 Apple 标记废弃但目前可用, 其他平台需另选沙箱机制.
- 沙箱内命令免询问, 但写圈外路径会得到内核拒绝; 确有需要时由模型显式发起提权, 回到人工确认.
- 项目级方案: 在具体仓库内放 `<repo>/.zcode/config.json`, 用 `${ZCODE_PROJECT_DIR}` 指向仓库内的钩子脚本, 可随项目单独版本追踪, 详见 ZCode Hooks 文档.
