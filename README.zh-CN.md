# fig-cos

### 让科研图片，重新变得可编辑。

把论文插图、机制示意和图形摘要交给你的 Agent，获得可以改文字、换配色、调布局的 **SVG 与 PowerPoint**。

[English](README.md) · [安装 Skill](#quick-start安装到你的-agent) · [下载技能包](https://github.com/irrrricardo/fig-cos/releases) · [查看效果](#看看它能做什么)

![fig-cos：从参考图到可编辑科研图](docs/images/fig-cos-hero.png)

**一张参考图，一句需求，让你的 Agent 接着画。**

fig-cos 是面向科研绘图的 **Agent Skill**，可安装到 **Codex、Claude Code 和 DeepSeek Harness**。从复现一张已有图片，到组织一张新的科研示意图，把图形变成能继续修改、讨论和交付的成果。

```text
使用 fig-cos，把这张参考图复现成可编辑 PPT。
保留它的结构和布局，文字单独可改，图形按组件分组。
```

## 看看它能做什么

| 你想做的事 | fig-cos 帮你完成 |
| --- | --- |
| 复现论文里的复杂示意图 | 重建版式、文字和图形组件，交付 SVG / PPTX |
| 把截图带进自己的汇报 | 保留参考图的形象与结构，继续修改标签、配色与位置 |
| 完善机制图、图形摘要或流程图 | 组织内容层级，组合文字、箭头和科学插画 |
| 给已有图件增加合适的元素 | 连接 Bioicons、Reactome、SciDraw 等图库，挑选和装配矢量素材 |

### 01 · 复杂科研图，也能继续修改

多面板版式、密集标签、分子插画、流程箭头——把一张信息丰富的科研图，拆成可以继续使用的文字与组件。

![Biomni 多面板科研图复现，PowerPoint 实际渲染](docs/images/biomni-reconstruction.png)

**127 段可编辑文字 · 25 组图形组件 · SVG + 原生 PPTX**

案例：Huang 等，[*Biomni* 图 1](https://doi.org/10.1101/2025.05.30.656746)，CC BY 4.0，使用 fig-cos 重建。[图件来源与署名](docs/GALLERY.md)。

### 02 · 改文字、换配色、移动组件

标题换成自己的研究分组，重点细胞改成演示配色，再把组件挪到更合适的位置。科研图可以跟着你的论文和汇报一起迭代。

![可编辑示例：修改标签、调整配色、移动细胞组件](docs/images/editable-in-action.gif)

[打开修改后的 SVG](examples/editing/after.svg) · [下载可编辑 PPT](examples/editing/after.pptx) · [查看编辑示例](examples/editing/README.md)

### 03 · 从一个想法，开始一张新图

需要一段 DNA、一个细胞簇、一组流程关系？告诉 Agent 你想表达的内容，用文字、几何和科学组件搭建版式，再逐步完善。

![DNA 与细胞组件示例，PowerPoint 实际渲染](docs/images/editable-components.png)

[场景文件](examples/procedural/scene.json) · [SVG](examples/procedural/editable.svg) · [PowerPoint](examples/procedural/editable.pptx)

## 从参考图到成品，三步就绪

**① 给参考**：附上图片或 PDF，说明用途和想保留的部分。  
**② 说需求**：复现整图、修改局部，或以它为起点继续设计。  
**③ 接着改**：拿到 SVG、PPT 和预览，继续调整文字、组件与版式。

## Quick start：安装到你的 Agent

先克隆仓库：

```bash
git clone https://github.com/irrrricardo/fig-cos.git
cd fig-cos
```

### Codex

```bash
python tools/install_skill.py --agent codex
```

安装后附上参考图，直接调用：

```text
$fig-cos 把这张科研图复现成可编辑 SVG 和 PowerPoint。
```

也可以直接让 Codex 的 Skill Installer 安装：

```text
$skill-installer install https://github.com/irrrricardo/fig-cos/tree/main/skills/fig-cos
```

### Claude Code

```bash
python tools/install_skill.py --agent claude
```

附图后调用：

```text
/fig-cos 复现这张图，保留结构和布局，交付可编辑 PPT。
```

### DeepSeek Harness

```bash
python tools/install_skill.py --agent deepseek-harness
```

附图并告诉 Agent：

```text
请加载 fig-cos Skill，把这张参考图重建成可编辑 SVG 和 PPT。
```

### 安装目录

| Agent | 用户级安装位置 | 项目级安装位置 |
| --- | --- | --- |
| Codex | `~/.agents/skills/fig-cos/` | `<项目>/.agents/skills/fig-cos/` |
| Claude Code | `~/.claude/skills/fig-cos/` | `<项目>/.claude/skills/fig-cos/` |
| DeepSeek Harness | `~/.dsh/skills/fig-cos/` | `<项目>/.dsh/skills/fig-cos/` |

项目内安装可加 `--scope project --project-dir 你的项目目录`。也可从 [Releases](https://github.com/irrrricardo/fig-cos/releases) 下载技能包，解压后把完整 `fig-cos` 文件夹放入对应目录。

安装位置、会话发现与环境准备见 [Agent 安装指南](docs/AGENTS.md) 和 [运行环境](docs/COMPATIBILITY.md)。

## 让每次修改，都接得上

- **文字独立可改**：标题、标签和说明作为真实文字保留。
- **图形按组件组织**：移动一个模块，或继续编辑它的路径。
- **版式沿用原图**：从你选中的形象、结构和位置出发。
- **成果方便交接**：SVG、PowerPoint、预览和场景文件一起带走。
- **绘图与导出本地运行**：配合 Agent 完成从看图到交付的流程。

[核心 Skill](skills/fig-cos/SKILL.md) · [工作流程](docs/WORKFLOW.md) · [质量规范](docs/QUALITY.md) · [辅助 CLI](docs/CLI.md) · [参与开发](CONTRIBUTING.md)

## 致谢与许可

项目代码采用 MIT；图库与示例图件各自保留来源和许可。原生图形导出使用了 [yrui-cmd/Cell](https://github.com/yrui-cmd/Cell) 的公开 MIT 代码。完整署名见 [第三方声明](THIRD_PARTY_NOTICES.md) 与 [展示说明](docs/GALLERY.md)。
