from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import get_user, get_user_daget_count, get_user_claim_count, get_leaderboard


async def cb_menu_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user  = query.from_user
    uname = f"@{user.username}" if user.username else user.first_name

    daget_count = await get_user_daget_count(user.id)
    claim_count = await get_user_claim_count(user.id)

    # Cari rank di leaderboard
    lb    = await get_leaderboard(999)
    rank  = "-"
    for i, row in enumerate(lb, 1):
        if row[0] == user.id:
            rank = str(i)
            break

    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [>] YOUR PROFILE            ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  USERNAME  : {uname}\n"
        f"  USER ID   : {user.id}\n"
        f"  DAGET     : {daget_count} dibuat\n"
        f"  CLAIM     : {claim_count} kali\n"
        f"  LB RANK   : #{rank}\n"
        "```"
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
        ])
    )
