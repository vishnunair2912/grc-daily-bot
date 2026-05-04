#!/usr/bin/env python3
"""
GRC Daily Intelligence Briefing Bot — Vishnu Nair
100% Free Forever:
  - Google Gemini Flash API  → free (1500 req/day, no expiry, no card needed)
  - GitHub Actions           → free cron scheduler
  - Telegram Bot API         → free forever
"""

import os
import sys
import requests
from datetime import datetime

GEMINI_API_KEY     = os.environ["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

GEMINI_URL = (
   "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash-latest:generateContent?key=" + GEMINI_API_KEY
)

SYSTEM_CONTEXT = """You are a senior IT Risk, GRC, and Cybersecurity consultant — 
15+ years experience, Big 4 background (Deloitte / EY / PwC / KPMG).
You mentor an aspiring GRC professional named Vishnu Nair:
- BCA graduate (SICSR Pune, CGPA 7.0), DevOps internship at HJCloud Systems
- AWS Cloud Practitioner earned, AWS SAA in progress (target March 2026)
- CompTIA Security+ planned (May 2026)
- Joining MBA-ITBM at SCIT Pune, ISM specialisation (ISACA curriculum), June 2026
- Career target: Big 4 Risk Advisory or BFSI security role within 3-5 years
- Long-term certifications: CISA + CRISC
Tone: direct, practical, slightly critical. Real industry expectations. No fluff. No generic motivation."""

PROMPT_TEMPLATE = """Today is {date}.

Generate a GRC Daily Intelligence Briefing using EXACTLY this Telegram HTML format.
Do not add any text before or after the briefing block.

<b>🔴 GRC INTEL — {date_short}</b>
<code>━━━━━━━━━━━━━━━━━━━━━━━</code>

<b>📡 INDUSTRY PULSE</b>
• <b>[Topic tag]:</b> [One sentence — a real current development in GRC/cybersecurity/IT audit + why it matters for someone entering the field]
• <b>[Topic tag]:</b> [One sentence — a second development, regulatory change, or breach lesson + why it matters]

<b>🏢 BIG 4 INSIDER</b>
[2 sentences: what consulting teams are actually dealing with right now. Name specific tools, frameworks, or engagement types. Make it feel like insider intel, not a job description.]

<b>🎯 INTERVIEW Q OF THE DAY</b>
<b>Q:</b> [One sharp interview question — alternate between conceptual and scenario-based on different days]
<b>A:</b> [2–3 sentence structured answer. Practical and crisp. Include a framework reference where natural.]

<b>📚 SKILL FOCUS</b>
<b>[Concept name]</b> — [2 sentences: what it is in plain terms + one specific, actionable way to study it today given Vishnu's current level]

<b>⚡ CAREER EDGE</b>
[One brutally honest insight. Something most candidates don't do. Specific to GRC/IT Audit hiring at Big 4 or BFSI.]

<code>━━━━━━━━━━━━━━━━━━━━━━━</code>
<i>Daily briefing · vishnunair.in</i>

Strict rules:
- Each bullet point must fit on one line
- Interview answer must be immediately actionable, not generic
- Skill focus must connect to Vishnu's current stage (pre-MBA, AWS background, building toward CISA)
- Vary the content daily — do not repeat the same topics, questions, or tips
- Keep total output under 1500 characters"""


def generate_briefing() -> str:
    now = datetime.utcnow()
    date_str   = now.strftime("%A, %d %B %Y")
    date_short = now.strftime("%d %b %Y")

    print(f"Calling Gemini for {date_str}…")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_CONTEXT + "\n\n" + PROMPT_TEMPLATE.format(
                        date=date_str,
                        date_short=date_short
                    )}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 1024,
        }
    }

import time
    for attempt in range(3):
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        if resp.status_code == 429:
            print(f"Rate limited, waiting 30s (attempt {attempt+1})...")
            time.sleep(30)
            continue
        resp.raise_for_status()
        break

    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    print(f"Briefing generated: {len(text)} chars")
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
            print(f"✓ Telegram message sent ({parse_mode or 'plain text'})")
            return True

        err = resp.json().get("description", "unknown")
        print(f"Send attempt failed ({parse_mode or 'plain'}): {err}")

    return False


if __name__ == "__main__":
    try:
        briefing = generate_briefing()
        ok = send_telegram(briefing)
        sys.exit(0 if ok else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        # Send a fallback error notification to Telegram
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"⚠️ GRC Bot error today: {str(e)[:200]}",
            },
            timeout=10,
        )
        sys.exit(1)
