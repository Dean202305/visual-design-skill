# 视觉设计工坊 · visual-design

面向 **Codex、Claude Code、WorkBuddy 及其他 Agent Skills 宿主**的中文视觉设计技能。一份设计规范，按宿主使用不同安装入口；不绑定模型、工具名或作者机器路径。

从用途与竞品研究出发，选择方向和组件，完成实现、预览、检查与复用交付。适用于 Web、移动端、原生与桌面界面，以及 Figma、图片 / 视频、图表、文档、幻灯片和表格的视觉制作。

## 两个设计内核

- **Impeccable：反模板审查。** 在预览前检查无依据的紫蓝渐变、毛玻璃、重复卡片和空洞指标布局，先修正结构与内容，再决定表现。明确选定的品牌风格或 Liquid Glass 保留并验证。本包整合设计规则，不捆绑其可执行检测器或自动开启 hook。
- **awesome-design-md：视觉蓝图。** 随包提供 84 份固定版本的社区品牌分析，离线按需选择，映射为项目自己的设计变量和组件规范。它们是参考分析，不能称为大厂官方规范。

[内核工作规则](skills/visual-design/references/design-core.md) · [84 份蓝图目录](skills/visual-design/resources/design-core/blueprints.md) · [来源与许可](skills/visual-design/resources/design-core/SOURCES.md)

克隆仓库后，可列出蓝图或把选定的原始参考导入已有项目：

```bash
python3 skills/visual-design/scripts/blueprint.py list
python3 skills/visual-design/scripts/blueprint.py import linear.app --project "/你的项目目录"
```

导入到 `design-references/linear.app/`，同时保留许可与来源，不覆盖根目录 DESIGN.md。名称以目录为准；选定前先比较用途、平台和信息密度，避免只按品牌名选风格。

## 下载与安装

[下载当前发布包](https://github.com/Dean202305/visual-design-skill/releases/latest) · [兼容依据与验证范围](docs/compatibility.md)

| 使用工具 | 推荐安装方式 | 使用方式 |
| --- | --- | --- |
| Codex | 克隆仓库后运行下方安装器，或使用其 Skill 安装功能选择 `skills/visual-design` | `$visual-design` |
| Claude Code | 安装到项目或个人 `.claude/skills` | `/visual-design` |
| WorkBuddy | 下载当前 Release 的 WorkBuddy 专用 ZIP，在技能界面选择“添加技能 → 上传技能” | 选择技能，或描述设计任务 |
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
    B --> C[选择蓝图与比较设计方向]
    C --> D[确认后选择组件与实现]
    D --> E[反模板检查与实际预览]
    E --> F[确认后检查修正]
    F --> G[交付与项目内复用]
```

默认先确认用途与限制，提供 2–3 个有差异的方向。已有选择、明确委托和局部修改沿用会话授权，避免重复确认。新依赖、技术栈或交付范围变化先说明。

- **竞品**：按需求寻找真实产品，比较信息结构、交互逻辑和界面样式，保留来源与观察范围。
- **组件**：先判断用途、动作和状态，再选实现；动画完成不能代替业务成功。
- **视觉**：根据用途、已选蓝图和真实内容设计，拦截无依据的紫蓝渐变、毛玻璃与其他固定模板，保留用户已明确选择的表现。
- **平台**：保留项目技术栈、既有功能和原生交互习惯。
- **验收**：先提供可预览产物，确认后检查相关运行路径、内容、键盘 / 触屏及资源表现。
- **复用**：交付设计变量、变体 / API、适用状态、行为说明和可运行示例。

搜索、浏览器、图像生成、Figma 或文件编辑使用当前宿主已授权的能力；缺少时明确限制，不假装已经执行。见 [能力适配](skills/visual-design/references/agent-runtime.md)。

## 使用示例

[查看完整的 10 个使用案例](docs/examples.md)：每个案例包含准备材料、可复制请求和预期交付，覆盖从设计方向到代码或文件的流程。

| 场景 | 示例重点 |
| --- | --- |
| [求职助手桌面工作台](docs/examples.md#case-1) | 先出图，再实现；逐项保留筛选、任务和记录功能 |
| [运营数据后台](docs/examples.md#case-2) | 指标、筛选与图表的信息层级 |
| [品牌官网与动效](docs/examples.md#case-3) | 竞品研究、品牌表达与响应式实现 |
| [iOS / Android 原生应用](docs/examples.md#case-4) | 统一品牌，遵守平台交互习惯 |
| [Figma 设计与交接](docs/examples.md#case-5) | 组件状态、设计变量和开发规格 |
| [报告与演示文稿](docs/examples.md#case-6) | 数据叙事、可编辑文件与渲染检查 |
| [海报与社交图片](docs/examples.md#case-7) | 构图、字体层级和多尺寸适配 |
| [项目内可复用组件](docs/examples.md#case-8) | 组件 API、状态映射和可运行示例 |
| [Liquid Glass 材质修正](docs/examples.md#case-9) | 四层构建、背景折射验证与兼容降级 |
| [设计蓝图与反模板审查](docs/examples.md#case-10) | awesome-design-md 选型、Impeccable 检查与 DESIGN.md 适配 |

下面展示不同工具的调用写法；详细案例使用自然语言，可按宿主替换调用入口。

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
  resources/design-core/ # 固定版本的 Impeccable 规则与 84 份蓝图、许可
  scripts/validate.py
  scripts/blueprint.py    # 离线列举与导入蓝图
scripts/                # 跨平台安装与可复现打包
tests/                 # 临时目录内的分发回归测试
```

## 视觉参考与公开范围

[Aceternity UI](https://ui.aceternity.com/)、[Swishy](https://www.swishy.ai/)、[Anime.js](https://animejs.com/)、[MotionSites](https://motionsites.ai/)、[React Bits](https://reactbits.dev/)、[Uiverse](https://uiverse.io/elements)。它们用于组件和表现参考；竞品仍从具体产品需求搜索，采用资源前核对实现、依赖和使用条件。

本仓库发布统一规范和原创模板，未打包受限第三方运行时、商业插件资料、用户项目、账号配置或本机备份。实际制作依赖所在环境具备对应工具，本机已有完整整合版不会被自动替换。详见 [公开版与来源](skills/visual-design/references/provenance.md)。
