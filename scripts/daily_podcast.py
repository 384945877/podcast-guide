"""
每日 AI 新闻播客 — 自动化主流程

完整流程：抓取新闻 → 生成播客脚本 → TTS 生成音频 → 播放

用法：
  # 手动运行（推荐先试一次）
  ~/.personalized-podcast/venv/bin/python daily_podcast.py

  # 配合 crontab / launchd 实现每天自动执行
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
DATA_DIR = Path.home() / ".personalized-podcast"
VENV_PYTHON = DATA_DIR / "venv" / "bin" / "python"

sys.path.insert(0, str(SCRIPTS_DIR))
from utils import get_data_dir, load_config, load_env, setup_logging


def step1_fetch_news(logger, days=1, max_articles=15):
    """第 1 步：抓取 AI/科技新闻"""
    logger.info("=" * 50)
    logger.info("第 1 步：抓取今日 AI/科技新闻")
    logger.info("=" * 50)

    from fetch_news import fetch_all_news, format_news_text
    articles = fetch_all_news(days=days, max_articles=max_articles)

    if not articles:
        logger.warning("今天没有抓到新闻，尝试扩大到最近 2 天...")
        articles = fetch_all_news(days=2, max_articles=max_articles)

    if not articles:
        logger.error("没有抓到任何新闻，退出。")
        sys.exit(1)

    news_text = format_news_text(articles)

    # 保存新闻原文
    today = datetime.now().strftime("%Y-%m-%d")
    news_path = DATA_DIR / "scripts_output" / f"{today}-news.txt"
    news_path.write_text(news_text, encoding="utf-8")
    logger.info(f"新闻已保存: {news_path} ({len(articles)} 条)")

    return news_text, articles


def step2_generate_script(news_text, logger):
    """第 2 步：基于新闻生成播客对话脚本（JSON）"""
    logger.info("=" * 50)
    logger.info("第 2 步：生成播客对话脚本")
    logger.info("=" * 50)

    # 读取 PROMPT.md 模板
    prompt_path = SKILL_DIR / "PROMPT.md"
    prompt_template = prompt_path.read_text(encoding="utf-8")

    # 构造完整 prompt
    full_prompt = f"""{prompt_template}

---

以下是今天需要讨论的新闻内容，请根据上面的格式要求生成播客脚本：

{news_text}

注意：
- 用中文讨论这些新闻
- 挑选最有趣的 5-8 条重点讨论
- 其余的可以快速带过
- 保持轻松有趣的对话风格
- 输出纯 JSON 数组，不要包含 markdown 代码块标记
"""

    # 尝试用本地 LLM 或 API 生成脚本
    script = try_generate_with_llm(full_prompt, logger)

    if script is None:
        logger.info("未检测到可用的 LLM API，使用模板脚本...")
        script = generate_template_script(news_text)

    # 保存脚本
    today = datetime.now().strftime("%Y-%m-%d")
    script_path = DATA_DIR / "scripts_output" / f"{today}.json"
    counter = 1
    while script_path.exists():
        counter += 1
        script_path = DATA_DIR / "scripts_output" / f"{today}-{counter}.json"

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    logger.info(f"脚本已保存: {script_path} ({len(script)} 段对话)")
    return script_path, script


def try_generate_with_llm(prompt, logger):
    """尝试用可用的 LLM 生成脚本"""
    import os

    # 尝试 OpenAI 兼容 API
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")

    if api_key:
        try:
            import httpx
            logger.info(f"使用 LLM API ({model}) 生成脚本...")
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(
                    f"{api_base}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8,
                    },
                )
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]
                # 清理可能的 markdown 代码块标记
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                if content.endswith("```"):
                    content = content.rsplit("```", 1)[0]
                return json.loads(content.strip())
        except Exception as e:
            logger.warning(f"LLM API 调用失败: {e}")

    return None


def generate_template_script(news_text):
    """无 LLM 时使用模板生成简单脚本"""
    lines = news_text.split("\n")
    news_items = []
    current = ""
    for line in lines:
        if line.startswith("## "):
            if current:
                news_items.append(current.strip())
            current = line.replace("## ", "").strip()
        elif line.strip() and not line.startswith("#"):
            current += " " + line.strip()
    if current:
        news_items.append(current.strip())

    script = [
        {"speaker": "A", "text": "大家好！欢迎收听今天的 AI 科技新闻播客！我是 Alex。"},
        {"speaker": "B", "text": "我是 Sam，今天我们准备了不少有意思的新闻，一起来看看吧！"},
    ]

    for i, item in enumerate(news_items[:8]):
        if i % 2 == 0:
            script.append({"speaker": "A", "text": f"来看下一条，{item}"})
            script.append({"speaker": "B", "text": "这条挺有意思的，说明 AI 领域的发展速度真的越来越快了。"})
        else:
            script.append({"speaker": "B", "text": f"还有这条，{item}"})
            script.append({"speaker": "A", "text": "确实值得关注，这个方向未来可能会有更多突破。"})

    script.append({"speaker": "B", "text": "好了，今天的新闻就到这里。最大的感受就是 AI 领域每天都在加速进化。"})
    script.append({"speaker": "A", "text": "没错！感谢收听，我们明天见！"})

    return script


def step3_generate_audio(script_path, logger):
    """第 3 步：调用 speak.py 生成音频"""
    logger.info("=" * 50)
    logger.info("第 3 步：生成播客音频")
    logger.info("=" * 50)

    result = subprocess.run(
        [str(VENV_PYTHON), str(SCRIPTS_DIR / "speak.py"), "--script", str(script_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"音频生成失败:\n{result.stderr}")
        sys.exit(1)

    # 从输出中提取 MP3 路径
    for line in result.stdout.split("\n"):
        if ".mp3" in line:
            mp3_path = line.split(":")[-1].strip() if ":" in line else line.strip()
            if Path(mp3_path).exists():
                logger.info(f"音频已生成: {mp3_path}")
                return Path(mp3_path)

    # 找最新的 MP3
    episodes_dir = DATA_DIR / "episodes"
    mp3_files = sorted(episodes_dir.glob("*.mp3"))
    if mp3_files:
        logger.info(f"音频已生成: {mp3_files[-1]}")
        return mp3_files[-1]

    logger.error("未找到生成的音频文件")
    sys.exit(1)


def step4_play(mp3_path, logger):
    """第 4 步：播放音频"""
    logger.info("=" * 50)
    logger.info(f"第 4 步：播放 {mp3_path.name}")
    logger.info("=" * 50)

    subprocess.Popen(["open", str(mp3_path)])
    logger.info("播放中...")


def main():
    logger = setup_logging()
    load_env()

    logger.info("=" * 50)
    logger.info("每日 AI 新闻播客 - 开始生成")
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    # 第 1 步：抓新闻
    news_text, articles = step1_fetch_news(logger)

    # 第 2 步：生成脚本
    script_path, script = step2_generate_script(news_text, logger)

    # 第 3 步：生成音频
    mp3_path = step3_generate_audio(script_path, logger)

    # 第 4 步：播放
    step4_play(mp3_path, logger)

    logger.info("=" * 50)
    logger.info("完成！享受你的每日 AI 新闻播客吧！")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
