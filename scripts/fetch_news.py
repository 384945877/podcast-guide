"""
每日 AI/科技新闻自动抓取脚本

从多个 RSS 源抓取最新的 AI/科技新闻，筛选当天内容，
输出为文本摘要供播客脚本使用。

用法：
  python fetch_news.py                    # 抓取今天的新闻
  python fetch_news.py --days 2           # 抓取最近 2 天
  python fetch_news.py --max 20           # 最多返回 20 条
  python fetch_news.py --output news.txt  # 保存到文件
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx

# ── RSS 新闻源配置 ──────────────────────────────────────────
RSS_FEEDS = [
    {"name": "Hacker News (Best)", "url": "https://hnrss.org/best?q=AI+OR+LLM+OR+GPT+OR+Claude+OR+machine+learning", "lang": "en"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "lang": "en"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "lang": "en"},
    {"name": "Ars Technica AI", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "lang": "en"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "lang": "en"},
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "lang": "zh"},
    {"name": "量子位", "url": "https://www.qbitai.com/feed", "lang": "zh"},
]

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "gpt", "claude", "gemini", "openai", "anthropic", "google ai",
    "chatbot", "neural", "transformer", "diffusion", "agent", "copilot",
    "robot", "自动驾驶", "大模型", "人工智能", "机器学习", "深度学习",
    "生成式", "智能体", "芯片", "gpu", "nvidia", "apple", "meta",
    "microsoft", "startup", "融资", "开源",
]


def fetch_feed(feed_info, days=1, logger=print):
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(feed_info["url"], headers={"User-Agent": "PersonalizedPodcast/1.0"})
            resp.raise_for_status()
    except Exception as e:
        logger(f"  [跳过] {feed_info['name']}: {e}")
        return articles

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError:
        logger(f"  [跳过] {feed_info['name']}: XML 解析失败")
        return articles

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item") or root.findall(".//atom:entry", ns)

    for item in items:
        title_el = item.find("title") or item.find("atom:title", ns)
        title = title_el.text.strip() if title_el is not None and title_el.text else ""

        link_el = item.find("link") or item.find("atom:link", ns)
        link = ""
        if link_el is not None:
            link = link_el.text or link_el.get("href", "")

        desc_el = item.find("description") or item.find("atom:summary", ns)
        desc = ""
        if desc_el is not None and desc_el.text:
            desc = re.sub(r"<[^>]+>", "", desc_el.text).strip()[:300]

        pub_el = item.find("pubDate") or item.find("atom:published", ns) or item.find("atom:updated", ns)
        pub_date = None
        if pub_el is not None and pub_el.text:
            try:
                pub_date = parsedate_to_datetime(pub_el.text.strip())
            except Exception:
                try:
                    pub_date = datetime.fromisoformat(pub_el.text.strip().replace("Z", "+00:00"))
                except Exception:
                    pass

        if pub_date and pub_date < cutoff:
            continue

        text_to_check = (title + " " + desc).lower()
        if not any(kw in text_to_check for kw in AI_KEYWORDS):
            continue

        articles.append({
            "source": feed_info["name"],
            "title": title,
            "link": link.strip(),
            "description": desc,
            "date": pub_date.strftime("%Y-%m-%d %H:%M") if pub_date else "unknown",
            "lang": feed_info["lang"],
        })

    logger(f"  {feed_info['name']}: 获取 {len(articles)} 条")
    return articles


def fetch_all_news(days=1, max_articles=15):
    print(f"正在抓取最近 {days} 天的 AI/科技新闻...\n")
    all_articles = []
    for feed in RSS_FEEDS:
        all_articles.extend(fetch_feed(feed, days=days))

    seen_titles = set()
    unique = []
    for a in all_articles:
        key = a["title"].lower().strip()
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(a)

    unique.sort(key=lambda x: x["date"], reverse=True)
    return unique[:max_articles]


def format_news_text(articles):
    today = datetime.now().strftime("%Y年%m月%d日")
    lines = [f"# 今日 AI/科技新闻速递 - {today}\n"]
    lines.append(f"共 {len(articles)} 条新闻:\n")

    for i, a in enumerate(articles, 1):
        lines.append(f"## {i}. [{a['source']}] {a['title']}")
        if a["description"]:
            lines.append(f"   {a['description']}")
        if a["link"]:
            lines.append(f"   链接: {a['link']}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="抓取每日 AI/科技新闻")
    parser.add_argument("--days", type=int, default=1, help="抓取最近几天 (默认 1)")
    parser.add_argument("--max", type=int, default=15, help="最多返回几条 (默认 15)")
    parser.add_argument("--output", type=str, help="输出到文件")
    args = parser.parse_args()

    articles = fetch_all_news(days=args.days, max_articles=args.max)
    text = format_news_text(articles)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"\n已保存到 {args.output} ({len(articles)} 条新闻)")
    else:
        print("\n" + text)
