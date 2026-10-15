# Agent 兼容与验证范围

文档核对日期：2026-10-15。通用核心采用 [Agent Skills 格式](https://agentskills.io/specification)：一个技能目录、SKILL.md 和相对路径引用的资源。不同宿主仅处理安装与元数据差异。

| 宿主 | 安装入口 | 调用入口 | 本仓库适配 |
| --- | --- | --- | --- |
| Codex | 项目 `.agents/skills/visual-design`；用户 `~/.agents/skills/visual-design` | `$visual-design` 或按描述选择 | Python 安装器；可选 `agents/openai.yaml` |
| Claude Code | 项目 `.claude/skills/visual-design`；用户 `~/.claude/skills/visual-design` | `/visual-design` 或按描述选择 | 同一核心目录，沿用原生技能发现 |
| WorkBuddy | 在技能界面“添加技能 → 上传技能”导入专用 ZIP | 技能选择或任务描述 | 生成双语描述、author、version 等字段，ZIP 根含 SKILL.md |
| 其他支持 Agent Skills 的工具 | 按工具文档指定的技能目录或导入入口 | 由宿主决定 | 通用 ZIP 或 `--agent generic --scope directory --dest` |
| 无原生技能系统但能读取文件的 Agent | 提供解压目录，要求先读 SKILL.md | 普通对话 | 手动读取流程；不声称支持自动发现 |

Codex 路径与调用依据 [官方技能文档](https://developers.openai.com/codex/skills/)。较早版本可能使用不同目录，本安装器采用本次核对的 `.agents` 入口，不会修改既有旧目录。不要同时装两份同名技能。

Claude Code 路径与 `/名称` 调用依据 [官方技能文档](https://code.claude.com/docs/en/skills)。本机个人目录不代表云端会话也已安装；云端按其项目或账号技能配置处理。

WorkBuddy 的 [技能导入说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market) 和 [开放平台格式](https://open.workbuddy.cn/docs/skill) 是本包适配依据。没有猜测它的隐藏本地安装路径，也没有自动提交到其技能市场。

## 一份设计规范，两个归档布局

- Portable ZIP：顶层只有 `visual-design/` 目录，可解压后放入宿主要求的技能目录。
- WorkBuddy ZIP：归档根直接放 SKILL.md 与相对资源；只生成平台需要的入口字段，设计正文与通用版相同，省去 Codex 界面附件。
- 校验用 Python 脚本不参与设计推理；没有 Python 的宿主仍可读取规范和模板。

完整能力取决于宿主工具。搜索、浏览器、图像生成、Figma、文档编辑和原生 SDK 不会因安装技能自动出现；执行路线见 [Agent 能力适配](../skills/visual-design/references/agent-runtime.md)。

## 验证分级

本仓库测试目录安装、资源完整性、不覆盖已有文件、Unicode 路径、ZIP 结构、WorkBuddy 字段、正文一致和可复现归档。它们验证分发兼容，不代表每个客户端、模型、订阅和工具组合都实际完成过设计任务。

发布前在临时目录完成测试，避免修改真实宿主配置。未安装 Claude Code 的机器不能宣称已在 Claude Code 中实跑；仅按 WorkBuddy 文档生成 ZIP 也不能宣称已通过其客户端或市场审核。
