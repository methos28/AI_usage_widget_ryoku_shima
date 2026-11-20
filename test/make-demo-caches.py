#!/usr/bin/env python3
"""Write fake preview data only into an explicitly chosen empty directory.

Example: python3 test/make-demo-caches.py --output-dir /tmp/ai-usage-demo
No real account, widget cache or shared collector state is changed by default.
"""
import argparse
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(20261105)


def fmt(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def day_keys(days: int) -> list[str]:
    today = datetime.now().date()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]


def models_for(period_tokens: int, period_cache: int, models: list[tuple[str, float, float]]):
    """models: (name, token share, cache share) -> rows the cards understand."""
    rows = []
    for name, token_share, cache_share in models:
        total = int(period_tokens * token_share)
        cache = int(period_cache * cache_share)
        total_cache = total + cache
        rows.append({
            "name": name,
            "total": total,
            "totalLabel": fmt(total),
            "totalWithCacheRead": total_cache,
            "totalWithCacheReadLabel": fmt(total_cache),
            "inputLabel": fmt(int(total * 0.72)),
            "outputLabel": fmt(int(total * 0.19)),
            "reasoningLabel": fmt(int(total * 0.06)),
            "cacheReadLabel": fmt(cache),
            "cacheWriteLabel": "0",
            "cacheRate": round(cache / total_cache, 4) if total_cache else 0.0,
            "cost": 0.0,
            "costLabel": "",
            "sessions": random.randint(2, 9),
            "lastSeen": int(datetime.now().timestamp() * 1000),
        })
    peak = max((row["totalWithCacheRead"] for row in rows), default=0)
    for row in rows:
        row["pct"] = int(round(row["totalWithCacheRead"] * 100 / peak)) if peak else 0
    return rows


def build(tool: str, plan: str, model: str, models: list[tuple[str, float, float]],
          base_tokens: int, base_cost: float, util5h: float, util7d: float) -> dict:
    keys = day_keys(60)
    days = []
    for index, key in enumerate(keys):
        weekend = datetime.strptime(key, "%Y-%m-%d").weekday() >= 5
        factor = random.uniform(0.55, 1.45) * (0.55 if weekend else 1.0)
        tokens = int(base_tokens * factor)
        cache = int(tokens * random.uniform(18, 42))
        cost = round(base_cost * factor, 4)
        if index < 5:  # the newest days are the ones actually "in use"
            tokens = int(tokens * 1.4)
            cache = int(cache * 1.4)
            cost = round(cost * 1.4, 4)
        days.append({"date": key, "tokens": tokens, "cacheRead": cache, "cost": cost})

    today = days[-1]
    last7 = days[-7:]
    last30 = days[-30:]
    tokens7 = sum(day["tokens"] for day in last7)
    cache7 = sum(day["cacheRead"] for day in last7)
    cost7 = round(sum(day["cost"] for day in last7), 4)

    def period(rows):
        tokens = sum(day["tokens"] for day in rows)
        cache = sum(day["cacheRead"] for day in rows)
        total = tokens + cache
        return {
            "tokens": tokens,
            "tokensLabel": fmt(tokens),
            "cacheRate": round(cache / total, 4) if total else 0.0,
            "cost": round(sum(day["cost"] for day in rows), 4),
            "sessions": random.randint(2, 8),
            "models": models_for(tokens, cache, models),
        }

    now = datetime.now()
    hours = []
    for index in range(47, -1, -1):
        moment = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=index)
        active = 0.15 < random.random()
        tokens = int(random.uniform(8_000, 190_000)) if active else 0
        hours.append({
            "start": int(moment.timestamp() * 1000),
            "tokens": tokens,
            "cacheRead": int(tokens * random.uniform(15, 35)),
        })

    recent = [{"date": day["date"], "tokens": day["tokens"]} for day in last7]

    def shell_models():
        rows = []
        for row in models_for(sum(day["tokens"] for day in last7),
                              sum(day["cacheRead"] for day in last7), models):
            rows.append({
                "name": row["name"],
                "sessions": row["sessions"],
                "total": row["total"],
                "totalLabel": row["totalLabel"],
                "inputLabel": row["inputLabel"],
                "outputLabel": row["outputLabel"],
                "reasoningLabel": row["reasoningLabel"],
                "cacheReadLabel": row["cacheReadLabel"],
                "cacheWriteLabel": row["cacheWriteLabel"],
                "todayLabel": fmt(today["tokens"]),
                "costLabel": "",
                "lastSeen": int(now.timestamp() * 1000),
                "totalWithCacheRead": row["totalWithCacheRead"],
                "totalWithCacheReadLabel": row["totalWithCacheReadLabel"],
                "pct": row["pct"],
            })
        return rows

    sessions = [
        {"id": "demo-running-1", "title": "Refactor billing flow",
         "directory": "/example/projects/billing", "started": int((now - timedelta(minutes=24)).timestamp() * 1000),
         "updated": int(now.timestamp() * 1000), "tokens": 486_000, "cost": 1.24, "running": True},
        {"id": "demo-done-1", "title": "Debug auth timeout",
         "directory": "/example/projects/api", "started": int((now - timedelta(hours=3)).timestamp() * 1000),
         "updated": int((now - timedelta(hours=2, minutes=12)).timestamp() * 1000),
         "tokens": 1_820_000, "cost": 2.10, "running": False},
        {"id": "demo-done-2", "title": "Write release notes",
         "directory": "/example/projects/docs", "started": int((now - timedelta(days=1)).timestamp() * 1000),
         "updated": int((now - timedelta(hours=20)).timestamp() * 1000),
         "tokens": 640_000, "cost": 0.80, "running": False},
    ]

    return {
        "5h-utilization": f"{util5h:.4f}",
        "5h-reset": str(int((now + timedelta(hours=2, minutes=14)).timestamp())),
        "7d-utilization": f"{util7d:.4f}",
        "7d-reset": str(int((now + timedelta(days=3, hours=5)).timestamp())),
        "updated_at": now.strftime("%H:%M:%S"),
        "_source": "demo",
        "_demo": True,
        "_plan": plan,
        "_model": model,
        "_models": shell_models(),
        "_tokens_used": 618_000,
        "_tokens_used_with_cache_read": 14_960_000,
        "_window_limit": 1_000_000,
        "_rate_per_hour": 96_000,
        "_rate_per_hour_with_cache_read": 2_400_000,
        "_today_tokens": today["tokens"],
        "_today_tokens_with_cache_read": today["tokens"] + today["cacheRead"],
        "_recent_days": recent,
        "_days": days,
        "_hours": hours,
        "_sessions": sessions,
        "_periods": {
            "today": period([today]),
            "24h": period([today]),
            "7": period(last7),
            "30": period(last30),
            "all": period(days),
        },
        "_7d_tokens": tokens7,
        "_7d_tokens_with_cache_read": tokens7 + cache7,
        "_7d_limit": 20_000_000,
        "_cost_5h": round(base_cost * 0.2, 4),
        "_cost_7d": cost7,
        "_cost_today": today["cost"],
        "status": "allowed",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.expanduser()
    output.mkdir(mode=0o700, parents=True, exist_ok=True)
    for tool in ("claude", "codex"):
        if (output / (tool + "-usage.json")).exists() or (output / (tool + "-usage.json")).is_symlink():
            parser.error("refusing to overwrite an existing usage cache")
    claude = build(
        "claude", "Max 5x", "claude-sonnet-4-5",
        [("claude-sonnet-4-5", 0.62, 0.58),
         ("claude-opus-4-1", 0.27, 0.31),
         ("claude-haiku-4-5", 0.11, 0.11)],
        base_tokens=1_450_000, base_cost=3.20, util5h=0.34, util7d=0.58)
    codex = build(
        "codex", "ChatGPT Plus", "gpt-5.1-codex",
        [("gpt-5.1-codex", 0.71, 0.68),
         ("gpt-5.1-codex-mini", 0.29, 0.32)],
        base_tokens=980_000, base_cost=1.85, util5h=0.22, util7d=0.41)

    for tool, data in (("claude", claude), ("codex", codex)):
        path = output / f"{tool}-usage.json"
        data["_demo"] = True
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as handle:
            json.dump(data, handle)
        print("wrote", path)


if __name__ == "__main__":
    main()
