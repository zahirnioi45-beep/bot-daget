import time
from config import COOLDOWN_SECONDS

_last_action: dict[int, float] = {}


def is_on_cooldown(user_id: int) -> bool:
    now = time.time()
    last = _last_action.get(user_id, 0)
    if now - last < COOLDOWN_SECONDS:
        return True
    _last_action[user_id] = now
    return False


async def check_membership(bot, user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False
