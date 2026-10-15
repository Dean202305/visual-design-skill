# 视觉设计工坊 · visual-design

面向 **Codex、Claude Code、WorkBuddy 及其他 Agent Skills 宿主**的中文视觉设计技能。一份设计规范，按宿主使用不同安装入口；不绑定模型、工具名或作者机器路径。

从用途与竞品研究出发，选择方向和组件，完成实现、预览、检查与复用交付。适用于 Web、移动端、原生与桌面界面，以及 Figma、图片 / 视频、图表、文档、幻灯片和表格的视觉制作。

## 下载与安装

[下载当前发布包](https://github.com/Dean202305/visual-design-skill/releases/latest) · [兼容依据与验证范围](docs/compatibility.md)

| 使用工具 | 推荐安装方式 | 使用方式 |
| --- | --- | --- |
| Codex | 克隆仓库后运行下方安装器，或使用其 Skill 安装功能选择 `skills/visual-design` | `$visual-design` |
| Claude Code | 安装到项目或个人 `.claude/skills` | `/visual-design` |
| WorkBuddy | 下载 `visual-design-workbuddy-v1.1.0.zip`，在技能界面选择“添加技能 → 上传技能” | 选择技能，或描述设计任务 |
| 其他 Agent Skills 工具 | 解压 Portable ZIP 到该工具规定的技能目录；也可使用通用目录安装 | 按宿主入口调用 |
| 只能读取文件的 Agent | 提供解压后的目录，要求先读取 SKILL.md 和相关参考 | 普通对话使用，不保证自动发现 |

### Codex / Claude Code

先克隆仓库：

```bash
git clone https://github.com/Dean202305/visual-design-skill.git
cd visual-design-skill
```

安装到一个已有项目，二选一：

```bash
python3 scripts/install.py --agent codex --project "/你的项目目录"
python3 scripts/install.py --agent claude-code --project "/你的项目目录"
```

或安装到当前用户：

```bash
python3 scripts/install.py --agent codex --scope user
python3 scripts/install.py --agent claude-code --scope user
```

安装器只复制此技能，不改模型配置、API Key 或项目指令文件。目标已有同名目录时拒绝覆盖；先备份并移走旧目录后再安装。用 `--dry-run` 可先看目标位置。安装后让宿主重新加载技能或开启新会话。

脚本使用 Python 3.9+ 标准库，无第三方 Python 依赖。Windows 可将 `python3` 换为 `py -3`。不使用脚本时，也可手动复制完整技能目录；不要只复制 SKILL.md 而漏掉参考与模板。

### WorkBuddy

下载 Release 中的 **WorkBuddy ZIP 原文件**，在 WorkBuddy 的技能页面导入。不要上传整个 GitHub 仓库的源码 ZIP，也不要再给专用包套一层目录。包内已经包含平台所需的双语描述、作者和版本字段。

这是可导入的技能包，不代表已上架 WorkBuddy 市场。具体界面以客户端当前版本为准。[官方导入说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)

### 其他 Agent

```bash
python3 scripts/install.py --agent generic --scope directory --dest "/该工具技能目录/visual-design"
```

`--dest` 是最终技能目录，安装器不猜测其他工具的发现路径。若工具不支持 Agent Skills，可让它读取 SKILL.md，再按需读取相对引用；是否可自动发现由宿主决定。

## 工作逻辑

```mermaid
flowchart LR
    A[确认用途与限制] --> B[竞品研究与界面观察]
    B --> C[比较设计方向]
    C --> D[确认后选择组件与实现]
    D --> E[实际预览]
    E --> F[确认后检查修正]
    F --> G[交付与项目内复用]
```

默认先确认用途与限制，提供 2–3 个有差异的方向。已有选择、明确委托和局部修改沿用会话授权，避免重复确认。新依赖、技术栈或交付范围变化先说明。

- **竞品**：按需求寻找真实产品，比较信息结构、交互逻辑和界面样式，保留来源与观察范围。
- **组件**：先判断用途、动作和状态，再选实现；动画完成不能代替业务成功。
- **视觉**：根据用途设计配色、排版与动效，不预设白蓝绿、深色、玻璃或其他固定模板。
- **平台**：保留项目技术栈、既有功能和原生交互习惯。
- **验收**：先提供可预览产物，确认后检查相关运行路径、内容、键盘 / 触屏及资源表现。
- **复用**：交付设计变量、变体 / API、适用状态、行为说明和可运行示例。

搜索、浏览器、图像生成、Figma 或文件编辑使用当前宿主已授权的能力；缺少时明确限制，不假装已经执行。见 [能力适配](skills/visual-design/references/agent-runtime.md)。

## 使用示例

Codex：

```text
$visual-design 优化这个桌面工作台。先核对原有功能并研究竞品，再给我可比较的方向。
```

Claude Code：

```text
/visual-design 按已确认的设计实现页面，保留全部筛选和任务状态，并交付预览与组件说明。
```

WorkBuddy 或普通对话：

```text
使用视觉设计工坊，根据这份报告制作可编辑演示文稿。先确认受众与讲述重点，再预览并检查。
```

## 开发与检查

```bash
python3 skills/visual-design/scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/package.py
```

打包生成 Portable ZIP、WorkBuddy ZIP 和 SHA256SUMS。两种包由同一核心生成，设计正文一致；默认只在 `dist/` 写生成物。验证详情见 [兼容说明](docs/compatibility.md)。

```text
skills/visual-design/    # 唯一的通用技能核心
  SKILL.md
  agents/openai.yaml    # 可选 Codex 界面元数据
  references/
  assets/templates/
  scripts/validate.py
scripts/                # 跨平台安装与可复现打包
tests/                 # 临时目录内的分发回归测试
```

## 视觉参考与公开范围

[Aceternity UI](https://ui.aceternity.com/)、[Swishy](https://www.swishy.ai/)、[Anime.js](https://animejs.com/)、[MotionSites](https://motionsites.ai/)、[React Bits](https://reactbits.dev/)、[Uiverse](https://uiverse.io/elements)。它们用于组件和表现参考；竞品仍从具体产品需求搜索，采用资源前核对实现、依赖和使用条件。

本仓库发布统一规范和原创模板，未打包受限第三方运行时、商业插件资料、用户项目、账号配置或本机备份。实际制作依赖所在环境具备对应工具，本机已有完整整合版不会被自动替换。详见 [公开版与来源](skills/visual-design/references/provenance.md)。
