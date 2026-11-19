# 强制界面细节规范

用户已确认：本规范用于所有界面项目，不是可选风格；“边框”指普通 1px 边框，“减 40”指 font-weight 数值减 40。新建、改版及局部修改均在本次范围内遵守，不能由品牌蓝图或来源默认值覆盖，也不据此重做任务范围以外的界面。用户之后明确修改约定时再更新。

下列规则描述视觉与交互结果，Web 使用所列 CSS/API，原生界面映射到相应平台能力。静态稿体现层次与排版，并标注动效规格；不能声称图片已验证交互。字体、系统设置或渲染能力无法兑现某项规则时，说明具体缺口与替代，不将其悄悄变成可选项。焦点可辨认、真实成功状态和减少动态效果仍是必需条件。

## 层次、暗色与输入框

- **微明度分层**：用背景、内容表面、嵌入表面、浮层之间的细微明度差区分空间，不靠普通 1px 轮廓或分隔线画满界面。明度差应在实际屏幕上可辨认，前景文字、状态与必要控件仍有足够对比；微明度不等于低对比文字。按页面底层色调设变量，避免固定浅灰或纯黑套用。
- **暗色字重减 40**：每个文本角色的暗色目标为其浅色基准减 40，例如 500 → 460、400 → 360；不指减少 40%。确认字体文件与 `@font-face` 声明支持这些值，优先可变字体。静态字体或受限的字重轴可能只映射到邻近字重；计算样式显示 460 不等于字形真的更细。不能用降低不透明度或缩小字号伪装字重变化，无法精确实现时明确报告。新增或替换字体仍遵守许可与依赖确认约定。
- **温润聚焦**：输入框聚焦时通过同色系双环阴影和表面加深形成咬合感，不突然出现高亮边线或改变边框宽度。两环共享输入框圆角、没有布局跳动，焦点存续期间持续可辨认。不能直接删除 outline 而不提供等效反馈；强制颜色模式下阴影可能不显示，应保留系统可见焦点轮廓，不用“去边框”隐藏焦点。

以下是结构示例，色值、环宽与过渡时间由项目实际对比度和预览确定，不是统一配色模板：

```css
.field {
  border: 0;
  background: var(--field-surface);
  border-radius: var(--control-radius);
  transition: background-color 140ms ease-out, box-shadow 140ms ease-out;
}
.field:focus {
  outline: none;
  background: var(--field-surface-focused);
  box-shadow: 0 0 0 2px var(--focus-inner), 0 0 0 5px var(--focus-outer);
}
@media (forced-colors: active) {
  .field:focus { outline: 2px solid Highlight; outline-offset: 2px; }
}
```

## 文字晕开、数字与行内图标

- **入场先晕后清**：新出现文字从轻微高斯模糊快速对焦至 `filter: blur(0)`，相邻字形错开几十毫秒。按字素簇分段，例如 `Intl.Segmenter` 的 grapheme 粒度，避免拆坏中文组合字符或 emoji。不要用动画改变正文内容、阅读顺序、选择和复制结果。
- **流式内容只动新增片段**：已清晰内容不反复模糊，不重播整段；文字到达即可显示，动画不阻塞输入、复制和停止生成。字形较多时并行消退或分批处理，不能让逐字延迟累计成数秒阅读等待。模糊只施加于新增文字，不晕染整张卡片。辅助技术合并播报，不把每个字都作为独立 live 更新。
- **减少动态效果**：使用 `prefers-reduced-motion` 或平台设置时直接呈现清晰终态，不保留逐字延迟、模糊或弹簧等待。任何动效中断、卸载或快速更新都必须到达可读终态。
- **数字等宽锁定**：用正确的 `font-variant-numeric: tabular-nums`，核对字体真的提供等宽数字。它不要求正文改成等宽字体，也不能单独保证 9 → 10 或 99 → 100 的总宽度不变；对变化区按合理最大位数预留宽度、对齐小数与单位，宽度不足时允许扩展而不裁掉真实数值。
- **行内小图标下移 1/8 字高**：以当前文字 em 为参照，下移 `0.125em`；Web 行内 SVG 可使用 `vertical-align: -0.125em`，或在已对齐的包装层用等效偏移，二者不要叠加。统一图标尺寸、viewBox 留白和笔画后检查视觉中心，避免字体回退让图标与文字脱节。装饰图标不重复进入辅助技术朗读。

```css
.changing-number { font-variant-numeric: tabular-nums; }
.inline-icon { width: 1em; height: 1em; vertical-align: -0.125em; }
.prose { text-wrap: pretty; }
@keyframes ink-in {
  from { filter: blur(3px); opacity: 0.7; }
  to   { filter: blur(0); opacity: 1; }
}
.new-grapheme {
  display: inline-block;
  animation: ink-in 150ms ease-out both;
  animation-delay: var(--grapheme-delay, 0ms);
}
@media (prefers-reduced-motion: reduce) {
  .new-grapheme { animation: none; filter: none; opacity: 1; }
}
```

模糊半径与时长是起始示例；交错以几十毫秒为单位，预览真实内容后控制总体等待。逐字包裹只用于需要的新增片段，检查其对换行、连字和屏幕阅读的影响；必要时按短片段晕开，保留原始正文语义。

## 展开、换行与反馈节奏

**自适应展开**：Web 的展开容器使用 `grid-template-rows: 0fr` → `1fr`，让内容撑开，不用固定大 `max-height` 猜测内容高度。中间包装层 `min-height: 0; overflow: hidden`，内容间距放在内层，避免关闭后残留高度。收起状态还要控制可访问性和焦点：先将必要焦点移回触发器，再对折叠内容设 `inert` 等实际不可交互状态，触发器同步 `aria-expanded`。只压成零高并不会自动阻止 Tab 进入。立即 `display: none` 会中断过渡，若需设置应在退出完成后进行。

```css
.disclosure { display: grid; grid-template-rows: 0fr; transition: grid-template-rows 180ms ease-out; }
.disclosure[data-open="true"] { grid-template-rows: 1fr; }
.disclosure > .clip { min-height: 0; overflow: hidden; }
@media (prefers-reduced-motion: reduce) {
  .disclosure { transition: none; }
}
```

**正文排版保护**：正文启用 `text-wrap: pretty`，降低末行只剩一个孤词或极短内容的概率。这是浏览器的排版策略，不能承诺每种语言、宽度和字体都绝无孤词；不支持时保留正常换行。用实际中文、英文、长链接、缩放和窄屏检查末行，必要时调整容器或经用户认可的文案，不靠全段 `nowrap`、乱插硬换行或不换行空格把内容撑出屏幕。它与分页排版的 `orphans` 不是同一机制。

| 交互 | 强制节奏与终态 |
| --- | --- |
| 拖拽、吸附、侧边栏调整 | 指针移动直接跟随；释放时立即提交最终尺寸或吸附点，禁用回弹、惯性漂移和等待动画。不声称设备链路物理“零延迟”，但实现不得人为增加松手延迟。保留最小/最大边界、指针取消、触屏和键盘替代路径。 |
| 点赞等轻量肯定反馈 | 使用短促、幅度受控的一点回弹，反馈欢快；动画不阻塞连续操作，状态仍以真实业务结果为准，失败要可回滚或说明。 |
| 复制成功对勾 | 复制实际成功后才显示，允许一次小幅弹性反馈；自本次成功起 2500ms 自动隐藏成功标记并恢复原按钮状态，不留下空占位或继续显示“已复制”。按钮点击区与布局保持稳定。 |

复制反馈的计时在每次成功时重置，清理旧计时器并在卸载时取消；后发操作应使旧异步结果失效，避免早先结果覆盖新状态。复制失败不能出现成功对勾；减少动态效果时直接切换标记，仍保留 2500ms 自动恢复。恢复的是视觉反馈，不清除已复制的剪贴板内容。

## 验收

按本次涉及的组件实测：微明度层级与正文对比、浅/暗对应字重与实际字体、键盘及强制颜色焦点、长流式内容与减少动态效果、数字跨位数、图标基线、展开后的动态内容与收起焦点、窄屏末行、拖拽释放、连续点赞、复制成功/失败/快速重复与卸载。计时器受后台页节流影响，不能把回调绝对准时当作保证；页面恢复可见时根据成功时间重新核对并清除过期反馈。

这些是用户已确认的项目规范，不是已经核实的某家“大厂原版”。技术依据：[CSS 字重](https://www.w3.org/TR/css-fonts-4/#font-weight-prop)、[数字字形](https://www.w3.org/TR/css-fonts-4/#font-variant-numeric-prop)、[文本换行策略](https://www.w3.org/TR/css-text-4/)、[焦点可见要求](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)。
