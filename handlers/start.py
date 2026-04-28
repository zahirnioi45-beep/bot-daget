import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import CHANNEL_LINK, CHANNEL_ID, BOT_USERNAME
from database import upsert_user, get_daget_by_ref
from handlers.middleware import check_membership, is_on_cooldown
from handlers.menu import show_main_menu


def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 JOIN CHANNEL", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ SUDAH JOIN", callback_data="check_join")],
    ])


def welcome_text(user) -> str:
    uid = user.id
    uname = f"@{user.username}" if user.username else user.first_name
    return (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║   ██╗    ██╗███████╗██╗      ║\n"
        "║   ██║    ██║██╔════╝██║      ║\n"
        "║   ██║ █╗ ██║█████╗  ██║      ║\n"
        "║   ██║███╗██║██╔══╝  ██║      ║\n"
        "║   ╚███╔███╔╝███████╗███████╗ ║\n"
        "║    ╚══╝╚══╝ ╚══════╝╚══════╝ ║\n"
        "╚══════════════════════════════╝\n"
        f"  [SYSTEM] WELCOME TO BOT\n"
        f"  USERNAME : {uname}\n"
        f"  USER ID  : {uid}\n"
        "```"
    )


def join_required_text() -> str:
    return (
        "```\n"
        "╔════════════════════════════╗\n"
        "║  [!] ACCESS DENIED         ║\n"
        "║  Wajib JOIN channel dulu   ║\n"
        "║  sebelum menggunakan bot   ║\n"
        "╚════════════════════════════╝\n"
        "```"
    )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await upsert_user(user.id, user.username, user.first_name)

    args = context.args
    if args and args[0].startswith("claim_"):
        ref_code = args[0][6:]
        context.user_data["pending_claim"] = ref_code

    is_member = await check_membership(context.bot, user.id, CHANNEL_ID)

    if is_member:
        if context.user_data.get("pending_claim"):
            from handlers.claim import show_claim_page
            msg = await update.message.reply_text(
                "```\n[SYSTEM] Memproses...\n```",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            context.user_data["msg_id"] = msg.message_id
            await show_claim_page(update, context)

        else:
            msg = await update.message.reply_text(
                welcome_text(user),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            context.user_data["msg_id"] = msg.message_id
            await show_main_menu(update, context, edit=True)

    else:
        msg = await update.message.reply_text(
            join_required_text(),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=join_keyboard()
        )
        context.user_data["msg_id"] = msg.message_id


async def cb_check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if is_on_cooldown(query.from_user.id):
        await query.answer("⏳ Terlalu cepat, tunggu sebentar.", show_alert=True)
        return

    user = query.from_user
    is_member = await check_membership(context.bot, user.id, CHANNEL_ID)

    if is_member:
        if context.user_data.get("pending_claim"):
            from handlers.claim import show_claim_page
            await show_claim_page(update, context)
        else:
            await query.edit_message_text(
                welcome_text(user),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await show_main_menu(update, context, edit=True)

    else:
        await query.edit_message_text(
            "```\n"
            "╔════════════════════════════╗\n"
            "║  [✗] BELUM JOIN CHANNEL    ║\n"
            "║  Silakan join dulu         ║\n"
            "║  lalu tekan CEK ULANG      ║\n"
            "╚════════════════════════════╝\n"
            "```",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📡 JOIN CHANNEL", url=CHANNEL_LINK)],
                [InlineKeyboardButton("🔄 CEK ULANG", callback_data="check_join")],
            ])
        )
