# 设计内核来源与许可

核对日期：2026-11-19。本目录为固定版本的静态设计参考，catalog.json 记录源仓库、提交、原路径与每个原始文件的 SHA256。只有选择后的文件才按需读取。

- **Impeccable / Paul Bakaus**：[固定提交](https://github.com/pbakaus/impeccable/tree/b49177d32788f2dc585c42831d845dacf1ebed2c)。收录 skill/reference/craft-floor.md 原文，保留 [Apache-2.0 许可](impeccable/LICENSE.md) 和 [上游 NOTICE](impeccable/NOTICE.md)。这里只收录设计规则，不包含其 CLI、浏览器扩展、字体、其他平台文件或 hook。
- **awesome-design-md / VoltAgent**：[固定提交](https://github.com/VoltAgent/awesome-design-md/tree/fcc70284932276d085f01ef9f83edde90b1258cb)。收录 design-md 下 84 份 DESIGN.md 原文，保留 [MIT 许可](awesome-design-md/LICENSE.md)。LICENSE 重命名为 LICENSE.md 方便随 Markdown 包分发，内容未改。

以上收录文件内容未修改。中文整合规范位于 references/design-core.md，是单独的适配层：只采纳符合用户任务的设计判断，明确用户方向、项目既有规范、平台、功能与真实性约束的优先级。上游的命令、绝对风格禁令和其他宿主指令不因此成为本包的执行入口。

awesome-design-md 是社区分析，不能表述为大厂官方发布；其中色值、字体和交互结论需结合目标页面与当前官方资料核对。文档许可不授予品牌标志、商标、专有字体、图片或其他资产的额外权利。
