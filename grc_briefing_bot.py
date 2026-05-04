#!/usr/bin/env python3
"""
GRC Daily Intelligence Briefing Bot — Vishnu Nair
100% Free Forever:
  - Groq API (Llama 3.3 70B) → free, 14,400 req/day, no card needed
  - GitHub Actions            → free cron scheduler
  - Telegram Bot API          → free forever
"""

import os
import sys
import requests
from datetime import datetime

GROQ_API_KEY       = os.environ["GROQ_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM = """You are a senior IT Risk, GRC, and Cybersecurity consultant — 15+ years, Big 4 background.
Generate a sharp daily intelligence briefing for Vishnu Nair, an aspiring GRC professional:
- BCA graduate, AWS CCP earned, AWS SAA in progress, Security+ planned (May 2026)
- Joining MBA-ITBM at SCIT Pune (ISM/ISACA specialisation) in June 2026
- Target: Big 4 Risk Advisory or BFSI security role. Tracking toward CISA + CRISC.
Tone: direct, practical, no fluff. Real industry expectations, not textbook theory."""

PROMPT = """Today is {date}. Generate the GRC Daily Briefing using EXACTLY this format.
Use Telegram HTML formatting (no Markdown).

<b>🔴 GRC INTEL — {date_short}</b>
<code>━━━━━━━━━━━━━━━━━━━━━━━</code>

<b>📡 INDUSTRY PULSE</b>
- <b>[Topic]:</b> [1-line update + why it matters for a GRC fresher]
- <b>[Topic]:</b> [1-line update + why it matters for a GRC fresher]

<b>🏢 BIG 4 INSIDER</b>
[2 sentences: what consulting teams are actually dealing with right now, tools/skills in demand]

<b>🎯 INTERVIEW Q OF THE DAY</b>
<b>Q:</b> [1 sharp question — conceptual or scenario-based]
<b>A:</b> [Crisp 2-3 sentence structured answer. Practical, not textbook.]

<b>📚 SKILL FOCUS</b>
<b>[Concept name]</b> — [2 sentences: what it is + one concrete way to study it today]

<b>⚡ CAREER EDGE</b>
[1 brutally honest insight to stand out in GRC/IT Audit hiring]

<code>━━━━━━━━━━━━━━━━━━━━━━━</code>
<i>Daily briefing for Vishnu Nair · vishnunair.in</i>

Rules:
- Keep each bullet to 1 line max
- Interview answer must be immediately useful, not generic
- Skill focus must be actionable at his current pre-MBA level
- Total message under 1500 characters"""


def generate_briefing() -> str:
    now = datetime.utcnow()
    date_str   = now.strftime("%A, %d %B %Y")
    date_short = now.strftime("%d %b %Y")

    print(f"Calling Groq for {date_str}...")

    resp = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user",   "content": PROMPT.format(
                    date=date_str,
                    date_short=date_short
                )},
            ],
            "temperature": 0.85,
            "max_tokens": 1024,
        },
        timeout=30,
    )
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    print(f"Generated {len(text)} chars")
    return text


def send_telegram(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    for parse_mode in ["HTML", ""]:
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }, timeout=15)

        if resp.ok:
            print(f"✓ Sent via {parse_mode or 'plain text'}")
            return True

        err = resp.json().get("description", "unknown")
        print(f"Send failed ({parse_mode or 'plain'}): {err}")

    return False


if __name__ == "__main__":
    try:
        briefing = generate_briefing()
        ok = send_telegram(briefing)
        sys.exit(0 if ok else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": f"⚠️ GRC Bot error: {str(e)[:200]}"},
            timeout=10,
        )
        sys.exit(1)
