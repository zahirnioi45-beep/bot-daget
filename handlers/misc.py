from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import CHANNEL_LINK, OWNER_USERNAME, BOT_USERNAME


async def cb_menu_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [?] HELP & TUTORIAL         ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        "  Butuh tutorial penggunaan bot?\n"
        "  Kunjungi channel kami!\n"
        "```"
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 TUTORIAL CHANNEL", url="https://t.me/tutorialajabro")],
            [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
        ])
    )


async def cb_menu_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [>] OWNER INFO              ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  Hubungi owner bot di bawah\n"
        "```"
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 PROFILE OWNER", url="https://t.me/raxiyareu")],
            [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
        ])
    )


async def cb_menu_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [>] OFFICIAL CHANNEL        ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        "  Bergabung ke channel resmi kami!\n"
        "```"
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 JOIN CHANNEL", url="https://t.me/kepoqnjieng")],
            [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
        ])
    )


async def cb_menu_share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bot_link = f"https://t.me/{BOT_USERNAME}"
    share_url = f"https://t.me/share/url?url={bot_link}&text=Cek bot keren ini!"

    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [>] SHARE BOT               ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  Link: {bot_link}\n"
        "\n"
        "  Bagikan bot ini ke temanmu!\n"
        "```"
    )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 SHARE BOT", url=share_url)],
            [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
        ])
    )
