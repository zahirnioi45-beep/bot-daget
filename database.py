import aiosqlite
import asyncio
from datetime import datetime

DB_PATH = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                joined_at   TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS dagets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id  INTEGER NOT NULL,
                template    INTEGER NOT NULL,
                slots       INTEGER NOT NULL,
                slots_left  INTEGER NOT NULL,
                message     TEXT NOT NULL,
                link        TEXT NOT NULL,
                ref_code    TEXT UNIQUE NOT NULL,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                daget_id    INTEGER NOT NULL,
                claimer_id  INTEGER NOT NULL,
                claimed_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(daget_id, claimer_id)
            )
        """)
        await db.commit()


# ─── USER ────────────────────────────────────────────────────────────────────

async def upsert_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username   = excluded.username,
                first_name = excluded.first_name
        """, (user_id, username or "", first_name or ""))
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, first_name, joined_at FROM users WHERE user_id = ?",
            (user_id,)
        ) as cur:
            return await cur.fetchone()


async def count_users() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ─── DAGET ───────────────────────────────────────────────────────────────────

async def create_daget(creator_id: int, template: int, slots: int,
                       message: str, link: str, ref_code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO dagets (creator_id, template, slots, slots_left, message, link, ref_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (creator_id, template, slots, slots, message, link, ref_code))
        await db.commit()


async def get_daget_by_ref(ref_code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM dagets WHERE ref_code = ?", (ref_code,)
        ) as cur:
            return await cur.fetchone()


async def get_daget_by_id(daget_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM dagets WHERE id = ?", (daget_id,)
        ) as cur:
            return await cur.fetchone()


async def count_dagets() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM dagets") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def get_user_daget_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM dagets WHERE creator_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def get_user_claim_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM claims WHERE claimer_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ─── CLAIM ───────────────────────────────────────────────────────────────────

async def try_claim(daget_id: int, claimer_id: int):
    """
    Returns: 'ok', 'already', 'empty'
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Cek sudah claim
        async with db.execute(
            "SELECT id FROM claims WHERE daget_id = ? AND claimer_id = ?",
            (daget_id, claimer_id)
        ) as cur:
            if await cur.fetchone():
                return "already", None

        # Cek slot
        async with db.execute(
            "SELECT slots_left FROM dagets WHERE id = ?", (daget_id,)
        ) as cur:
            row = await cur.fetchone()
            if not row or row[0] <= 0:
                return "empty", None

        # Kurangi slot
        await db.execute(
            "UPDATE dagets SET slots_left = slots_left - 1 WHERE id = ?",
            (daget_id,)
        )
        await db.execute(
            "INSERT INTO claims (daget_id, claimer_id) VALUES (?, ?)",
            (daget_id, claimer_id)
        )
        await db.commit()

        # Ambil data terbaru
        async with db.execute(
            "SELECT slots_left FROM dagets WHERE id = ?", (daget_id,)
        ) as cur:
            row = await cur.fetchone()
            return "ok", row[0] if row else 0


async def get_claim_order(daget_id: int, claimer_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT ROW_NUMBER() OVER (ORDER BY claimed_at) as rn, claimer_id
            FROM claims WHERE daget_id = ?
        """, (daget_id,)) as cur:
            rows = await cur.fetchall()
            for row in rows:
                if row[1] == claimer_id:
                    return row[0]
    return 0


async def get_all_claimers(daget_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT c.claimer_id, u.username, u.first_name, c.claimed_at
            FROM claims c
            LEFT JOIN users u ON c.claimer_id = u.user_id
            WHERE c.daget_id = ?
            ORDER BY c.claimed_at ASC
        """, (daget_id,)) as cur:
            return await cur.fetchall()


# ─── LEADERBOARD ─────────────────────────────────────────────────────────────

async def get_leaderboard(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT d.creator_id, u.username, u.first_name,
                   COUNT(d.id) as total_daget,
                   SUM(d.slots - d.slots_left) as total_claims
            FROM dagets d
            LEFT JOIN users u ON d.creator_id = u.user_id
            GROUP BY d.creator_id
            ORDER BY total_daget DESC, total_claims DESC
            LIMIT ?
        """, (limit,)) as cur:
            return await cur.fetchall()
