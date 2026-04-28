from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import count_users, count_dagets


async def cb_menu_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    total_users  = await count_users()
    total_dagets = await count_dagets()

    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [>] BOT STATISTICS          ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  TOTAL USER  : {total_users}\n"
        f"  TOTAL DAGET : {total_dagets}\n"
        "```"
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
        ])
    )
