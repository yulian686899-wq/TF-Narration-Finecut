# TF-Narration-Finecut

**让 Codex 按明确规则精剪中文口播：清理重复起句、卡壳和多余气口，保留说话者的观点与补充。**

A Codex skill for fine-cutting talking-head videos, preserving the speaker's ideas, and refining edits through review feedback.

当前版本：**v0.1.0 · 规则与工具调用指南**。

## 适合什么场景

你录了几段口播，有重录、说到一半重来、长等待，或者完整句前面多了几个字，希望 Codex 把它们剪顺，同时保留参考稿之外的有效补充。

本项目特别关注这类问题：

> 我现在……我现在介绍这个功能。

清理前一次失败起句，保留后面的完整表达。相似开头如果各有新信息，则分别保留。

## 四个部分

| 部分 | 内容 |
|---|---|
| 怎么剪 | 重复、残句与改口、口误重说、英文卡壳、口头禅的判断和句首残词检查。 |
| 工具调用 | 本地转写、Codex 内容取舍、Python 波形辅助、FFmpeg 同步剪辑与声音处理。 |
| 验收标准 | 观点与限定保留、字音完整、衔接自然、音量统一、画面声音同步。 |
| 审核复盘 | 接收问题标注，回查原片、生成修正版，分开维护长期偏好、确认案例和待验证发现。 |

## 安装到 Codex

在 Codex 中调用内置安装技能：

```text
使用 $skill-installer，从 https://github.com/yulian686899-wq/TF-Narration-Finecut
安装仓库根目录的技能，名称设为 tf-narration-finecut。
```

安装目录应包含本仓库的 `SKILL.md`、`agents/` 和 `references/`。安装完成后，在技能选择器中检查 `tf-narration-finecut`；如果尚未显示，重启 Codex 后再检查。

参考 [OpenAI 官方技能说明](https://learn.chatgpt.com/docs/build-skills)。

## 使用示例

```text
用 $tf-narration-finecut 精剪这些口播视频。

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

- Codex：理解内容、作剪辑判断、调用工具并记录依据。
- FFmpeg / ffprobe：原片检查、同步裁切、拼接、声音处理和导出检查。
- Python / NumPy：波形辅助及项目记录。
- mlx-whisper 与已有本地 Whisper 模型：带时间的转写。

当前本地转写流程沿用 macOS Apple Silicon 环境。其他系统的等价转写适配尚未验证。安装这个 skill 不会自动安装上述工具或下载语音模型。

默认响度目标约 -16 LUFS，导出真峰值不高于 -1 dBTP；这些是可按项目调整的默认值，不是各平台的统一要求。比例、帧率和分辨率以当前任务要求为准。

## 当前能力

这是由 Codex 调度现有工具的技能规则包，没有自带独立的一键剪辑引擎。右侧网页审核工作区、本地标注服务、自动唤醒和 Studio 适配尚未实现。目前通过聊天中的时间范围与备注接收返修意见。

预期交付包括成片、内容与切点对照、检查结果和尚需审核的位置。语音转写、波形和媒体检查各有用途；它们不等于逐字听审，也不保证零误删。

本版完成了技能结构、内部引用、名称与界面配置检查。发布包未进行独立安装后的端到端视频剪辑实测；没有附带私人原片、转写或准确率数字。

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
└── .github/ISSUE_TEMPLATE/
```

## 反馈与参与

通过 [Issues](https://github.com/yulian686899-wq/TF-Narration-Finecut/issues) 提交问题。请说明版本、环境、问题范围、实际表现和预期处理；可以使用脱敏或虚构台词复现，不必公开私人录音。

规则修改请参考 [贡献说明](CONTRIBUTING.md)。版本变化见 [更新记录](CHANGELOG.md)。

## 来源与许可证状态

方法整理参考了 [成峰口播剪辑技能](https://github.com/Agentchengfeng/chengfeng-videocut-skills) 的分类判断思路，并结合创作者实际剪辑反馈。本仓库未包含其代码、模型、运行时或 Studio。

当前尚未指定许可证；后续选定后会在仓库根目录添加 `LICENSE`。公开可见与开源授权需要分开确认，参考 [GitHub 许可证说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)。
