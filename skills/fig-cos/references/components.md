# 场景与组件契约

`compose.py` 接收本地 SVG、已检查的位图、程序组件及真实文字，共享装配导出；不决定科学内容，不后台调用生成模型。

```json
{
  "schema_version": 1,
  "mode": "design",
  "canvas": {"width": 1200, "height": 700, "background": "#ffffff"},
  "components": [
    {"id":"cell","kind":"svg","file":"cell.svg","box":[80,120,240,200],
     "source":{"url":"真实来源 URL","author":"原作者","license":"逐项许可"}},
    {"id":"label","kind":"text","content":"Cell",
     "attrs":{"x":200,"y":360,"font-size":26,"font-family":"Arial","text-anchor":"middle","fill":"#17384d"}}
  ]
}
```

mode 为 reconstruct/design/ai-assisted，仅记录来源，不改变算法。每个 id 唯一，字母开头的字母/数字/横线/下划线。所有位置使用同一 SVG 画布单位；box=[x,y,width,height]，text 的 y 为基线。相对素材路径以场景文件所在目录为基准。

| kind | 字段 | 行为 |
| --- | --- | --- |
| svg | file, box；可选 rotation/normalize/trace_fallback/source | 保持比例、正交旋转；接收解析后的路径/几何/文字。CSS、defs 等先规范化。渐变近似需显式 trace_fallback |
| trace | file, box, text_free=true；可选 preset/source_kind/source | 局部描摹无字位图，source_kind 为 reference-raster 或 ai-generated；不执行生图 |
| parametric | generator, box, parameters | dna/cell-cluster，以及结构精绘示例 wheeled-bin/metal-bin/ribbon-protein/cell-aggregate；其他绘制器可生成 SVG 接入 |
| text | content, attrs；可选 line_height | 真实文本；换行拆为独立基线，按语言选择已安装字体 |
| shape | tag, attrs | rect/ellipse/circle/line/polyline/polygon/path；常用 SVG 几何和表现属性 |
| group | children；可选 attrs | 支持嵌套和变换，整体移动面板而内部仍可编辑 |

source 建议保留 url/author/license/license_url/modification。素材旁有 `.attribution.json` 时自动读取署名，保留原许可，不将源位图描摹或生成素材冒充图库原始矢量。

```powershell
python SKILL/scripts/compose.py --scene scene.json --output-dir new-job --export-pptx
```

输出 scene.svg/svg-preview.png，原始 scene-input.json，解析后可再次运行的 scene.json，独立 components/、逐项 provenance.json 和 job-report.json。解析后的场景使用输出目录内相对路径，复制整个目录后仍可装配。启用 --export-pptx 增加 export/；--render-ppt 同时导出并增加 powerpoint/ 实际预览，仍需看图验收。

后续组件只需产出支持的 SVG，或本地无字图片加来源，不必共用生成后端。代码可直接调用 `svg_assets.place_component` 放置文字/几何/分组；旧的 `place_icon` 继续支持规范化图标。

SVG 节点可直接携带受支持的线性渐变，组件实例化时 defs 与 fill 引用一并改名；原生 PPT 保留对应渐变填色。范围及失败条件见 [precision-redraw.md](precision-redraw.md)。trace 节点若经过预先放大，用 original_pixel_dimensions 记录放大前尺寸，来源记录不会将重采样视为新增科学细节。

导出器按叠放顺序保留 data-component-key 和旧 data-icon-key 的嵌套组合。稳定 ID 便于替换和 `check_preserved.py --editable-component ID` 检查其他内容是否保持。
