# Personalized Podcast — 工作痛点、使用方法与 Skill 详解

## 一、它解决了什么工作痛点？

### 痛点 1：信息过载，没时间看
每天大量的 Newsletter、长文、研究报告、技术文档堆积如山。坐在电脑前一篇篇读完不现实，但不读又怕错过关键信息。

**解法：** 把任何文本/文件/URL 扔进去，自动生成一期双人对话播客。通勤、散步、做饭时听完，零碎时间变学习时间。

### 痛点 2：每天的 AI/科技新闻跟不上
AI 领域一天一个大新闻，没精力逐条刷。

**解法：** 内置每日新闻自动抓取（7 大 RSS 源），一键生成"今日 AI 新闻播客"，上班路上就能听完当天最重要的科技动态。

### 痛点 3：会议开完就忘，决策质量无法复盘
会议纪要只是记了"说了什么"，但没有人帮你分析"决策逻辑对不对"、"沟通方式好不好"、"有没有盲区"。

**解法：** 把会议记录丢进去，两个 AI 主持人从 **6 个专业维度** 深度复盘你的决策和表现——这种第三方视角的犀利分析，日常工作中几乎不可能得到。

### 痛点 4：想了解别人对自己的客观印象
简历、周报、历史发言——你写了很多内容，但很难从第三方视角审视自己。

**解法：** 把个人内容（简历、会议发言、日记）喂进去，让两个主持人像"旁观者"一样讨论你——你的思维模式、沟通风格、决策习惯，角度非常新颖。

### 痛点 5：内容输出形式单一
写了一篇文章、整理了一份笔记，想快速转成音频分享给团队或自己回听，没有便捷方案。

**解法：** 一条命令生成 MP3，还能通过 RSS 订阅推送到 Apple Podcasts / Spotify / Overcast 等播客应用。

---

## 二、核心场景

### 场景 A：每日 AI 新闻播客（自动化）

从 7 个 RSS 源自动抓取 AI/科技新闻，生成双人对话播客：

**数据源：** Hacker News、TechCrunch AI、The Verge AI、Ars Technica、MIT Tech Review、机器之心、量子位

**一键运行：**
```bash
~/.personalized-podcast/venv/bin/python scripts/daily_podcast.py
```

**设置每天早上 8:00 自动运行（macOS）：**
```bash
cp scripts/com.podcast.daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.podcast.daily.plist
```

**也可以单独抓新闻看看：**
```bash
~/.personalized-podcast/venv/bin/python scripts/fetch_news.py --days 1 --max 10
```

### 场景 B：会议决策复盘（6 维度深度分析）

这是最有价值的场景。不是简单地"听一遍会议记录"，而是从 **6 个专业维度** 结构化分析你的决策和表现：

| 维度 | 分析什么 |
|------|---------|
| **决策质量** | 逻辑链是否完整？数据驱动还是拍脑袋？有没有考虑替代方案？ |
| **思维模式** | 有没有认知偏见（确认偏误、锚定效应、沉没成本）？战略层还是陷入细节？ |
| **沟通风格** | 表达清晰还是模糊？怎么说服人？有没有真正在听别人说话？ |
| **信息盲区** | 忽略了什么？谁的发言没被重视？哪些该问的问题没问？ |
| **影响力与领导力** | 主导还是被动？给团队空间了吗？共识是真的还是表面的？ |
| **行动导向** | 有没有清晰的下一步？有责任人和时间点吗？会议投入产出比如何？ |

**两位主持人分工：**
- **Alex** — 同事视角：捕捉微妙的人际信号和沟通细节，"如果我是他的同事，我会怎么看他"
- **Sam** — 教练视角：拆解决策逻辑和思维模式，"如果我是他的顾问，我会给什么建议"

**用法：**
```
/podcast read ~/meeting.txt --prompt PROMPT_MEETING.md
```

### 场景 C：通用内容播客

把任何内容变成播客：

| 场景 | 命令 |
|------|------|
| 听一篇文章 | `/podcast read ~/Downloads/article.txt` |
| 听一个网页 | `/podcast https://some-article-url.com` |
| 直接粘贴内容 | `/podcast 这里粘贴你想听的文字内容...` |
| 分析简历 | `/podcast read ~/Documents/resume.pdf 让主持人分析我的职业轨迹` |
| 辩论模式 | `/podcast read ~/notes.md 做成乐观派 vs 怀疑派的辩论` |
| 独白叙述 | `/podcast solo narrator，帮我走读这篇论文` |

---

## 三、快速开始

### 前提条件
| 依赖 | 说明 |
|------|------|
| Python 3.10+ | 运行脚本 |
| ffmpeg | 音频处理（`brew install ffmpeg`）|
| Fish Audio 账号 | 免费 TTS 服务，200 万+声音可选 |

### 安装部署

```bash
# 1. 克隆项目
gh repo clone zarazhangrui/personalized-podcast-skill ~/.claude/skills/personalized-podcast

# 2. 创建数据目录 & 虚拟环境
mkdir -p ~/.personalized-podcast/{scripts_output,episodes,logs}
python3 -m venv ~/.personalized-podcast/venv
~/.personalized-podcast/venv/bin/pip install httpx pydub pyyaml python-dotenv jinja2 audioop-lts

# 3. 复制默认配置
cp ~/.claude/skills/personalized-podcast/config/config.example.yaml ~/.personalized-podcast/config.yaml

# 4. 配置 API Key
echo "FISH_API_KEY=你的Fish_Audio_API_Key" > ~/.personalized-podcast/.env
```

### 自定义你的播客

- **改主持人风格：** 编辑 `PROMPT.md`（通用）或 `PROMPT_MEETING.md`（会议复盘）
- **换声音：** 在 [fish.audio/discovery](https://fish.audio/discovery/) 找喜欢的声音，把 ID 填入 `config.yaml`
- **改节目名称/语气：** 编辑 `config.yaml` 中的 `show_name` 和 `tone` 字段

---

## 四、Skill 架构详解

### 整体流程

```
用户输入内容（文本/文件/URL/会议记录）
        │
        ▼
  选择 Prompt 模板（通用 / 新闻 / 会议复盘）
        │
        ▼
  AI 按模板维度分析内容，生成双人对话脚本（JSON）
        │
        ▼
  Fish Audio 为每句话生成语音（不同角色不同声音）
        │
        ▼
  pydub + ffmpeg 拼接音频，加停顿和淡入淡出
        │
        ▼
  输出 MP3，自动播放
```

### 目录结构

```
~/.claude/skills/personalized-podcast/    # Skill 本体
├── SKILL.md                              # 给 AI Agent 的完整指令
├── PROMPT.md                             # 通用播客 Prompt（双人聊天风格）
├── PROMPT_MEETING.md                     # 会议决策复盘 Prompt（6 维度分析）
├── config/
│   └── config.example.yaml               # 默认配置模板
├── scripts/
│   ├── speak.py                          # TTS 生成 + 音频拼接
│   ├── fetch_news.py                     # 每日 AI/科技新闻抓取（7 大 RSS 源）
│   ├── daily_podcast.py                  # 每日新闻播客全自动流程
│   ├── publish.py                        # 发布到 GitHub Pages（可选）
│   ├── bootstrap.py                      # 首次初始化（可选）
│   ├── utils.py                          # 配置加载、日志、环境变量工具
│   └── com.podcast.daily.plist           # macOS 定时任务配置
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
| **PROMPT.md** | 通用播客 Prompt，两个朋友聊天风格，可改成辩论、采访、独白等 |
| **PROMPT_MEETING.md** | 会议复盘专用 Prompt，6 维度结构化分析决策质量、思维模式、沟通风格等 |
| **fetch_news.py** | 从 7 个 RSS 源抓取 AI/科技新闻，关键词过滤 + 去重 |
| **daily_podcast.py** | 全自动流程：抓新闻 → 生成脚本 → TTS 音频 → 播放 |
| **speak.py** | 核心引擎：读取 JSON 脚本 → 调用 Fish Audio API → 拼接音频 → 输出 MP3 |
| **publish.py** | 可选：将 MP3 推送到 GitHub Pages，更新 RSS Feed |

### 默认主持人

| 角色 | 名字 | 性格 | 声音 |
|------|------|------|------|
| Speaker A | Alex | 好奇、有活力，负责引入话题和提问 | 自然男声 |
| Speaker B | Sam | 分析型、机智，负责深入讨论和给出观点 | 温暖女声 |

### RSS 订阅（可选）

| 应用 | 订阅方式 |
|------|---------|
| Apple Podcasts (Mac) | 菜单 File > Add a Show by URL |
| Apple Podcasts (iPhone) | 资料库 > 编辑 > Add a Show by URL |
| Overcast | 右上角 "+" > Add URL |
| Spotify | 需通过 podcasters.spotify.com 提交（公开） |
| Snipd | Home > Podcasts > 右上角三点 > Add RSS |

### 常见问题排查

| 问题 | 解决方案 |
|------|---------|
| API key not found | 检查 `~/.personalized-podcast/.env` 是否有有效的 `FISH_API_KEY` |
| ffmpeg not installed | `brew install ffmpeg` (macOS) 或 `sudo apt install ffmpeg` (Linux) |
| TTS quota exceeded | Fish Audio 免费额度用完，等月度重置或升级付费计划 |
| gh not authenticated | `gh auth login` 登录 GitHub CLI |
