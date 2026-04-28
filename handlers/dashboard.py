from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import count_users, count_dagets, get_leaderboard


async def cb_menu_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    total_users  = await count_users()
    total_dagets = await count_dagets()
    lb           = await get_leaderboard(3)
    now          = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    top_lines = ""
    for i, row in enumerate(lb, 1):
        uid, uname, fname, td, tc = row
        name = f"@{uname}" if uname else (fname or str(uid))
        top_lines += f"  #{i} {name} | D:{td} C:{tc or 0}\n"

    if not top_lines:
        top_lines = "  Belum ada data.\n"

    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [>] SYSTEM DASHBOARD        ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  ► TIMESTAMP  : {now}\n"
        f"  ► STATUS     : ONLINE ✓\n"
        f"  ► USERS      : {total_users}\n"
        f"  ► DAGETS     : {total_dagets}\n"
        "\n"
        "  ── TOP 3 KREATOR ──\n"
        f"{top_lines}"
        "\n"
        "  ─────────────────────────────\n"
        "  [SYSTEM] All systems nominal\n"
        "```"
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
        ])
    )
