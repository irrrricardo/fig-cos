# 来源与实现范围

- SVG 校验、文字合并、路径解析、原生 PPTX 导出、画布处理来自 [yrui-cmd/Cell](https://github.com/yrui-cmd/Cell)，提交 `2465e0adb0537c47538299dfea4de44e265a1055`，目录 `skills/cell_su8/scripts/`。原文件未修改，MIT 许可证在 `scripts/vendor/LICENSE`。
- 位图描摹使用 [visioncortex/vtracer 0.6.12](https://github.com/visioncortex/vtracer/tree/0.6.12)，由本地 Python 包提供，许可证随包保留。
- 场景装配、组件桥接、参数示意、局部保护检查、图库连接、PDF 局部恢复及本地导出适配为独立实现。生成图片由宿主可用工具完成，脚本不包含模型权重或生成服务客户端。图库来源与许可见 [icon-libraries.md](icon-libraries.md)，组件接口见 [components.md](components.md)。
- 结构精绘示例、原始像素质量记录及原生线性渐变适配为独立实现；供应目录文件未修改。精绘示例使用解析曲线、分部件几何与光影，不是原图隐藏像素恢复模型，范围见 [precision-redraw.md](precision-redraw.md)。

支持原生路径与文字、局部源素材恢复、人工标记的嵌套 PPT 组合及已知无字位图的颜色描摹。自动语义分割、任意复杂遮挡和原始透明图层的无损恢复、隐藏水印验证不在已实现范围内。程序图形是示意，不能作为经验数据。生成工具可用性与本地转换测试分开说明。
