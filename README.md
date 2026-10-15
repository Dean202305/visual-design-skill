# 视觉设计工坊 · visual-design

一个以用途为起点的中文 Codex 设计 Skill：先理解任务与限制，研究同类产品，再选方向、组件和实现方式，最后预览与验收。

适用于 Web、移动端、原生与桌面界面，也覆盖 Figma、图片 / 视频、图表、文档、幻灯片和表格的视觉制作。规范使用中文，代码与 API 名称保留英文。

## 工作逻辑

```mermaid
flowchart LR
    A[确认用途与限制] --> B[搜索竞品与观察界面]
    B --> C[比较 2–3 个设计方向]
    C --> D[确认后选择组件与实现]
    D --> E[提供实际预览]
    E --> F[确认后检查与修正]
    F --> G[交付文件与项目内复用约定]
```

已有明确方向或局部修改时，沿用现有决定。已授权的操作不反复确认；会改变方向、技术栈或交付范围的决定先说明。

## 能力

- **用途与竞品**：按真实需求搜索同类产品，比较信息结构、交互流程和界面样式，保留来源与可观察范围。
- **组件选择**：先判断动作、内容和状态，再匹配组件；示例动画与业务结果分别核对。
- **视觉与动效**：按用途选择配色、排版、材质与表现力，避免固定审美和重复套模板。
- **多平台实施**：保留项目技术栈和原生控件习惯，明确 Web 参考如何转为平台实现。
- **预览与验收**：先看实际产物，再检查主要路径、内容极值、键盘 / 触屏、资源与性能。
- **复用交付**：设计变量、变体 / API、适用状态、行为说明及可运行示例。

## 安装

在支持 Skill 安装的 Codex 环境中，可以直接说：

> 使用 skill-installer 从 https://github.com/Dean202305/visual-design-skill 安装 skills/visual-design。

也可下载本仓库，把 `skills/visual-design/` 放到你的 Codex skills 目录中。已存在同名技能时，先保留原目录并比较版本，不直接覆盖。安装后按客户端提示重新加载或重启。

## 使用

```text
$visual-design 帮我优化这个桌面工作台。先核对原有功能，研究同类产品，再给我可比较的方向。
```

```text
$visual-design 按已经选定的设计实现页面，保留全部筛选和任务状态，交付组件说明与可预览版本。
```

```text
$visual-design 根据这份报告制作可编辑的演示文稿，先确认受众与讲述重点，再预览并检查。
```

Skill 支持按任务自动识别，也支持 `$visual-design` 显式调用。纯后端、文件管理和不涉及呈现的数据分析不触发。

## 文件结构

```text
skills/visual-design/
├── SKILL.md
├── agents/openai.yaml
├── references/          # 工作流、竞品、组件、平台、动效、产物与验收
├── assets/templates/    # 设计约定、竞品比较、组件交付底稿
└── scripts/validate.py  # 结构、引用及常见敏感内容检查
```

从仓库根目录检查：

```bash
python3 skills/visual-design/scripts/validate.py
```

## 视觉参考

[Aceternity UI](https://ui.aceternity.com/)、[Swishy](https://www.swishy.ai/)、[Anime.js](https://animejs.com/)、[MotionSites](https://motionsites.ai/)、[React Bits](https://reactbits.dev/)、[Uiverse](https://uiverse.io/elements)。

这些网站用于组件和表现手法参考；竞品分析仍搜索与具体任务相符的真实产品。每次采用时核对具体实现、依赖与使用条件。

## 公开版范围

本仓库发布统一设计规范和原创复用模板，供可审阅、可安装地使用。第三方私有技能、商业插件资料、受限运行时、用户项目、账号配置和本机备份不随包发布。设计工作流可独立读取，实际生成、编辑和构建需要所在环境具备对应工具。

详见 [公开版与来源说明](skills/visual-design/references/provenance.md)。本机已有完整整合版不受本仓库发布影响。
