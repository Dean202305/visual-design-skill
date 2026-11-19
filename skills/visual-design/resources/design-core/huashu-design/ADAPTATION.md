# Huashu Design：借鉴范围

核对日期：2026-11-19。来源：alchaincyf/huashu-design，固定提交 `e8d1148a80d5a281d4247cffe320add3df017928`。这不是 alchaincyf/huashu-skills 中的同名轻量版。

| 一手来源 | 采用的机制 | 本技能的适配 |
| --- | --- | --- |
| [方向探索](https://github.com/alchaincyf/huashu-design/blob/e8d1148a80d5a281d4247cffe320add3df017928/references/directions.md) | 看真实参考，提供可见的不同方向 | 保留用户约定的 2–3 版，不增加六候选、随机风格或无条件重新选方向 |
| [看图打磨](https://github.com/alchaincyf/huashu-design/blob/e8d1148a80d5a281d4247cffe320add3df017928/references/polish-loop.md) | 原尺寸逐屏看，记录问题与前后变化 | 保留先预览确认再完整检查的顺序，只因实际问题迭代，不强制凑轮数 |
| [事实体检源码](https://github.com/alchaincyf/huashu-design/blob/e8d1148a80d5a281d4247cffe320add3df017928/scripts/design_lint.py) | 事实检查与品味判断分开 | 独立实现只读采集函数与标准库分析器；不移植字体/配色禁令、相似度判分或全局外观账本 |
| [上下文](https://github.com/alchaincyf/huashu-design/blob/e8d1148a80d5a281d4247cffe320add3df017928/references/design-context.md) | 从已有项目、品牌和真实资产取依据 | 沿用已有优先级，以项目内记录保留用户选择，不写入跨项目偏好档案 |

新增执行入口见 [设计证据规范](../../../references/design-evidence.md)。这些改进不覆盖强制界面细节、八种按用途选择的动效、四层 Liquid Glass 或原生平台语义。

上游主体为 MIT，[原许可](LICENSE.md) 内容未改，文件校验值见上级 catalog.json。本包未收录其原版可执行脚本、92 份风格样张、视频/字体/商标资产、插件配置、云服务或 hooks。上游演示贴纸有单独许可，不在本包内。这里借鉴工作方法并独立实现工具，不能声称运行了 Huashu 原版检测器，或继承其全部输出能力。
