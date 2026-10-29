# 科学图库与矢量装配

本技能已索引 [Bioicons](https://bioicons.com/)，包含细胞、蛋白、核酸、微生物、实验设备等 SVG；通用机器人、数据库、齿轮等使用 [Lucide](https://lucide.dev/)。Bioicons 许可按单图判断，不能用网站代码许可替代素材许可。下载结果自动保留作者、许可、源 URL 和哈希。来自图库的科学图标是相近素材替换，不是原始图标的恢复。

## 扩展目录

| 来源 | 已实现能力 | 选用重点 |
| --- | --- | --- |
| [Reactome Icon Library](https://reactome.org/icon-lib/) | 官方公开目录搜索、SVG 下载、作者与 CC BY 4.0 记录 | 分子、细胞组成及过程图标；结合条目说明核对具体结构 |
| [SciDraw](https://scidraw.io/) | 矢量筛选、搜索、下载、作者与逐项许可记录 | 科学家贡献的动物、实验及结构素材；标记 vector 的文件仍须验证内部是否嵌图 |
| [NIH BioArt](https://bioart.niaid.nih.gov/) | 指定条目解析及预览文件信息 | 解剖、细胞、病原与医疗专业插画；SVG 下载需逐条在官网确认，尚未接通通用矢量下载接口 |
| [TogoTV](https://togotv.dbcls.jp/pics.html)、[Servier Medical Art](https://smart.servier.com/) | 可在官网补充查找；未新增独立 API 适配器 | 部分素材已由 Bioicons 收录，去重后计数，按原条目许可署名 |

```powershell
python SKILL/scripts/candidate_board.py "DNA" --per-provider 3 --output-dir new-candidates
python SKILL/scripts/science_catalogs.py search --provider reactome "ribosome" --limit 8 --output results.json
python SKILL/scripts/science_catalogs.py search --provider scidraw "DNA" --limit 8 --output results.json
python SKILL/scripts/science_catalogs.py fetch --results results.json --index 0 --output-dir cached-assets
python SKILL/scripts/science_catalogs.py nih-entry 172
```

候选板同时查询 Bioicons、Reactome、SciDraw，导出预览和来源 JSON。查看候选形态后再选择；排名并非匹配质量分数。单库失败或伪矢量会记录在 rejected 中，不静默代用。NIH 的解析依赖公开页面结构；失败时直接检查条目页。未知许可保留原标记及条目链接，不能自行归为 CC0。

```powershell
python SKILL/scripts/icon_library.py search "antibody" --limit 8
python SKILL/scripts/icon_library.py search "细胞" --license cc-0
python SKILL/scripts/icon_library.py fetch --path "从搜索结果复制完整 path"
python SKILL/scripts/icon_library.py fetch --lucide database
```

搜索默认读本地索引；`refresh` 显式更新公开目录，不在每次绘图时重新下载整库。部分中文词有映射，专业词用英文搜索。不要用未经验证的假路径拼凑素材。第一次获取 Lucide 图标需要联网；已缓存时直接复用。

发行版将下载和更新写入用户缓存，不写安装包：可用 `FIG_COS_CACHE` 指定缓存根目录，默认采用 `XDG_CACHE_HOME/fig-cos` 或 `~/.cache/fig-cos`。未更新时使用随包附带的 Bioicons 索引。

## 图标规范化

`normalize_icon.py` 解析 CSS 选择器、展开变换、将描边转路径、解析 clipPath 与 use，并规整 evenodd 镂空。未支持的滤镜、遮罩和文字明确报错。

```powershell
python SKILL/scripts/normalize_icon.py --input downloaded.svg --output component.svg
```

复杂渐变在现有 PPT 导出器中不保证无损，默认拒绝。只有需要近似图标且任务允许时，显式加 `--trace-fallback`：本地渲染 512px，再描摹为矢量路径。必须把这种修改记为“渐变与轮廓近似”，不可称为原始路径无损保留。

## 组装与分组

在生成科研图的 Python 代码里，将本技能 scripts 加入 sys.path，使用 `svg_assets.place_icon` 放置已规范化图标：

```python
import xml.etree.ElementTree as ET
from svg_assets import place_icon
scene = ET.Element('{http://www.w3.org/2000/svg}svg',
                   {'viewBox':'0 0 1200 800','width':'1200','height':'800'})
place_icon(scene, 'component.svg', key='cell-icon-1',
           x=100, y=200, width=100, height=80,
           source_url='实际素材源 URL')
```

每个实例 key 必须唯一；保持长宽比，可按 90 度旋转。输出 SVG 中 `data-icon-key` 标记的各图标，在 `rebuild.py` 导出时会形成可移动整体的原生 PPT 组合，组合内路径仍可编辑。

将用到的 `.attribution.json` 汇总到交付目录，规范化与描摹都要标记修改。Lucide 的 ISC 及部分 Feather 衍生图标的 MIT 文本在缓存目录随包保留；Bioicons 的署名图标需保留作者及许可链接。

## 素材与场景的衔接

规范化后的图标可用 `compose.py` 的 svg 节点装配，旁边的署名 JSON 自动读入来源。带真实文字的源组件使用 `place_component` 或不带 normalize 的 svg 节点；不要将文字传入只处理图标路径的规范化器。不同画布留白可能使同尺寸素材显得大小不同，按实际可见边界比较。

同类方法调研见 [公开方法与证据](public-methods.md)。
