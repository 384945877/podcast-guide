# Personalized Podcast

## 一、它解决了什么工作痛点？

### 痛点 1：信息过载，没时间看
每天大量的 Newsletter、长文、研究报告、技术文档堆积如山。坐在电脑前一篇篇读完不现实，但不读又怕错过关键信息。

**解法：** 把任何文本/文件/URL 扔进去，自动生成一期双人对话播客。通勤、散步、做饭时听完，零碎时间变学习时间。

### 痛点 2：会议记录/文档只能看不能"听"
会议纪要、项目文档、周报月报——都是干巴巴的文字，回顾起来效率低。

**解法：** 把会议记录丢进去，两个 AI 主持人用聊天的语气帮你复盘要点，比自己再看一遍有趣且高效。

### 痛点 3：想了解别人对自己的客观印象
简历、周报、历史发言——你写了很多内容，但很难从第三方视角审视自己。

**解法：** 把个人内容（简历、会议发言、日记）喂进去，让两个主持人像"旁观者"一样讨论你——你的思维模式、沟通风格、决策习惯，角度非常新颖。

### 痛点 4：内容输出形式单一
写了一篇文章、整理了一份笔记，想快速转成音频分享给团队或自己回听，没有便捷方案。

**解法：** 一条命令生成 MP3，还能通过 RSS 订阅推送到 Apple Podcasts / Spotify / Overcast 等播客应用。

---

## 二、使用方法

### 前提条件
| 依赖 | 说明 |
|------|------|
| Python 3.10+ | 运行脚本 |
| ffmpeg | 音频处理（`brew install ffmpeg`）|
| Fish Audio 账号 | 免费 TTS 服务，200 万+声音可选 |

### 快速开始

**1. 安装 Skill**
```bash
gh repo clone zarazhangrui/personalized-podcast-skill ~/.claude/skills/personalized-podcast
```

**2. 首次部署（自动完成或手动执行）**
```bash
# 创建数据目录
mkdir -p ~/.personalized-podcast/{scripts_output,episodes,logs}

# 创建虚拟环境 & 安装依赖
python3 -m venv ~/.personalized-podcast/venv
~/.personalized-podcast/venv/bin/pip install httpx pydub pyyaml python-dotenv jinja2 audioop-lts

# 复制默认配置
cp ~/.claude/skills/personalized-podcast/config/config.example.yaml ~/.personalized-podcast/config.yaml

# 配置 API Key（替换为你的真实 Key）
echo "FISH_API_KEY=你的Fish_Audio_API_Key" > ~/.personalized-podcast/.env
```

**3. 生成播客**
```
/podcast <粘贴内容、指定文件、或给一个 URL>
```

### 常用命令示例

| 场景 | 命令 |
|------|------|
| 听一篇文章 | `/podcast read ~/Downloads/article.txt` |
| 听一个网页 | `/podcast https://some-article-url.com` |
| 直接粘贴内容 | `/podcast 这里粘贴你想听的文字内容...` |
| 分析简历 | `/podcast read ~/Documents/resume.pdf 让主持人分析我的职业轨迹` |
| 复盘会议 | `/podcast read ~/meeting.txt 让主持人旁听并分享对我的印象` |
| 辩论模式 | `/podcast read ~/notes.md 做成乐观派 vs 怀疑派的辩论` |
| 新闻播报 | `/podcast 逐条朗读并讨论这些新闻...` |
| 独白叙述 | `/podcast solo narrator，帮我走读这篇论文` |

### 自定义你的播客

- **改主持人风格：** 编辑 `~/.claude/skills/personalized-podcast/PROMPT.md`
- **换声音：** 在 [fish.audio/discovery](https://fish.audio/discovery/) 找喜欢的声音，把 ID 填入 `~/.personalized-podcast/config.yaml` 的 `host_a_voice_id` / `host_b_voice_id`
- **改节目名称/语气：** 编辑 `config.yaml` 中的 `show_name` 和 `tone` 字段

### RSS 订阅（可选）

生成的播客可以通过 GitHub Pages 发布 RSS Feed，订阅到你常用的播客应用：

| 应用 | 订阅方式 |
|------|---------|
| Apple Podcasts (Mac) | 菜单 File > Add a Show by URL |
| Apple Podcasts (iPhone) | 资料库 > 编辑 > Add a Show by URL |
| Overcast | 右上角 "+" > Add URL |
| Spotify | 需通过 podcasters.spotify.com 提交（公开） |
| Snipd | Home > Podcasts > 右上角三点 > Add RSS |

---

## 三、Skill 架构详解

### 整体流程

```
用户输入内容（文本/文件/URL）
        │
        ▼
  AI 阅读内容，按 PROMPT.md 写双人对话脚本（JSON）
        │
        ▼
  Fish Audio 为每句话生成语音（不同角色不同声音）
        │
        ▼
  pydub + ffmpeg 拼接音频，加停顿和淡入淡出
        │
        ▼
  输出 MP3，自动播放
        │
        ▼
  （可选）发布到 GitHub Pages RSS Feed
```

### 目录结构

```
~/.claude/skills/personalized-podcast/    # Skill 本体
├── SKILL.md                              # 给 AI Agent 的完整指令
├── PROMPT.md                             # 播客脚本生成 Prompt（风格/结构/格式）
├── README.md                             # 项目说明
├── config/
│   └── config.example.yaml               # 默认配置模板
├── scripts/
│   ├── speak.py                          # TTS 生成 + 音频拼接
│   ├── publish.py                        # 发布到 GitHub Pages（可选）
│   ├── bootstrap.py                      # 首次 Repo 初始化（可选）
│   └── utils.py                          # 配置加载、日志、环境变量工具
├── templates/
│   └── feed_template.xml                 # RSS Feed 模板
└── examples/                             # 示例文件

~/.personalized-podcast/                  # 用户数据（自动创建）
├── config.yaml                           # 你的配置
├── .env                                  # Fish Audio API Key
├── scripts_output/                       # 生成的对话脚本（JSON）
├── episodes/                             # 生成的 MP3 文件
└── logs/                                 # 运行日志
```

### 核心文件说明

| 文件 | 作用 |
|------|------|
| **SKILL.md** | AI Agent 的"操作手册"——首次设置、生成流程、RSS 配置、故障排查全在这里 |
| **PROMPT.md** | 控制播客风格的核心 Prompt。默认是两个朋友聊天风格，可改成辩论、采访、独白等 |
| **speak.py** | 核心脚本：读取 JSON 脚本 → 调用 Fish Audio API → 拼接音频 → 输出 MP3 |
| **publish.py** | 可选：将 MP3 推送到 GitHub Pages 仓库，更新 RSS Feed |
| **utils.py** | 工具集：加载配置、加载 .env、日志设置、状态管理 |
| **config.yaml** | 节目名称、语气、语言、声音 ID、RSS 配置、保留集数 |

### 默认主持人

| 角色 | 名字 | 性格 | 声音 |
|------|------|------|------|
| Speaker A | Alex | 好奇、有活力，负责引入话题和提问 | 自然男声 |
| Speaker B | Sam | 分析型、机智，负责深入讨论和给出观点 | 温暖女声 |

### 常见问题排查

| 问题 | 解决方案 |
|------|---------|
| API key not found | 检查 `~/.personalized-podcast/.env` 是否有有效的 `FISH_API_KEY` |
| ffmpeg not installed | `brew install ffmpeg` (macOS) 或 `sudo apt install ffmpeg` (Linux) |
| TTS quota exceeded | Fish Audio 免费额度用完，等月度重置或升级付费计划 |
| gh not authenticated | `gh auth login` 登录 GitHub CLI |
