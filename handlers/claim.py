from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import CHANNEL_ID
from database import (
    get_daget_by_ref, get_user, try_claim,
    get_claim_order, get_all_claimers
)
from handlers.middleware import check_membership
from handlers.start import join_required_text, join_keyboard


async def show_claim_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ref_code = context.user_data.get("pending_claim")
    query    = update.callback_query
    user     = update.effective_user
    chat_id  = update.effective_chat.id
    msg_id   = context.user_data.get("msg_id")

    # Cek membership
    is_member = await check_membership(context.bot, user.id, CHANNEL_ID)
    if not is_member:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=join_required_text(),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=join_keyboard()
        )
        return

    daget = await get_daget_by_ref(ref_code)
    if not daget:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=(
                "```\n"
                "╔══════════════════════╗\n"
                "║  [✗] LINK TIDAK VALID║\n"
                "╚══════════════════════╝\n"
                "```"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
            ])
        )
        return

    # id: 0, creator_id: 1, template: 2, slots: 3, slots_left: 4,
    # message: 5, link: 6, ref_code: 7, created_at: 8
    daget_id    = daget[0]
    creator_id  = daget[1]
    slots       = daget[3]
    slots_left  = daget[4]
    msg_text    = daget[5]
    orig_link   = daget[6]

    creator = await get_user(creator_id)
    creator_uname = f"@{creator[1]}" if creator and creator[1] else str(creator_id)

    uname = f"@{user.username}" if user.username else user.first_name

    if slots_left <= 0:
        text = (
            "```\n"
            "╔══════════════════════════════╗\n"
            "║  [✗] UDAH HABIS              ║\n"
            "║  LO LAMA SIH ABIS KAN WK     ║\n"
            "╚══════════════════════════════╝\n"
            "```"
        )
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
            ])
        )
        return

    # Tampilkan tombol CLAIM
    text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [!] ADA DAGET BUAT KAMU!    ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  DARI    : {creator_uname}\n"
        f"  PESAN   : {msg_text}\n"
        f"  SLOT    : {slots_left}/{slots} tersisa\n"
        "\n"
        "  Tekan CLAIM untuk ambil daget!\n"
        "```"
    )

    context.user_data["claim_daget_id"]   = daget_id
    context.user_data["claim_creator_id"] = creator_id
    context.user_data["claim_orig_link"]  = orig_link
    context.user_data["claim_slots"]      = slots

    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 CLAIM DAGET", callback_data="do_claim")],
            [InlineKeyboardButton("🏠 HOME",        callback_data="back_home")],
        ])
    )


async def cb_do_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user       = query.from_user
    daget_id   = context.user_data.get("claim_daget_id")
    creator_id = context.user_data.get("claim_creator_id")
    orig_link  = context.user_data.get("claim_orig_link")
    slots      = context.user_data.get("claim_slots", 0)
    uname      = f"@{user.username}" if user.username else user.first_name

    if not daget_id:
        await query.answer("❌ Data tidak ditemukan.", show_alert=True)
        return

    status, slots_left = await try_claim(daget_id, user.id)

    if status == "already":
        await query.answer("⚠️ Kamu sudah pernah claim ini!", show_alert=True)
        return

    if status == "empty":
        await query.edit_message_text(
            "```\n"
            "╔══════════════════════════════╗\n"
            "║  [✗] SLOT HABIS              ║\n"
            "╚══════════════════════════════╝\n"
            "```",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 HOME", callback_data="back_home")]
            ])
        )
        return

    # Sukses claim
    order    = await get_claim_order(daget_id, user.id)
    now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    creator  = await get_user(creator_id)
    creator_uname = f"@{creator[1]}" if creator and creator[1] else str(creator_id)

    success_text = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [✓] CLAIM BERHASIL!         ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  CLAIMER  : {uname}\n"
        f"  ID       : {user.id}\n"
        f"  PEMBUAT  : {creator_uname}\n"
        f"  ID BUAT  : {creator_id}\n"
        f"  WAKTU    : {now}\n"
        f"  URUTAN   : #{order}\n"
        f"  SISA SLOT: {slots_left}/{slots}\n"
        "\n"
        f"  LINK DAGET:\n"
        f"  {orig_link}\n"
        "```"
    )

    await query.edit_message_text(
        success_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 BUKA LINK", url=orig_link)],
            [InlineKeyboardButton("🏠 HOME",      callback_data="back_home")],
        ])
    )

    # ─── NOTIF KE PEMBUAT ────────────────────────────────────────────────────
    await _notify_creator(
        context=context,
        creator_id=creator_id,
        claimer_uname=uname,
        claimer_id=user.id,
        order=order,
        slots_left=slots_left,
        slots=slots,
        daget_id=daget_id,
        now=now
    )

    # Bersihkan state
    for key in ["pending_claim", "claim_daget_id", "claim_creator_id",
                "claim_orig_link", "claim_slots"]:
        context.user_data.pop(key, None)


async def _notify_creator(context, creator_id, claimer_uname, claimer_id,
                           order, slots_left, slots, daget_id, now):
    notif = (
        "```\n"
        "╔══════════════════════════════╗\n"
        "║  [!] ADA YANG CLAIM DAGET!   ║\n"
        "╚══════════════════════════════╝\n"
        "\n"
        f"  CLAIMER  : {claimer_uname}\n"
        f"  ID       : {claimer_id}\n"
        f"  URUTAN   : #{order}\n"
        f"  WAKTU    : {now}\n"
        f"  SISA SLOT: {slots_left}/{slots}\n"
        "```"
    )
    try:
        await context.bot.send_message(
            chat_id=creator_id,
            text=notif,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except Exception:
        pass

    # Jika slot habis, kirim TOP RANK
    if slots_left == 0:
        claimers = await get_all_claimers(daget_id)
        lines = ""
        for i, (cid, cuname, cfname, cat) in enumerate(claimers, 1):
            name = f"@{cuname}" if cuname else (cfname or str(cid))
            lines += f"  #{i:<3} {name}\n"

        top_text = (
            "```\n"
            "╔══════════════════════════════╗\n"
            "║  [★] SLOT HABIS! TOP RANK    ║\n"
            "╚══════════════════════════════╝\n"
            "\n"
            f"{lines}"
            "```"
        )
        try:
            await context.bot.send_message(
                chat_id=creator_id,
                text=top_text,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        except Exception:
            pass
