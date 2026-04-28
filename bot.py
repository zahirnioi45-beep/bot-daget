import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database import init_db

from handlers.start import cmd_start, cb_check_join
from handlers.menu import cb_back_home, show_main_menu
from handlers.daget import (
    cb_menu_daget, cb_select_template,
    cb_slot_dec, cb_slot_inc, cb_slot_noop, cb_slot_next,
    cb_select_message, cb_msg_confirm,
    handle_link_input,
)
from handlers.claim import cb_do_claim
from handlers.leaderboard import cb_menu_leaderboard
from handlers.profile import cb_menu_profile
from handlers.stats import cb_menu_stats
from handlers.dashboard import cb_menu_dashboard
from handlers.misc import (
    cb_menu_help, cb_menu_owner,
    cb_menu_channel, cb_menu_share,
)

# ================= WEB SERVER (BIAR LOLOS DEPLOY) =================
def run_web_server():
    port = int(os.environ.get("PORT", 8080))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot is running")

    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


# ================= LOGGING =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ================= INIT DB =================
async def post_init(app):
    await init_db()
    logger.info("Database initialized.")


# ================= MAIN BOT =================
def main():
    logger.info("Starting bot...")

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # ─── COMMAND ─────────────────────────────
    app.add_handler(CommandHandler("start", cmd_start))

    # ─── CALLBACK BASIC ───────────────────────
    app.add_handler(CallbackQueryHandler(cb_check_join, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(cb_back_home, pattern="^back_home$"))

    # MENU
    app.add_handler(CallbackQueryHandler(cb_menu_daget, pattern="^menu_daget$"))
    app.add_handler(CallbackQueryHandler(cb_menu_leaderboard, pattern="^menu_leaderboard$"))
    app.add_handler(CallbackQueryHandler(cb_menu_profile, pattern="^menu_profile$"))
    app.add_handler(CallbackQueryHandler(cb_menu_stats, pattern="^menu_stats$"))
    app.add_handler(CallbackQueryHandler(cb_menu_dashboard, pattern="^menu_dashboard$"))
    app.add_handler(CallbackQueryHandler(cb_menu_help, pattern="^menu_help$"))
    app.add_handler(CallbackQueryHandler(cb_menu_owner, pattern="^menu_owner$"))
    app.add_handler(CallbackQueryHandler(cb_menu_channel, pattern="^menu_channel$"))
    app.add_handler(CallbackQueryHandler(cb_menu_share, pattern="^menu_share$"))

    # DAGET FLOW
    app.add_handler(CallbackQueryHandler(cb_select_template, pattern=r"^tpl_[123]$"))
    app.add_handler(CallbackQueryHandler(cb_slot_dec, pattern="^slot_dec$"))
    app.add_handler(CallbackQueryHandler(cb_slot_inc, pattern="^slot_inc$"))
    app.add_handler(CallbackQueryHandler(cb_slot_noop, pattern="^slot_noop$"))
    app.add_handler(CallbackQueryHandler(cb_slot_next, pattern="^slot_next$"))
    app.add_handler(CallbackQueryHandler(cb_select_message, pattern=r"^msg_[01234]$"))
    app.add_handler(CallbackQueryHandler(cb_msg_confirm, pattern="^msg_confirm$"))

    # CLAIM
    app.add_handler(CallbackQueryHandler(cb_do_claim, pattern="^do_claim$"))

    # MESSAGE INPUT
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_link_input
        )
    )

    logger.info("Bot started successfully.")
    app.run_polling(drop_pending_updates=True)


# ================= ENTRY =================
if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    main()
