# fig-cos

**一个用于科研图片复现的 Agent Skill，交付可编辑 SVG 与原生 PowerPoint。**

[English](README.md) · [安装 Skill](#quick-start安装到你的-agent) · [SKILL.md](skills/fig-cos/SKILL.md) · [展示与署名](docs/GALLERY.md) · [质量规范](docs/QUALITY.md)

**把 Skill 安装到 Codex、Claude Code 或 DeepSeek Harness，附上参考图，再让 Agent 使用它完成复现。**

默认采用 **Previous local tracing**：沿原图分组件局部描摹，保留形象、结构和位置，文字、框与箭头独立重建。模糊图片也沿用这条路线，不自动换成通用图标、另一种蛋白折叠或 AI 重画。

本项目的核心是 **[skills/fig-cos/ 技能包](skills/fig-cos/)**。Python 脚本是技能的辅助执行工具，CLI 是可选开发入口；安装 Skill 本身不要求先安装一个 Python 应用，也没有额外的付费绘图后端或内置模型 API 客户端。

## 过去完成的效果

![Biomni 参考图复现，历史 PowerPoint 实际显示](docs/images/biomni-reconstruction.png)

历史交付含 127 个真实文字对象、3,978 个原生对象，无嵌入位图。科学插画来自源图局部恢复/描摹，部分通用 UI 图标及论文缩略图使用替代示意；不宣称像素一致或语义图层恢复。改编自 Huang 等人的 *Biomni* 图 1，[bioRxiv 2025](https://doi.org/10.1101/2025.05.30.656746)，CC BY 4.0。[修改与署名](docs/GALLERY.md)。

![原图、早期不合适的图库替换、源图细节恢复的对照](docs/images/source-details.png)

中列仅作为早期替换不够贴合的对照；默认保留原图形象。论文衍生部分沿用同一来源与许可，图库部分单独署名。

![原创 DNA 和细胞可编辑组件，历史 PowerPoint 实际显示](docs/images/editable-components.png)

原创程序示意，不代表实测分子或细胞结构。[场景](examples/procedural/scene.json) · [SVG](examples/procedural/editable.svg) · [PPT](examples/procedural/editable.pptx)。

## Quick start：安装到你的 Agent

### Codex

在 Codex 中让 Skill Installer 安装：

```text
$skill-installer install https://github.com/irrrricardo/fig-cos/tree/main/skills/fig-cos
```

也可以先克隆仓库，再用仅复制文件的安装脚本：

```bash
git clone https://github.com/irrrricardo/fig-cos.git
cd fig-cos
python tools/install_skill.py --agent codex
```

默认安装到 `~/.agents/skills/fig-cos/`。附上参考图后调用：

```text
$fig-cos 按原图局部描摹复现这张图，保留组件形象、结构和版式，输出可编辑 SVG 与 PPT。
```

Codex 会自动发现技能；若未显示，重启会话。[官方说明](https://learn.chatgpt.com/docs/build-skills)。

### Claude Code

在已克隆的仓库中执行：

```bash
python tools/install_skill.py --agent claude
```

默认安装到 `~/.claude/skills/fig-cos/`。附图后调用：

```text
/fig-cos 按原图复现，保留原有组件和布局，输出可编辑 SVG 与 PowerPoint。
```

[Claude Code 的技能目录与调用方式](https://code.claude.com/docs/en/skills)。

### DeepSeek Harness

在已克隆的仓库中执行：

```bash
python tools/install_skill.py --agent deepseek-harness
```

默认安装到 `~/.dsh/skills/fig-cos/`，设置了 `DSH_HOME` 时跟随该配置。Harness 启用本地文件系统技能提供器后，附图并提示：

```text
请加载并使用 fig-cos Skill，按原图局部描摹复现这张图片，保留形象、结构与版式，交付可编辑 SVG 和 PPT。
```

这里指 DeepSeek 官方 **Harness**，不是网页聊天或单独的模型 API。[官方技能提供器说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)。

### 项目内安装 / 手动安装

安装脚本可加 `--scope project --project-dir 你的项目目录`。或从 [Releases](https://github.com/irrrricardo/fig-cos/releases) 下载 Skill ZIP，解压后将完整 `fig-cos` 文件夹放入：

| Agent | 用户级目录 | 项目级目录 |
| --- | --- | --- |
| Codex | `~/.agents/skills/fig-cos/` | `<项目>/.agents/skills/fig-cos/` |
| Claude Code | `~/.claude/skills/fig-cos/` | `<项目>/.claude/skills/fig-cos/` |
| DeepSeek Harness | `~/.dsh/skills/fig-cos/` | `<项目>/.dsh/skills/fig-cos/` |

**复制整个技能包，不要只复制 SKILL.md。** 安装脚本仅用 Python 标准库、拒绝覆盖已有技能，不会安装依赖或修改 Agent 的配置。已有本机 `$fig_cos` 调用可继续保留。

## Agent 的运行条件

Agent 需要能读取文件、运行 Python，并能看图或接收明确的文字/布局清单。实际调用辅助脚本时，可让 Agent 在自己的执行环境中准备技能包内的 `requirements.txt`。Ubuntu/glibc Linux 使用 Python 3.11/3.12；Windows CI 覆盖 3.11/3.13。CairoSVG 可能需要 Cairo 运行库和合适字体。[兼容性](docs/COMPATIBILITY.md)。

生成原生 PPTX 不需要安装 Office；实际 PowerPoint 预览需要 Windows、桌面 PowerPoint 及可选 COM 依赖。PDF 局部恢复的 PyMuPDF 具有 AGPL/商业双许可，基本截图描摹与导出不需要它。上面的安装目录按官方文档核对，未声称已在每个 Agent 中完成独立端到端视觉验收。

## 使用规范

- 参考图默认局部描摹，文字、框、箭头、组件组合保持独立可编辑。
- 图库替换、AI 重画、通用组件和实验性精绘，仅在明确要求时采用。
- 先核对原有形象、结构、连接、遮挡与布局，再看光滑度。路径数量、导出成功都不是质量结论。
- 不把可编辑路径说成恢复了原始透明图层、分子身份、语义部件或隐藏像素。
- 按要求交付 SVG/PPT、预览、场景或代码、来源及近似说明；未查看实际 PowerPoint 渲染时如实标明。

[工作流程](docs/WORKFLOW.md) · [质量规范](docs/QUALITY.md) · [接入说明](docs/AGENTS.md)。没有内置 OCR/超分/生成模型，也没有附带 MCP 服务。

## 辅助 CLI 与开发

需要单独调试脚本的开发者可执行 `python -m pip install .`，获得 `fig-cos doctor / trace / compose / export` 等入口。**这是辅助工具，不是用户安装和使用 Skill 的主要方式。** 见 [CLI 文档](docs/CLI.md) 和 [贡献规范](CONTRIBUTING.md)。

自写代码采用 MIT；供应代码、图库和论文衍生展示各自保留许可与署名，见 [第三方声明](THIRD_PARTY_NOTICES.md)。
