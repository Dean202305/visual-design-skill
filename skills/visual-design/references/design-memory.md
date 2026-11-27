# 设计记忆

开始设计时用 `recall` 检查本地记忆。返回 `enabled: true` 表示已有用户启用后的记录，后续每轮改稿完成或收到验收结果时整理并写入。首次由用户要求记忆时创建记录。记录和读取使用 [design_memory.py](../scripts/design_memory.py)，只需要 Python 3.9+ 标准库。

## 何时查阅和记录

1. 确定本次的项目、产物与媒介。复用项目的稳定名称，例如「织序 AI 企业版」，媒介使用简短一致的标签，例如 `web`、`mobile`、`slides`。
2. 开始设计前运行 `recall`。把适用的偏好带入方向选择和检查，按需查看最近的相关改稿。当前用户要求优先。同一偏好在多个适用范围有记录时，优先使用项目记录，其次媒介记录，再参考通用记录。
3. 一轮修改整理为「原先如何、用户反馈、实际修改、校验和结果」。同轮工具重试合并为一条，后续新增的反馈另记。提案用 `proposed`，已实施等确认用 `applied`，用户确认用 `accepted`，被否决或撤回分别用 `rejected`、`reverted`。只有实际检查过的内容才填写校验结果。
4. 已接受的局部选择可作为项目内先例。用户明确希望某种做法以后复用时，按其实际范围更新偏好。某份稿件的配色、参考模板中的特点、代理的猜测或用户的沉默仅可作为本次记录。后续反馈改变了原决定时，用新记录更新同一偏好键。
5. 新改稿使用新的 `revision.id`。同一改稿的验收结果变化时，沿用该编号并提交新事件。重试同一次写入沿用外层 `id`，同内容只保存一次。需要检查全部阶段时用 `history`。

## 调用

从技能目录运行。宿主可访问同一目录时，共用一份记忆；默认位置为 `~/.visual-design/memory/`。通过 `VISUAL_DESIGN_MEMORY_DIR` 或放在子命令前的 `--memory-dir` 指定用户可读写的其他位置。

```bash
python3 scripts/design_memory.py recall --project "示例工作台" --medium web
python3 scripts/design_memory.py record /path/to/one-design-event.json
python3 scripts/design_memory.py history --project "示例工作台" --medium web --limit 30
```

`recall` 输出生效的偏好和该项目最近的改稿。需要聚焦一份产物时加 `--artifact`。`history` 给出匹配的总数和最近记录，需要更多时增大 `--limit`。当宿主没有可写的持久目录时，在当前任务整理可审阅的改稿摘要，并说明实际保存的位置与可复用范围。

一条虚构的记录可以同时整理修改和保存用户已确认的偏好：

```json
{
  "id": "workbench-navigation-02-approved",
  "revision": {
    "id": "navigation-02",
    "project": "示例工作台",
    "artifact": "主导航",
    "medium": "web",
    "before": "窄屏功能面板从屏幕左侧展开",
    "feedback": "窄屏改从底部导航按钮处弹出",
    "change": "面板向上出现，右边缘对齐按钮",
    "check": "核对桌面与窄屏，在触屏上打开和收起",
    "status": "accepted"
  },
  "preferences": [
    {
      "key": "navigation.catalog",
      "scope": "project",
      "context": "示例工作台",
      "value": "窄屏目录贴着底部导航右侧按钮展开",
      "evidence": "用户明确要求后续该工作台沿用"
    }
  ]
}
```

只写改稿时省略 `preferences`，只写偏好时省略 `revision`。通用偏好用 `global`，媒介偏好用 `medium` 和对应标签，项目偏好用 `project` 和项目名。用户要求撤回某个偏好时，以相同范围和键记录 `value: null`，后续读取采用仍适用的其他范围记录。记录只保留必要的设计决定、反馈和验证摘要，私人资料、会话全文、凭据和商业内容留在原处。

## PPT 模板参考

制作演示文稿时用 `recall --medium slides` 检查 `ppt_references`。若用户更新授权模板，从指定位置读取样本，可将归纳写入记忆目录的 `ppt-references.md`，按用途寻找相关条目。每条注明来源或本地文件、看过的实际页、适用用途、可复用的版式和可确认的主题色或字体。渲染和母版信息分别标明，来源可见性变化时先核实。

夸克网盘是可选来源，使用当前宿主已授权的网盘能力读取用户指定的模板。其他宿主同样可使用记忆目录里的盘点结果或用户给出的本地样本。阅读模板后借鉴信息层级、留白、主题与页面组合，按新内容安排版式。模板原件和个人记忆存于本地私有目录，打包技能时仅包含工作流、脚本和虚构示例。
