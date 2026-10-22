# 兼容与安装说明

核对日期：2026-10-22。核心遵循 [Agent Skills 规范](https://agentskills.io/specification)：`SKILL.md` 使用标准的 `name`、`description` 前言，详细规则放在 `references/`。

本页区分技能格式、目录安装和实际剪辑环境。官方文档核对与本地打包测试，不等于已经逐一运行六种客户端完成剪辑。

## 本地目录与调用

下表路径都需在末尾添加 `tf-narration-finecut/SKILL.md`：

| 客户端 | 个人技能目录 | 项目技能目录 | 调用 |
|---|---|---|---|
| Codex | `~/.agents/skills/` | `.agents/skills/` | `$tf-narration-finecut`，也可按描述匹配 |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | `/tf-narration-finecut`，或按描述匹配 |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` | 明确要求使用技能；斜杠入口取决于客户端版本 |
| Cursor Agent | `~/.cursor/skills/` | `.cursor/skills/` | 输入 `/` 选择技能 |
| Copilot CLI / VS Code | `~/.copilot/skills/` | `.github/skills/` | `/tf-narration-finecut` |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` | 要求加载技能，由原生 `skill` 工具读取 |

Gemini CLI、Cursor、Copilot 与 OpenCode 还支持共享 `.agents/skills/` 和 `~/.agents/skills/`；安装器的 `shared` 参数写入这里。Claude Code 使用表中原生目录。不要为同一客户端重复安装多个同名副本。

Codex 的旧版或既有配置可能仍使用 `~/.codex/skills/` 或 `$CODEX_HOME/skills/`。本仓库按照当前官方文档默认写入 `.agents/skills/`；如你的版本使用旧目录，可显式指定完整目标：

```bash
python3 tools/skill_package.py install --agent codex --destination "~/.codex/skills/tf-narration-finecut"
```

安装器保留 `agents/openai.yaml` 为 Codex 提供显示信息，其他宿主的核心规则不依赖这个文件。没有添加宿主专用授权字段或自动执行钩子。

## 使用仓库安装器

需要 Python 3.10 或更新版本，无额外 Python 包依赖：

```bash
git clone https://github.com/yulian686899-wq/TF-Narration-Finecut.git tf-narration-finecut
cd tf-narration-finecut
python3 tools/skill_package.py install --agent claude-code --scope user --dry-run
python3 tools/skill_package.py install --agent claude-code --scope user
```

`--agent` 支持 `codex`、`claude-code`、`gemini-cli`、`cursor`、`copilot`、`opencode`、`shared`。默认范围是个人目录；项目安装使用 `--scope project --project /path/to/project`。

安装器只复制六个技能文件，保留统一的文件夹名。已存在的目标目录会拒绝覆盖，防止丢失使用者补充的规则和反馈。更新前先保存本地修改，再自行决定如何替换。它不会修改 `CLAUDE.md`、`GEMINI.md`、`AGENTS.md` 或任何全局客户端配置。

Windows 可用本机的 Python 启动命令替代 `python3`。安装器支持本机路径处理；Windows/Linux 上的 MLX 转写方案仍未验证。

## 原生安装与重新加载

Codex 可向内置 `$skill-installer` 提供本仓库地址，要求安装根目录技能并命名为 `tf-narration-finecut`。未显示时检查扫描目录，必要时重启客户端。

Claude Code 的目录安装完成后使用 `/tf-narration-finecut`。普通 ZIP 需先解压到对应目录，不提供未经核对的 ZIP 一键导入命令。

Gemini CLI 可使用原生安装器：

```bash
gemini skills install https://github.com/yulian686899-wq/TF-Narration-Finecut.git --scope user
```

也可安装本地 `.skill` 包：

```bash
gemini skills install ./tf-narration-finecut.skill --scope user
```

在会话内用 `/skills list`、`/skills reload` 检查与重载。普通 `.zip` 与 `.skill` 内容一致，但 Gemini 安装器按 `.skill` 后缀识别压缩包，不要直接传普通 ZIP。工作区技能还需满足客户端的信任设置。

Copilot CLI 可用 `/skills reload`、`/skills info tf-narration-finecut` 检查；VS Code 在聊天中输入 `/` 选择技能。这里的支持范围指本地 CLI / VS Code，不代表 Copilot 云端能直接访问你的电脑视频。

Cursor 在 Agent 中输入 `/` 查看技能。个人目录的技能是否同步到远程或云环境，由 Cursor 当前同步设置决定；本地安装不会自动证明云端可用。

OpenCode 可以明确要求“使用 tf-narration-finecut”，由模型通过原生 skill 工具加载。本包未启用 OpenCode 的可选斜杠元数据，不承诺默认出现 `/tf-narration-finecut` 命令。

## 不支持技能目录的智能体

从发布页下载 `tf-narration-finecut.instructions.md`，作为完整指令交给宿主。它合并了正文和四份参考规则，不依赖再打开相对文件。

这是一种手动提供规则的方式，不是对 Dify、Coze 或任意聊天网页的原生插件适配。宿主需有文件、命令执行和转写能力才能执行完整剪辑；仅能聊天时应输出建议，不能报告已经导出视频。反馈的长期保存也取决于宿主提供的存储。

## 运行环境和测试范围

所有客户端都需要能读到原片并执行 FFmpeg/ffprobe、Python 与本地转写工具，遵守各自的工具授权。现有转写方案沿用 Apple Silicon 环境中的 mlx-whisper，未新增云端 ASR 或跨系统转写实现。

本仓库的自动测试覆盖个人/项目目录映射、七种安装目标在临时目录中的写入、拒绝覆盖、dry-run、标准 ZIP/.skill 内容、校验值和单文件规则完整性。未将文件安装进用户的各家真实技能目录，也未逐客户端完成识别、剪辑与导出。

打包和测试：

```bash
python3 -m unittest discover -s tests -v
python3 tools/skill_package.py build
```

产物默认在 `dist/`，不进入 Git 历史。

## 官方依据

- [Agent Skills 规范](https://agentskills.io/specification)
- [OpenAI 官方技能说明](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Gemini CLI Skills](https://geminicli.com/docs/cli/skills/)
- [Gemini CLI 创建与打包说明](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/creating-skills.md)
- [Cursor Agent Skills](https://cursor.com/docs/skills)
- [GitHub Copilot CLI Skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [OpenCode Skills](https://opencode.ai/docs/skills/)
