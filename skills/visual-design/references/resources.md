# 技术入口与复用模板

本公开包自带完整工作规范与通用模板。第三方技术手册、商业插件、字体库、构建产物和私有运行时不随包复制；使用目标项目实际具备且有权使用的工具。

## 本包模板

| 用途 | 模板 | 使用方式 |
| --- | --- | --- |
| 明确用途、限制、方向与待确认项 | [设计约定](../assets/templates/design-brief.md) | 多页或多组件任务复制到项目，沿用已有文档位置 |
| 研究真实产品并保留证据 | [竞品比较](../assets/templates/competitive-review.md) | 少量代表样本，记录可观察范围与取舍，不按格子编造结论 |
| 组件变量、API、状态与例子 | [组件交付](../assets/templates/component-spec.md) | 只填写相关状态，连接实际组件文件和运行入口 |

模板辅助项目内复用；单点修改无需建立整套文档。

## 官方技术起点

| 主题 | 官方入口 |
| --- | --- |
| Web 语义、CSS、表单与浏览器行为 | [MDN](https://developer.mozilla.org/) |
| 可访问性规范与控件模式 | [WCAG](https://www.w3.org/WAI/WCAG22/quickref/)、[ARIA APG](https://www.w3.org/WAI/ARIA/apg/) |
| Apple 平台 | [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/) |
| Android | [Android Design](https://developer.android.com/design) |
| Windows | [Windows apps](https://learn.microsoft.com/en-us/windows/apps/) |
| Figma | [Plugin API](https://developers.figma.com/docs/plugins/) |
| 时间线、SVG 与交错动效 | [Anime.js](https://animejs.com/documentation/) |
| React 组件动效 | [Motion](https://motion.dev/docs) |
| 时间线与滚动编排 | [GSAP](https://gsap.com/docs/v3/) |
| 3D 与 Canvas 场景 | [Three.js](https://threejs.org/docs/) |

这些是查找起点，不是依赖清单或已验证版本。采用前核对当前 API、许可、项目已有版本与实际工具能力。组件和视觉来源按 [六站索引](sources.md) 查找；真实产品研究按 [竞品分析](competitive-analysis.md) 执行。

## 验证本包

从本 skill 目录运行：

```bash
python3 scripts/validate.py
```

检查入口、引用、模板、Python 语法和常见敏感内容。结构校验不能替代设计判断、真实交互验证或第三方平台验收。
