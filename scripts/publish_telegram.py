import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def added_queue_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-status", "HEAD^", "HEAD", "--", "telegram-queue/*.json"],
        check=True,
        capture_output=True,
        text=True,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", maxsplit=1)
        if len(parts) == 2 and parts[0] == "A":
            files.append(Path(parts[1]))
    return files


def build_message(data: dict) -> str:
    required = ["sport", "match", "market", "odds", "book"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        fail(f"Chybí povinná pole: {', '.join(missing)}")

    emoji = {
        "Tenis": "🎾",
        "Fotbal": "⚽",
        "Basketbal": "🏀",
        "Hokej": "🏒",
        "CS2": "🎮",
        "Stolní tenis": "🏓",
    }.get(str(data["sport"]), "📊")

    lines = [
        "🔥 <b>LEFI EDGE — VALUE TIP</b>",
        "",
        f"{emoji} <b>{data['match']}</b>",
    ]

    competition = data.get("competition")
    if competition:
        lines.append(f"🏆 {competition}")

    lines.extend(
        [
            "",
            f"🎯 <b>{data['market']}</b>",
            f"💰 Kurz: <b>{float(data['odds']):.2f}</b>",
            f"🏦 {data['book']}",
            f"💵 Vklad: {int(data.get('stake_czk', 1000)):,} Kč".replace(",", " "),
        ]
    )

    model_probability = data.get("model_probability")
    if model_probability is not None:
        implied = 100 / float(data["odds"])
        edge = float(model_probability) - implied
        lines.extend(
            [
                "",
                f"📊 Náš odhad: <b>{float(model_probability):.1f} %</b>",
                f"📉 Pravděpodobnost podle kurzu: {implied:.1f} %",
                f"📈 Edge: <b>{edge:+.1f} p. b.</b>",
            ]
        )

    note = data.get("note")
    if note:
        lines.extend(["", f"📝 {note}"])

    lines.extend(
        [
            "",
            "🔎 Kompletní tracker:",
            "https://lefiedgeweb.vercel.app/",
            "",
            "18+ | Hraj odpovědně",
        ]
    )
    return "\n".join(lines)


def send_message(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    if not body.get("ok"):
        fail(f"Telegram API odmítlo zprávu: {body}")
    print(f"Zveřejněno, message_id={body['result']['message_id']}")


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        fail("Nejsou nastavené TELEGRAM_BOT_TOKEN a TELEGRAM_CHAT_ID v GitHub Secrets.")

    queue_files = added_queue_files()
    if not queue_files:
        print("V tomto commitu nebyl přidán žádný nový JSON tip. Nic se neposílá.")
        return

    for path in queue_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("approved") is not True:
            fail(f"Soubor {path} nemá approved=true.")
        send_message(token, chat_id, build_message(data))


if __name__ == "__main__":
    main()
