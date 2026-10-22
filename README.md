# TF-Narration-Finecut

**让支持 Agent Skills 的智能体按明确规则精剪中文口播：清理重复起句、卡壳和多余气口，保留说话者的观点与补充。**

A portable Agent Skill for fine-cutting talking-head videos, preserving the speaker's ideas, and refining edits through review feedback.

当前版本：**v0.2.0 · 多智能体格式与安装适配**。

## 适合什么场景

你录了几段口播，有重录、说到一半重来、长等待，或者完整句前面多了几个字，希望智能体把它们剪顺，同时保留参考稿之外的有效补充。

本项目特别关注这类问题：

> 我现在……我现在介绍这个功能。

清理前一次失败起句，保留后面的完整表达。相似开头如果各有新信息，则分别保留。

## 四个部分

| 部分 | 内容 |
|---|---|
| 怎么剪 | 重复、残句与改口、口误重说、英文卡壳、口头禅的判断和句首残词检查。 |
| 工具调用 | 本地转写、当前智能体内容取舍、Python 波形辅助、FFmpeg 同步剪辑与声音处理。 |
| 验收标准 | 观点与限定保留、字音完整、衔接自然、音量统一、画面声音同步。 |
| 审核复盘 | 接收问题标注，回查原片、生成修正版，分开维护长期偏好、确认案例和待验证发现。 |

## 多智能体安装

核心只有一份 `SKILL.md` 与四份参考规则，各宿主按自己的技能目录加载。以下支持情况按官方文档核对；各客户端的完整视频剪辑尚未实测。

| 智能体 | 安装器参数 | 调用入口 |
|---|---|---|
| Codex | `codex` | `$tf-narration-finecut` |
| Claude Code | `claude-code` | `/tf-narration-finecut` |
| Gemini CLI | `gemini-cli` | 明确要求使用此技能；提供斜杠技能入口的版本也可直接选择 |
| Cursor Agent | `cursor` | 输入 `/` 选择技能 |
| GitHub Copilot CLI / VS Code | `copilot` | `/tf-narration-finecut` |
| OpenCode | `opencode` | 要求使用此技能，由原生 skill 工具加载 |

下载仓库后，用 Python 3.10 或更新版本运行安装器。例如安装到 Claude Code 的个人技能目录：

```bash
git clone https://github.com/yulian686899-wq/TF-Narration-Finecut.git tf-narration-finecut
cd tf-narration-finecut
python3 tools/skill_package.py install --agent claude-code --scope user
```

将 `claude-code` 换成上表其他参数即可。安装器只复制技能的六个文件，不下载客户端、工具或模型，不覆盖已有目录；可加 `--dry-run` 先查看目标位置。

项目级安装需要显式指定项目目录：

```bash
python3 tools/skill_package.py install --agent cursor --scope project --project /path/to/video-project
```

完整目录表、旧版 Codex 目录、Gemini 原生安装和加载检查见[兼容与安装说明](docs/COMPATIBILITY.md)。Codex 也可以继续使用内置安装技能：

```text
使用 $skill-installer，从 https://github.com/yulian686899-wq/TF-Narration-Finecut
安装仓库根目录的技能，名称设为 tf-narration-finecut。
```

安装后的目录名应为 `tf-narration-finecut`，包含 `SKILL.md`、`agents/` 和 `references/`。`agents/openai.yaml` 是 Codex 可选显示信息，其他宿主不依赖它。安装后按各客户端方式重新加载技能。

## 下载格式

[v0.2.0 发布页](https://github.com/yulian686899-wq/TF-Narration-Finecut/releases/tag/v0.2.0) 提供：

- `tf-narration-finecut.zip`：标准目录包，解压后放入对应技能目录。
- `tf-narration-finecut.skill`：相同 ZIP 内容的 `.skill` 包，可供 Gemini CLI 的原生安装器使用。
- `tf-narration-finecut.instructions.md`：合并正文和四份规则的单文件，供不能加载技能目录的智能体手动读取。
- `SHA256SUMS`：下载文件的 SHA-256 校验值。

普通聊天或自定义机器人读取单文件后，可以依规则分析已有转写；直接裁切和导出仍需要宿主另有文件与执行工具，不能据此宣称已经原生集成。

## 使用示例

```text
使用 tf-narration-finecut 精剪这些口播视频。

输入：我提供的视频文件。
参考：我提供的大纲只用于理解，以实际原声为准。
要求：保留不重复的观点和临场补充，剪掉卡壳、失败起句和多余气口。
尤其检查完整句前面有没有残留上一遍重录的字词。
输出：保存到我指定的目录，保留原片，附上切点记录和检查结果。
```

返修时，可以直接说：

```text
00:42附近，完整句之前多了一次“我现在”。
回原片核对，保留完整表达，给我修正版及这一段的前后对照。
```

这是使用说明中的假设时间和台词，不是真实剪辑案例。

## 工具与环境

- 当前智能体：理解内容、作剪辑判断、调用工具并记录依据。
- FFmpeg / ffprobe：原片检查、同步裁切、拼接、声音处理和导出检查。
- Python / NumPy：波形辅助及项目记录。
- mlx-whisper 与已有本地 Whisper 模型：带时间的转写。

当前本地转写流程沿用 macOS Apple Silicon 环境。其他系统的等价转写适配尚未验证。安装这个 skill 不会自动安装上述工具或下载语音模型。

默认响度目标约 -16 LUFS，导出真峰值不高于 -1 dBTP；这些是可按项目调整的默认值，不是各平台的统一要求。比例、帧率和分辨率以当前任务要求为准。

## 当前能力

这是由当前智能体调度现有工具的技能规则包，没有自带独立的一键剪辑引擎。网页审核工作区、本地标注服务、自动唤醒和 Studio 适配尚未实现。目前通过聊天中的时间范围与备注接收返修意见。

预期交付包括成片、内容与切点对照、检查结果和尚需审核的位置。语音转写、波形和媒体检查各有用途；它们不等于逐字听审，也不保证零误删。

本版检查技能结构、内部引用和配置，并用临时目录测试安装器、包内容和单文件导出。验证不涉及各客户端实际加载或完整剪辑，没有附带私人原片、转写或准确率数字。

## 文件结构

```text
TF-Narration-Finecut/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── how-to-cut.md
│   ├── toolchain.md
│   ├── quality-standards.md
│   └── review-and-learning.md
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── docs/COMPATIBILITY.md
├── tools/skill_package.py
├── tests/test_skill_package.py
└── .github/ISSUE_TEMPLATE/
```

## 反馈与参与

通过 [Issues](https://github.com/yulian686899-wq/TF-Narration-Finecut/issues) 提交问题。请说明版本、环境、问题范围、实际表现和预期处理；可以使用脱敏或虚构台词复现，不必公开私人录音。

规则修改请参考 [贡献说明](CONTRIBUTING.md)。版本变化见 [更新记录](CHANGELOG.md)。

## 来源与许可证状态

方法整理参考了 [成峰口播剪辑技能](https://github.com/Agentchengfeng/chengfeng-videocut-skills) 的分类判断思路，并结合创作者实际剪辑反馈。本仓库未包含其代码、模型、运行时或 Studio。

当前尚未指定许可证；后续选定后会在仓库根目录添加 `LICENSE`。公开可见与开源授权需要分开确认，参考 [GitHub 许可证说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)。
