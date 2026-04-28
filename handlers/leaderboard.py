from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import get_leaderboard


async def cb_menu_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rows = await get_leaderboard(10)

    if not rows:
        body = "  Belum ada data.\n"
    else:
        medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 10
        body = ""
        for i, row in enumerate(rows):
            uid, uname, fname, total_daget, total_claims = row
            name = f"@{uname}" if uname else (fname or str(uid))
            body += (
                f"  {medals[i]} #{i+1} {name}\n"
                f"       Daget: {total_daget} | Claims: {total_claims or 0}\n"
            )

    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [★] GLOBAL LEADERBOARD      ║\n"
        "║  Top kreator daget           ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"{body}"
        "```"
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
        ])
    )
