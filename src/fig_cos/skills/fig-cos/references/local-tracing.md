# 默认基线：Previous local tracing

2026-10-29 用户明确选择对照中的 **Previous local tracing** 一列，作为今后参考图片复现的默认。对应三图测试的原复现结果；不是后来通用精绘、描摹参数扫描或原分辨率直接描摹的试验。

## 默认做法

1. 保留原始截图并记录画布、文字、框和箭头的位置。文字重建为真实文本，规则框/箭头用几何；不将整页一并描摹。
2. 按原图组件裁剪，每个组件保持原形象、纵横比、朝向和相对位置。复杂蛋白、细胞和物体按源图的可见颜色轮廓描摹，不用通用组件重新想象。
3. 必要时将局部用 Lanczos 放大到 2 倍，使用本地 VTracer 的 detail 预设拟合曲线。记录放大前尺寸；2 倍采样不增加原图信息，不默认改用原分辨率直接描摹或更强的 clean 简化。
4. 仅针对已核对的均匀背景进行匹配/清理，保留细线、孔洞、透明叠加的可见颜色及部件边界。背景判断或轮廓遮罩会误删连接线，处理前后必须看局部；不从图形类别推断应删除的区域。
5. 通过 `place_component` 按源坐标装配，每个图标独立分组。文字、框与用户认可区域保持稳定 ID；修改局部时运行保护检查。
6. 对照原图看整页和局部，查看导出 SVG 与实际 PowerPoint。先检查形象、结构、连接、遮挡、颜色及文字，再检查可编辑性。路径多/少、放大后的像素数都不是质量结论。

本地调用示例（已检查无字的局部素材）：

```powershell
python SKILL/scripts/trace_asset.py --input-image crop-2x.png --original-size 132 175 --text-free --preset detail --output-dir new-component
python SKILL/scripts/rebuild.py --input-svg assembled.svg --output-dir new-export
python SKILL/scripts/preview_ppt.py --pptx new-export/editable.pptx --output-dir new-preview --width 2400
```

当前 detail 参数：`filter_speckle=1`、`color_precision=8`、`layer_difference=8`、`length_threshold=2.0`；描摹为 color/stacked/spline，`corner_threshold=60`、`max_iterations=10`、`splice_threshold=45`、`path_precision=3`。这些是已选路线的起点，源图的实际显示与细线保留决定是否需要局部调整。

## 路线边界

- “更清晰/精致”或输入模糊，本身不触发重设计。默认继续沿源图描摹，允许保留忠实的细节和不完美边缘。
- 同一原图的原始路径可以复用；同类别图库图标不等于同一素材，不默认替换。
- 结构精绘、AI 重画、通用生成器和新的修复模型仅在用户明确要求时使用，作为独立候选；保留描摹基线。
- 本路线恢复可编辑的颜色轮廓与独立文字，不宣称恢复原始透明图层、分子身份或语义部件。不要把这些局限当作自动改用另一种形态的理由。
- 用户从头设计新图时仍可选择图库、程序组件或 AI 素材；此默认仅针对参考图片复现。
