# 视觉设计工坊 · visual-design

面向 **Codex、Claude Code、WorkBuddy 及其他 Agent Skills 宿主**的中文视觉设计技能。一份设计规范，按宿主使用不同安装入口；不绑定模型、工具名或作者机器路径。

从用途与竞品研究出发，选择方向和组件，完成实现、预览、检查与复用交付。适用于 Web、移动端、原生与桌面界面，以及 Figma、图片 / 视频、图表、文档、幻灯片和表格的视觉制作。

## 设计内核

- **unslop** 负责已有界面的诊断、分层改稿与可选迭代短片。[改稿流程](skills/visual-design/references/unslop.md)
- **Impeccable：反模板审查。** 在预览前检查无依据的紫蓝渐变、毛玻璃、重复卡片和空洞指标布局，先修正结构与内容，再决定表现。明确选定的品牌风格或 Liquid Glass 保留并验证。本包整合设计规则，不捆绑其可执行检测器或自动开启 hook。
- **awesome-design-md：视觉蓝图。** 随包提供 84 份固定版本的社区品牌分析，离线按需选择，映射为项目自己的设计变量和组件规范。它们是参考分析，不能称为大厂官方规范。

[内核工作规则](skills/visual-design/references/design-core.md) · [84 份蓝图目录](skills/visual-design/resources/design-core/blueprints.md) · [来源与许可](skills/visual-design/resources/design-core/SOURCES.md)

克隆仓库后，可列出蓝图或把选定的原始参考导入已有项目：

```bash
python3 skills/visual-design/scripts/blueprint.py list
python3 skills/visual-design/scripts/blueprint.py import linear.app --project "/你的项目目录"
```

导入到 `design-references/linear.app/`，同时保留许可与来源，不覆盖根目录 DESIGN.md。名称以目录为准；选定前先比较用途、平台和信息密度，避免只按品牌名选风格。

## 设计记忆

启用后会按项目和媒介回顾已确认的偏好，并逐轮记录用户反馈、实际修改和验收状态。PPT 可参考已授权的模板盘点。数据默认写入本机用户目录，访问同一目录的宿主可以继续使用。[设计记忆用法](skills/visual-design/references/design-memory.md)

## 真实初稿、看图修正与作品事实检查

借鉴 Huashu Design 的可见初稿和事实检查分工，保留本技能的 2–3 方向、先预览确认及多平台流程。为关键参考保留实际画面，用相同真实内容比较方向，在项目内连接用户选择、问题、修改和复查。[设计证据规范](skills/visual-design/references/design-evidence.md) · [记录模板](skills/visual-design/assets/templates/design-evidence.md) · [对比与采用说明](docs/huashu-design-comparison.md)

Web 可用标准库工具检查宿主浏览器保存的 DOM 快照，不安装新的 Playwright/Pillow，不启动云服务或 hooks：

```bash
# 输出函数源码，用当前宿主的浏览器求值工具执行并保存返回的 JSON
python3 skills/visual-design/scripts/design_audit.py collector
python3 skills/visual-design/scripts/design_audit.py check "/项目证据目录/snapshot.json"
```

工具报告坏图、溢出和加载状态等有限事实；不判断美感、对比度合规或交互成功，无失败仍标为 `needs_review`。输入缺失返回错误；实际截图、交互和目标平台检查仍需执行。DOM 检查结果按项目保存。偏好与改稿记录沿用用户启用的设计记忆。

## 所有界面项目的强制细节

[完整界面规范](skills/visual-design/references/interface-craft.md) 已作为用户约定接入选型、实施与验收，优先于蓝图默认值：

- 微明度分层替代普通 1px 边框；暗色模式各角色的 `font-weight` 数值减 40，核对实际字体支持。
- 输入框通过同色系双环阴影和表面加深表达聚焦；保留可辨认的键盘焦点。
- 流式新增文字由轻微模糊迅速对焦，相邻字素错开几十毫秒；减少动态效果时直接清晰显示。
- 变化数字使用 `tabular-nums` 并按位数预留空间；行内小图标下移 `0.125em`。
- 展开使用 `grid-template-rows: 0fr` → `1fr`；正文使用 `text-wrap: pretty`，配合实际内容检查末行。
- 尺寸调整、侧边栏调整、排序和数据选点立即定住，不回弹；倾斜面板与底部抽屉允许按对应方案弹性复位。点赞和成功对勾短促回弹；复制真实成功后显示对勾，2500ms 后恢复，重复操作和卸载都清理旧计时。

字体能力、浏览器兼容和系统可访问性条件要如实记录。以上为已确认的项目规范，不声明为某家公司的官方设计系统。

## 八种按用途选择的交互动效

从 [效果库](skills/visual-design/references/motion-recipes.md) 选用，采用后必须落实状态、打断、复位、可访问性与验收，不给所有组件叠加全部效果。

| 效果 | 实现重点 |
| --- | --- |
| 3D 倾斜光影面板 | 跟随触点微倾和模拟镜面高光，释放后阻尼回正 |
| 流体胶囊形变按钮 | 按钮到状态或面板的几何、圆角连续变化 |
| 共享元素无缝展开 | 条目与详情连续展开，返回找回原位置 |
| 磁吸游标与滚动码表 | 图表选点、指示线和等宽数字准确联动 |
| 阻尼弹性抽屉 | 边界橡皮筋阻力，按位移与速度选择合法锚点 |
| 动态弥散光晕边框 | 仅 AI 功能区或重点模块的有记录例外，避免全页套用 |
| 弹簧交错列表或瀑布流 | 新项目弱弹性上移、细微交错，不重复播放已读内容 |
| 弹性微缩按钮 | 按下 0.96 与内阴影加深，释放轻微超调回到 1 |

## 下载与安装

[下载当前发布包](https://github.com/Dean202305/visual-design-skill/releases/latest) · [旧版接入自动更新](#自动更新) · [兼容依据与验证范围](docs/compatibility.md)

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

安装器把技能复制到指定目录。已有同名技能请走下方的自动更新接入流程。用 `--dry-run` 可先看目标位置。安装后让宿主重新加载技能或开启新会话。

脚本使用 Python 3.9+ 标准库，无第三方 Python 依赖。Windows 可将 `python3` 换为 `py -3`。不使用脚本时，也可手动复制完整技能目录；不要只复制 SKILL.md 而漏掉参考与模板。

### WorkBuddy

下载 Release 中的 **WorkBuddy ZIP 原文件**，在 WorkBuddy 的技能页面导入。不要上传整个 GitHub 仓库的源码 ZIP，也不要再给专用包套一层目录。包内已经包含平台所需的双语描述、作者和版本字段。

这是可导入的技能包，不代表已上架 WorkBuddy 市场。具体界面以客户端当前版本为准。[官方导入说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)

### 其他 Agent

```bash
python3 scripts/install.py --agent generic --scope directory --dest "/该工具技能目录/visual-design"
```

`--dest` 是最终技能目录，安装器不猜测其他工具的发现路径。若工具不支持 Agent Skills，可让它读取 SKILL.md，再按需读取相对引用；是否可自动发现由宿主决定。

### 自动更新

用 **v1.8.0** 或更新版本的官方 ZIP 或安装器安装后，Visual Design 会在调用时检查最新的 GitHub 正式 Release。宿主需要能运行 Python 3.9+、访问 GitHub 并写入本地技能目录。每份安装最多每 6 小时检查一次。新版通过校验后替换技能目录，旧版留存为备份。设计记忆、改稿记录和 PPT 模板索引保存在独立的本机记忆目录。

已经通过 ZIP 或安装器安装旧版的电脑，可用新版包内的脚本对原目录做一次接入。以下命令在新版 Portable ZIP 解压后的 `visual-design` 目录运行，示例是 Codex 的用户安装路径：

```bash
python3 scripts/update.py --now --skill-dir "$HOME/.agents/skills/visual-design"
```

把路径换成原技能目录即可用于 Claude Code、旧版 Codex 路径或其他本地 Agent。WorkBuddy 可在技能页导入一次新版专用 ZIP，后续更新取决于客户端是否提供原始可写目录和脚本权限。也可使用 WorkBuddy 的 [项目技能目录](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)，通过通用安装器把 Portable 版放在项目的 `.codebuddy/skills/visual-design`。

`--check` 只查看版本，`--now` 立即检查并更新。设置 `VISUAL_DESIGN_AUTO_UPDATE=0` 可暂停自动检查。Git 跟踪的副本随其仓库更新，自定义副本保留现有文件。[更新与恢复说明](skills/visual-design/references/auto-update.md)

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

[查看完整的 13 个使用案例](docs/examples.md)：每个案例包含准备材料、可复制请求和预期交付，覆盖从设计方向到代码或文件的流程。

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
| [界面层次与交互细节](docs/examples.md#case-11) | 微明度、字重、晕开、聚焦与不同反馈节奏 |
| [按用途组合交互动效](docs/examples.md#case-12) | 倾斜、抽屉、流光与按压反馈的范围及例外 |
| [真实方向与作品检查](docs/examples.md#case-13) | 参考画面、真实初稿、项目记录和事实检查边界 |

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
tests/                 # 分发、蓝图与作品事实检查
```

## 视觉参考与公开范围

[Aceternity UI](https://ui.aceternity.com/)、[Swishy](https://www.swishy.ai/)、[Anime.js](https://animejs.com/)、[MotionSites](https://motionsites.ai/)、[React Bits](https://reactbits.dev/)、[Uiverse](https://uiverse.io/elements)。它们用于组件和表现参考；竞品仍从具体产品需求搜索，采用资源前核对实现、依赖和使用条件。

本仓库发布统一规范和原创模板，未打包受限第三方运行时、商业插件资料、用户项目、账号配置或本机备份。实际制作依赖所在环境具备对应工具，本机已有完整整合版不会被自动替换。详见 [公开版与来源](skills/visual-design/references/provenance.md)。

### 既有界面的九轮精修

从实际页面诊断模板感，再决定整屏、局部或仅提建议。按需交付 10 秒内的本地迭代短片。实现与使用示例见 [改稿流程](skills/visual-design/references/unslop.md) 和 [改稿示例](docs/examples.md#unslop-review)。
