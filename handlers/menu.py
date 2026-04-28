from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


MAIN_MENU_TEXT = (
    "```\n"
    "╔══════════════════════════╗\n"
    "║  [>] MAIN MENU           ║\n"
    "║  Pilih menu di bawah ini ║\n"
    "╚══════════════════════════╝\n"
    "```"
)


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 BUAT DAGET",   callback_data="menu_daget"),
            InlineKeyboardButton("🏆 LEADERBOARD",  callback_data="menu_leaderboard"),
        ],
        [
            InlineKeyboardButton("👤 PROFILE",      callback_data="menu_profile"),
            InlineKeyboardButton("📊 STATS",        callback_data="menu_stats"),
        ],
        [
            InlineKeyboardButton("🖥️ DASHBOARD",   callback_data="menu_dashboard"),
            InlineKeyboardButton("❓ HELP",         callback_data="menu_help"),
        ],
        [
            InlineKeyboardButton("👑 OWNER",        callback_data="menu_owner"),
            InlineKeyboardButton("📢 CHANNEL",      callback_data="menu_channel"),
        ],
        [
            InlineKeyboardButton("🔗 SHARE BOT",    callback_data="menu_share"),
        ],
    ])


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    if edit:
        query = update.callback_query
        if query:
            await query.edit_message_text(
                MAIN_MENU_TEXT,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=main_menu_keyboard()
            )
        else:
            # Dari start handler (message bukan callback)
            chat_id = update.effective_chat.id
            msg_id  = context.user_data.get("msg_id")
            if msg_id:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=MAIN_MENU_TEXT,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=main_menu_keyboard()
                )
    else:
        msg = await update.message.reply_text(
            MAIN_MENU_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard()
        )
        context.user_data["msg_id"] = msg.message_id


async def cb_back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Bersihkan state daget
    for key in ["daget_step", "daget_template", "daget_slots",
                "daget_message_idx", "daget_link", "pending_claim"]:
        context.user_data.pop(key, None)

    await query.edit_message_text(
        MAIN_MENU_TEXT,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard()
    )
