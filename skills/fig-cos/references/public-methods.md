# 公开方法与证据

核对日期：2026-10-29。

| 来源 | 核对到的内容 | 本技能处理 |
| --- | --- | --- |
| [小描官网](https://xiaomiao-ai.com/) / [开发者文档](https://xiaomiao-ai.com/docs) | 公开图片到 SVG、期刊图及处理接口的契约；已检查资料没有给出识别模型、权重或服务端实现 | 不能由接口推断其具体算法，未访问受保护的客户或内部处理接口 |
| [Cell](https://github.com/yrui-cmd/Cell) / [cell-lct](https://github.com/yrui-cmd/cell-lct) | 文字清单、外部识别调用、SVG 几何解析及 PPT/Illustrator 本地导出 | MIT 离线导出代码已复用，许可见 vendor/LICENSE；外部服务没有复刻 |
| [AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit) | SAM 分割、SVG 占位布局、图标装配；autofigure2.py 的装配函数嵌入 PNG image 标签 | 借鉴分层装配思想，用真实矢量图库替换图标；不把含 image 的 SVG 宣称为全矢量 |
| [Edit-Banana](https://github.com/BIT-DataLab/Edit-Banana) | AGPL-3.0；SAM3、OCR、VLM 与 DrawIO 结构重建；README 明示网页版本可能领先公开仓库 | 参考结构拆分和文本核对，不拷贝代码，不安装额外付费 API |
| [VisPainter](https://github.com/HerzogFL/VisPainter) | 任务解析、布局草稿、工具绘制、截图反馈循环；公开 MCP 工具 | 借鉴先布局后装配再验收的流程，不依赖其 API 或 Visio |
| [StarVector](https://github.com/joanrod/star-vector) / [OmniSVG](https://github.com/OmniSVG/OmniSVG) | Apache-2.0 代码，提供图片到 SVG 模型路线和权重入口 | 作为候选，没有下载或运行权重，不能声称已有模型推理能力 |
| [picosvg](https://github.com/googlefonts/picosvg) | Apache-2.0；将描边、裁剪与变换解析为等价路径，但不支持全部 SVG 特性 | 已安装并接入，补充全局 CSS 展开、视口收紧及明确失败处理 |

以上项目没有证据表明就是小描服务端使用的技术。当前实现是公开代码与独立编写工具的组合，目标是同类可编辑绘图能力。
