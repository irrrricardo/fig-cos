# fig-cos

**按原图复现科研示意图，交付可编辑 SVG 与原生 PowerPoint。**

[English](README.md) · [使用流程](docs/WORKFLOW.md) · [CLI](docs/CLI.md) · [质量规范](docs/QUALITY.md) · [图库来源与展示署名](docs/GALLERY.md)

这个项目把已实际使用的科研图复现方法、本地转换脚本与 Agent Skill 整理成独立发行包。模型负责看图、识别文字与安排组件，脚本负责描摹、装配和导出。绘图引擎本身不需要第三方服务密钥。

**默认采用 Previous local tracing：按原图分组件局部描摹，保留组件形象、结构和位置，文字、框与箭头独立重建。** 模糊图片也沿用这一路线，不自动改成通用蛋白、垃圾桶或 AI 重画。只有明确要求重新设计或探索替代方法时才采用其他路线。

## 过去完成的效果

![Biomni 参考图复现，历史 PowerPoint 实际显示](docs/images/biomni-reconstruction.png)

这份历史交付包含 127 个真实文字对象、3,978 个原生对象，无嵌入位图。科学插画来自参考图局部恢复/描摹，部分通用 UI 图标和论文缩略图使用替代示意。不是像素一致或语义图层恢复。改编自 Huang 等人的 *Biomni* 图 1，来源 [bioRxiv](https://doi.org/10.1101/2025.05.30.656746)，CC BY 4.0；完整修改及署名见 [展示说明](docs/GALLERY.md)。

![原图、早期图库替换与源图细节恢复的比较](docs/images/source-details.png)

中列是早期类别匹配的替代图标，仅作失败对照；默认采用保留原图形象的路线。

![原创 DNA 与细胞可编辑组件，历史 PowerPoint 实际显示](docs/images/editable-components.png)

原创程序示意，可用 `fig-cos demo` 重跑。[PPT](examples/procedural/editable.pptx) · [SVG](examples/procedural/editable.svg) · [场景](examples/procedural/scene.json)。示意不代表实测分子或细胞结构。

## 安装与运行

```bash
git clone https://github.com/irrrricardo/fig-cos.git
cd fig-cos
python -m venv .venv
# 激活虚拟环境后：
python -m pip install .
fig-cos doctor
fig-cos demo --output-dir outputs/demo
```

需要 Python 3.11+，其中 **Ubuntu/glibc Linux 请使用 Python 3.11 或 3.12**：固定的 VTracer 0.6.12 没有兼容 Ubuntu CPython 3.13 的安装包。Windows 的 CI 覆盖 3.11/3.13。CairoSVG 可能需要单独安装 Cairo 系统运行库；字体也影响版式。输出目录须为新目录。详细依赖与系统差异见 [兼容性](docs/COMPATIBILITY.md)。

```bash
fig-cos trace --input-image crop-2x.png --original-size 132 175 --text-free --preset detail --output-dir outputs/component
fig-cos compose --scene scene.json --output-dir outputs/figure --export-pptx
fig-cos export --input-svg approved.svg --output-dir outputs/export
fig-cos install-skill --target /你的Agent技能目录/fig-cos
```

公开技能包标识为 `fig-cos`，Python 模块为 `fig_cos`；已有本地 `$fig_cos` 调用不受影响。其他 Agent 需要能读取文件、运行 Python，并能看图或接收明确的文字/布局清单。没有内置 MCP 服务，也不要求使用特定 LLM。

## 能力与边界

- 默认局部颜色轮廓描摹；文字、框、箭头和嵌套组合独立可编辑。
- 可选跨库检索、源 PDF 局部恢复与从头设计；图库替换不自动用于参考复现。
- SVG/PPTX 导出与实际 PowerPoint 渲染是不同步骤。后者需要 Windows、桌面 PowerPoint 和 `.[powerpoint]` 额外依赖。
- `.[pdf]` 使用 PyMuPDF，具有 AGPL/商业双许可，应按用途核对。基本截图描摹和 PPTX 导出不需要它。
- 路径可编辑不等于恢复原始透明图层、科学身份、分子拓扑或隐藏像素。超分、自动语义分割和生成模型没有集成。

项目自写代码采用 MIT；上游代码、图库图标和论文衍生展示各自保留许可与署名。参见 [第三方声明](THIRD_PARTY_NOTICES.md)。开发验证参见 [贡献规范](CONTRIBUTING.md)。
