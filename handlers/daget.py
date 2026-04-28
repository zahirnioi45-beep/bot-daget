import asyncio
import secrets
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import TEMPLATES, MESSAGES, BOT_USERNAME, CHANNEL_ID
from database import create_daget, get_user
from handlers.middleware import check_membership, is_on_cooldown
from handlers.menu import main_menu_keyboard, MAIN_MENU_TEXT


# ─── STEP 1 : PILIH TEMPLATE ─────────────────────────────────────────────────

def template_text() -> str:
    return (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [STEP 1/4] PILIH APLIKASI   ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        "  🔴 DAGET\n"
        "  Di gunakan untuk aplikqsi dana\n"
        "\n"
        "  🟡GOGET\n"
        "  di gunakan untuk aplikasi gopay\n"
        "\n"
        "  🟢SOGET\n"
        "  di gunakan untuk aplikasi shoppe\n"
        "```"
    )


def template_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔴 DAGET", callback_data="tpl_1"),
            InlineKeyboardButton("🟡GOGET", callback_data="tpl_2"),
            InlineKeyboardButton("🟢SOGET", callback_data="tpl_3"),
        ],
        [InlineKeyboardButton("❌ CANCEL", callback_data="back_home")],
    ])


async def cb_menu_daget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if is_on_cooldown(query.from_user.id):
        await query.answer("⏳ Tunggu sebentar.", show_alert=True)
        return

    is_member = await check_membership(context.bot, query.from_user.id, CHANNEL_ID)
    if not is_member:
        from handlers.start import join_required_text, join_keyboard
        await query.edit_message_text(
            join_required_text(),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=join_keyboard()
        )
        return

    context.user_data["daget_step"] = "template"
    await query.edit_message_text(
        template_text(),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=template_keyboard()
    )


async def cb_select_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tpl = int(query.data.split("_")[1])
    context.user_data["daget_template"] = tpl
    context.user_data["daget_slots"]    = 5
    context.user_data["daget_step"]     = "slots"

    await _show_slot_page(query, context)


# ─── STEP 2 : SLOT PAGE ──────────────────────────────────────────────────────

def slot_text(tpl: int, slots: int) -> str:
    tname = TEMPLATES[tpl]["name"]
    return (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [STEP 2/4] ATUR SLOT        ║\n"
        f"║  Template : {tname:<17}║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  Jumlah slot saat ini: [{slots}]\n"
        "  Gunakan tombol ➖ / ➕ untuk ubah\n"
        "  (min: 1 | max: 100)\n"
        "```"
    )


def slot_keyboard(slots: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖", callback_data="slot_dec"),
            InlineKeyboardButton(f"  {slots}  ", callback_data="slot_noop"),
            InlineKeyboardButton("➕", callback_data="slot_inc"),
        ],
        [InlineKeyboardButton("➡️ NEXT", callback_data="slot_next")],
        [InlineKeyboardButton("❌ CANCEL", callback_data="back_home")],
    ])


async def _show_slot_page(query, context):
    tpl   = context.user_data["daget_template"]
    slots = context.user_data["daget_slots"]
    await query.edit_message_text(
        slot_text(tpl, slots),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=slot_keyboard(slots)
    )


async def cb_slot_dec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    slots = context.user_data.get("daget_slots", 5)
    context.user_data["daget_slots"] = max(1, slots - 1)
    await _show_slot_page(query, context)


async def cb_slot_inc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    slots = context.user_data.get("daget_slots", 5)
    context.user_data["daget_slots"] = min(100, slots + 1)
    await _show_slot_page(query, context)


async def cb_slot_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


async def cb_slot_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["daget_step"] = "message"
    await _show_message_page(query, context)


# ─── STEP 3 : PILIH PESAN ────────────────────────────────────────────────────

def message_text(selected_idx: int | None) -> str:
    preview = ""
    if selected_idx is not None:
        preview = (
            f"\n  [PREVIEW]\n"
            f"  {MESSAGES[selected_idx]}\n"
        )
    lines = "".join(
        f"  {'►' if i == selected_idx else ' '} [{i+1}] {m}\n"
        for i, m in enumerate(MESSAGES)
    )
    return (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [STEP 3/4] PILIH PESAN      ║\n"
        "╚══════════════════════════════╝\n"
        f"{preview}"
        "\n"
        f"{lines}"
        "```"
    )


def message_keyboard(selected_idx: int | None):
    btns = [
        [InlineKeyboardButton(
            f"{'✅' if i == selected_idx else '🔘'} PESAN {i+1}",
            callback_data=f"msg_{i}"
        )]
        for i in range(len(MESSAGES))
    ]
    btns.append([InlineKeyboardButton("✔️ CONFIRM", callback_data="msg_confirm")])
    btns.append([InlineKeyboardButton("❌ CANCEL", callback_data="back_home")])
    return InlineKeyboardMarkup(btns)


async def _show_message_page(query, context):
    idx = context.user_data.get("daget_message_idx")
    await query.edit_message_text(
        message_text(idx),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=message_keyboard(idx)
    )


async def cb_select_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[1])
    context.user_data["daget_message_idx"] = idx
    await _show_message_page(query, context)


async def cb_msg_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("daget_message_idx") is None:
        await query.answer("⚠️ Pilih pesan dulu!", show_alert=True)
        return

    context.user_data["daget_step"] = "link"
    await query.edit_message_text(
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [STEP 4/4] INPUT LINK DAGET ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        "  Kirim link daget kamu di sini\n"
        "  (contoh: [example.com)](https://example.com)\n)"
        "\n"
        "  [!] Ketik & kirim linknya sekarang\n"
        "```",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ CANCEL", callback_data="back_home")]
        ])
    )


# ─── STEP 4 : TERIMA LINK (message handler) ──────────────────────────────────

async def handle_link_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("daget_step") != "link":
        return

    if is_on_cooldown(update.effective_user.id):
        return

    link = update.message.text.strip()
    if not link.startswith("http"):
        await update.message.delete()
        return

    await update.message.delete()

    ref_code = secrets.token_urlsafe(8)
    context.user_data["daget_link"]     = link
    context.user_data["daget_ref_code"] = ref_code
    context.user_data["daget_step"]     = "loading"

    chat_id = update.effective_chat.id
    msg_id  = context.user_data.get("msg_id")

    # ─── LOADING BAR ─────────────────────────────────────────────────────────
    stages = [
        ("█░░░░░░░░░", "Menyiapkan data..."),
        ("███░░░░░░░", "Membangun link..."),
        ("█████░░░░░", "Mengenkripsi..."),
        ("███████░░░", "Menyimpan ke DB..."),
        ("██████████", "Selesai!"),
    ]

    for bar, label in stages:
        text = (
            "```\n"
            "╔══════════════════════════════╗\n"
            "║  [SYSTEM] GENERATING LINK    ║\n"
            "╚══════════════════════════════╝\n"
            "\n"
            f"  {bar} {len(bar.replace('░',''))//1*10}%\n"
            f"  {label}\n"
            "```"
        )
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await asyncio.sleep(0.7)

    # ─── SIMPAN KE DB ────────────────────────────────────────────────────────
    user      = update.effective_user
    template  = context.user_data["daget_template"]
    slots     = context.user_data["daget_slots"]
    msg_idx   = context.user_data["daget_message_idx"]
    message   = MESSAGES[msg_idx]
    ref_link = f"https://t.me/{BOT_USERNAME}?start=claim_{ref_code}"

    await create_daget(
        creator_id=user.id,
        template=template,
        slots=slots,
        message=message,
        link=link,
        ref_code=ref_code
    )

    # ─── OUTPUT ──────────────────────────────────────────────────────────────
    output = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [✓] LINK BERHASIL DIBUAT!   ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  PESAN  : {message}\n"
        "\n"
        f"  LINK   : {ref_link}\n"
        f"  SLOT   : {slots}\n"
        f"  TEMPLATE: {TEMPLATES[template]['name']}\n"
        "```"
    )

    share_text = f"{message}%0A{ref_link}"
    share_url = f"https://t.me/share/url?url={ref_link}&text={message}"

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=output,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 SHARE LINK", url=share_url)],
            [InlineKeyboardButton("🏠 BACK TO HOME", callback_data="back_home")],
        ])
    )

    # Bersihkan state
    for key in ["daget_step", "daget_template", "daget_slots",
                "daget_message_idx", "daget_link", "daget_ref_code"]:
        context.user_data.pop(key, None)
