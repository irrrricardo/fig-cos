# 文字清单

从原图读取标签，以原始画布像素记录。`x,y` 为基线，`source_bbox` 为参考边界。不要直接使用去字模型改变后的新图坐标。`paint_order` 大时文字置顶，应按原图遮挡关系调整。

```json
{
  "schema_version": "1.0",
  "source_canvas": {"width": 1200, "height": 700},
  "text_elements": [{
    "id": "label-1", "content": "Signal",
    "source_bbox": [100, 80, 100, 35],
    "x": 100, "y": 110, "coordinate_space": "pixels",
    "font_size": 28, "font_size_space": "pixels",
    "font_family": "Arial", "fill": "#111111",
    "text_anchor": "start", "rotation": 0, "paint_order": 999999
  }]
}
```

支持换行及可选 `font_weight`, `font_style`, `line_height`。每个 id 唯一。先检查输入副本中没有残留字形，再恢复真实文字，避免轮廓与文本框重叠。
