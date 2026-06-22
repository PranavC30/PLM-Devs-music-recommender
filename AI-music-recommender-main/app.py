import streamlit as st
import time
import os
import glob
import json
import hashlib
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from env import MusicEnv
from agent import QLearningAgent
from recommend import Recommender
from nlp_engine import NLPEngine
from dashboard import render_dashboard
from auth import (register_user, login_user, save_history_entry,
                  load_history, delete_user, save_journal_entry, load_journal)
from pomodoro import render_pomodoro
from gamification import update_stats, load_stats, get_level, BADGES, save_stats
from social import (share_playlist, load_shared_playlists, like_shared_playlist,
                    load_favourites, toggle_favourite, export_playlist_text,
                    get_leaderboard_top, get_user_rank, follow_user, unfollow_user,
                    load_friends, add_comment, get_comments)
from chatbot import MusicChatbot
from weekly_report import generate_weekly_report, export_report_text
from ratings import save_rating, get_rating, get_top_rated_songs, get_rating_stats
from playlist_generator import generate_playlist, get_preset_playlists
from content_filter import get_similar_songs
from ui_components import (
    inject_global_css, render_animated_header, render_song_card,
    render_song_card_with_art, render_mood_selector, render_skeleton_cards,
    show_toast, render_now_playing_bar, render_now_playing_bar_v2,
    render_sidebar, render_onboarding, render_splash_screen,
    render_lyrics_search, get_album_art_html,
    MOOD_ACCENT, MOOD_GRADIENTS, MOOD_EMOJI,
)

st.set_page_config(page_title="PLM Devs AI Recommender", page_icon="🎵", layout="wide")

# ── Constants ──────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Helper: apply mood theme ───────────────────────────────────────────
def apply_theme(mood: str):
    inject_global_css(
        accent=MOOD_ACCENT.get(mood, "#1DB954"),
        bg=MOOD_GRADIENTS.get(mood, MOOD_GRADIENTS["Relaxed"])
    )

# ── Helper: YouTube / Spotify embed ───────────────────────────────────
def get_yt_embed_html(url: str, song_name: str, language: str = "Hindi", spotify_url: str = "") -> str:
    import re
    query    = f"{song_name} official audio {language}".replace(" ", "+")
    yt_direct = (str(url).strip() if url and str(url).strip().lower() != "nan"
                 else f"https://www.youtube.com/results?search_query={query}")
    sp = str(spotify_url).strip() if spotify_url else ""
    if sp and sp.lower() != "nan" and sp.startswith("http"):
        if "/embed/" not in sp:
            sp = sp.replace("open.spotify.com/track/", "open.spotify.com/embed/track/")
        return (f"<div style='border-radius:14px;overflow:hidden;margin:10px 0 16px 0;"
                f"box-shadow:0 4px 20px rgba(0,0,0,0.4);'>"
                f"<iframe src='{sp}?utm_source=generator&theme=0' width='100%' height='152' "
                f"frameborder='0' allowfullscreen allow='autoplay; clipboard-write; "
                f"encrypted-media; fullscreen; picture-in-picture' loading='lazy' "
                f"style='border-radius:14px;display:block;'></iframe></div>")
    vid_id = None
    if url and str(url).strip() and str(url).strip().lower() != "nan":
        m = re.search(r"(?:v=|youtu\.be/|/embed/)([A-Za-z0-9_-]{11})", str(url))
        if m:
            vid_id = m.group(1)
    if vid_id and language == "English":
        return (f"<div style='border-radius:14px;overflow:hidden;margin:10px 0 16px 0;"
                f"box-shadow:0 4px 20px rgba(0,0,0,0.5);'>"
                f"<iframe width='100%' height='240' "
                f"src='https://www.youtube-nocookie.com/embed/{vid_id}?rel=0&modestbranding=1' "
                f"frameborder='0' allow='accelerometer; autoplay; clipboard-write; "
                f"encrypted-media; gyroscope; picture-in-picture' allowfullscreen "
                f"style='display:block;'></iframe></div>")
    return (f"<div style='text-align:center;margin:8px 0 18px 0;'>"
            f"<a href='{yt_direct}' target='_blank' style='display:inline-block;"
            f"padding:12px 32px;background:#FF0000;color:white;text-decoration:none;"
            f"border-radius:25px;font-weight:bold;font-size:1rem;"
            f"box-shadow:0 4px 15px rgba(255,0,0,0.4);'>▶ Play on YouTube</a></div>")

# ══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════
_defaults = {
    "logged_in": False, "is_admin": False, "username": None,
    "env": None, "nlp": None, "recommender": None, "agent": None, "chatbot": None,
    "last_genre": "None", "current_songs": [], "playlist_queue": [],
    "current_state": None, "current_action": None, "feedback_given": False,
    "current_mood": "Relaxed", "current_language": "Hindi",
    "new_badges": [], "chat_history": [],
    "checkin_done_today": None,
    "gen_playlist": [], "gen_playlist_total": 0.0,
    "onboard_done": False,
    "now_playing_song": None, "now_playing_mood": "Relaxed", "now_playing_genre": "",
    "now_playing_song_dict": None,
    "splash_shown": False,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

if st.session_state.env is None:         st.session_state.env         = MusicEnv()
if st.session_state.nlp is None:         st.session_state.nlp         = NLPEngine()
if st.session_state.recommender is None: st.session_state.recommender = Recommender()
if st.session_state.chatbot is None:     st.session_state.chatbot     = MusicChatbot()

apply_theme(st.session_state.get("current_mood", "Relaxed") or "Relaxed")

# ── Splash screen — show once per session ─────────────────────────────
if not st.session_state.get("splash_shown", False):
    render_splash_screen()
    st.session_state.splash_shown = True

# ══════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <style>
    .login-hero { text-align:center; padding:40px 20px 10px 20px; }
    .login-features { display:flex; justify-content:center; gap:16px; flex-wrap:wrap; margin:18px 0 30px 0; }
    .login-feat-chip { background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.15);
        border-radius:20px; padding:6px 16px; font-size:0.9rem; }
    </style>
    <div class='login-hero'>
        <h1 style='font-weight:800;font-size:2.4rem;background:linear-gradient(90deg,#1DB954,#fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            🎵 PLM Devs Music AI
        </h1>
        <p style='opacity:0.7;font-size:1rem;margin-top:6px;'>
            Your personal AI that learns your music taste and gets smarter every day.
        </p>
    </div>
    <div class='login-features'>
        <span class='login-feat-chip'>🧠 Q-Learning AI</span>
        <span class='login-feat-chip'>🎭 Mood Detection</span>
        <span class='login-feat-chip'>🌍 5 Languages</span>
        <span class='login-feat-chip'>🏆 Gamification</span>
        <span class='login-feat-chip'>🌐 Community</span>
        <span class='login-feat-chip'>📊 Weekly Reports</span>
    </div>
    """, unsafe_allow_html=True)

    _lc1, _lc2, _lc3 = st.columns([1, 2, 1])
    with _lc2:
        _ltab, _stab = st.tabs(["🔑 Login", "📝 Sign Up"])
        with _ltab:
            st.markdown("<br>", unsafe_allow_html=True)
            l_user = st.text_input("Username", key="l_user", placeholder="Enter your username")
            l_pass = st.text_input("Password", type="password", key="l_pass", placeholder="Enter your password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login →", use_container_width=True, type="primary"):
                if l_user.strip() == "admin_plm" and l_pass == "admin123":
                    st.session_state.is_admin = True
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    _ok, _msg = login_user(l_user.strip(), l_pass)
                    if _ok:
                        st.session_state.username = l_user.strip()
                        st.session_state.agent = QLearningAgent(
                            actions=st.session_state.env.get_actions(),
                            username=st.session_state.username)
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error(_msg)
        with _stab:
            st.markdown("<br>", unsafe_allow_html=True)
            s_user  = st.text_input("Choose Username", key="s_user", placeholder="e.g. pranav123")
            s_pass  = st.text_input("Choose Password", type="password", key="s_pass", placeholder="Min 4 characters")
            s_pass2 = st.text_input("Confirm Password", type="password", key="s_pass2", placeholder="Repeat password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create My AI Brain 🧠", use_container_width=True, type="primary"):
                if not s_user.strip():     st.error("Username cannot be empty.")
                elif s_pass != s_pass2:    st.error("Passwords do not match.")
                elif len(s_pass) < 4:      st.error("Password must be at least 4 characters.")
                else:
                    _ok, _msg = register_user(s_user.strip(), s_pass)
                    if _ok:
                        st.success(f"✅ {_msg} Now login!")
                    else:
                        st.error(_msg)

    st.markdown("<div style='text-align:center;margin-top:30px;opacity:0.4;font-size:0.78rem;'>"
                "Built with ❤️ by PLM Devs &nbsp;·&nbsp; Pranav Chakravorty</div>", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if st.session_state.is_admin:
    st.markdown("<h1 style='text-align:center;'>🛡️ PLM Devs God Mode</h1>", unsafe_allow_html=True)
    if st.button("🚪 Exit God Mode", type="primary"):
        st.session_state.logged_in = False
        st.session_state.is_admin  = False
        st.rerun()
    st.divider()

    st.header("1. Global AI Matrices")
    _files = glob.glob(os.path.join(_DIR, "q_table_*.json"))
    st.write(f"Total Active User Brains: **{len(_files)}**")
    for _f in _files:
        _un = os.path.basename(_f).replace("q_table_", "").replace(".json", "")
        with st.expander(f"View Q-Table: {_un}"):
            _ag = QLearningAgent(actions=st.session_state.env.get_actions(), username=_un)
            st.json(_ag.q_table)
            if st.button(f"🗑️ Delete {_un}", key=f"del_{_un}"):
                delete_user(_un)
                st.success("Deleted!")
                st.rerun()

    st.divider()
    st.header("2. Catalog Expansion")
    with st.form("add_song_form"):
        new_song    = st.text_input("Song Name")
        new_mood    = st.selectbox("Mood", st.session_state.env.moods)
        new_genre   = st.selectbox("Genre", st.session_state.env.get_actions())
        new_energy  = st.selectbox("Energy", ["Low", "Medium", "High"])
        new_lang    = st.selectbox("Language", ["Hindi", "English", "Punjabi", "Tamil", "Telugu"])
        new_url     = st.text_input("YouTube URL (Optional)")
        new_spotify = st.text_input("Spotify Embed URL (Optional)")
        if st.form_submit_button("Add to Universe") and new_song.strip():
            _csv = os.path.join(_DIR, "data", "songs.csv")
            with open(_csv, "a", encoding="utf-8") as _fcsv:
                _fcsv.write(f"\n{new_song},{new_mood},{new_genre},{new_energy},{new_lang},{new_url},{new_spotify}")
            st.success("Injected!")
            st.session_state.recommender = Recommender()
            st.session_state.chatbot     = MusicChatbot()

    st.divider()
    st.header("3. All Users History")
    for _hf in glob.glob(os.path.join(_DIR, "history_*.json")):
        _un2 = os.path.basename(_hf).replace("history_", "").replace(".json", "")
        with st.expander(f"History: {_un2}"):
            with open(_hf) as _fp: _hdata = json.load(_fp)
            st.write(f"Sessions: {len(_hdata)}")
            for _e in reversed(_hdata[-10:]):
                st.markdown(f"**{_e['timestamp']}** — `{_e['mood']}` | `{_e['genre']}` | `{_e['feedback']}`")
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# ONBOARDING — first-time users only
# ══════════════════════════════════════════════════════════════════════
if not st.session_state.get("onboard_done", False):
    render_onboarding()
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    _sb_stats  = load_stats(st.session_state.username) if st.session_state.username else {}
    _sb_xp     = _sb_stats.get("xp", 0)
    _sb_level  = get_level(_sb_xp)
    _sb_streak = _sb_stats.get("streak", 0)
    _sb_favs   = load_favourites(st.session_state.username) if st.session_state.username else []

    render_sidebar(
        username = st.session_state.username or "Guest",
        xp       = _sb_xp,
        level    = _sb_level,
        streak   = _sb_streak,
        queue    = st.session_state.playlist_queue,
        favs     = _sb_favs,
        mood     = st.session_state.get("current_mood", "Relaxed") or "Relaxed",
    )

    if st.button("🗑️ Clear Queue", use_container_width=True, key="clear_queue",
                 disabled=not st.session_state.playlist_queue):
        st.session_state.playlist_queue = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        for _k2 in list(st.session_state.keys()):
            del st.session_state[_k2]
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# BADGE POPUP
# ══════════════════════════════════════════════════════════════════════
if st.session_state.new_badges:
    for _badge in st.session_state.new_badges:
        show_toast(f"New Badge Unlocked: {_badge}", icon="🏅",
                   mood=st.session_state.get("current_mood", "Relaxed"))
    st.session_state.new_badges = []

# ══════════════════════════════════════════════════════════════════════
# DAILY MOOD CHECK-IN
# ══════════════════════════════════════════════════════════════════════
_today = datetime.date.today().isoformat()
if st.session_state.get("checkin_done_today") != _today:
    _hour = datetime.datetime.now().hour
    _greet = ("Morning" if 5 <= _hour < 12 else
              "Afternoon" if 12 <= _hour < 17 else
              "Evening"   if 17 <= _hour < 21 else "Night")
    st.markdown(f"""
    <div style='background:linear-gradient(90deg,rgba(29,185,84,0.15),rgba(100,149,237,0.1));
    border:1px solid rgba(255,255,255,0.15);border-radius:16px;
    padding:20px 24px;margin-bottom:20px;text-align:center;'>
        <h3 style='margin:0 0 6px 0;'>🌅 Good {_greet}, {st.session_state.username}!</h3>
        <p style='opacity:0.75;margin:0;font-size:0.95rem;'>Aaj kaisa feel ho raha hai? Apna mood check-in karo 👇</p>
    </div>""", unsafe_allow_html=True)
    _ci_cols = st.columns(4)
    for _col, (_label, _mval) in zip(_ci_cols, [
        ("😄 Happy","Happy"),("😢 Sad","Sad"),("🎯 Focus","Focus"),("😌 Relaxed","Relaxed")
    ]):
        with _col:
            if st.button(_label, use_container_width=True, key=f"ci_{_mval}"):
                st.session_state.checkin_done_today = _today
                st.session_state.current_mood = _mval
                apply_theme(_mval)
                save_journal_entry(st.session_state.username, _mval, f"Daily check-in: {_mval}")
                show_toast(f"Check-in done! Mood: {_mval}", icon="✅", mood=_mval)
                st.rerun()
    if st.button("⏭️ Skip check-in", key="skip_checkin"):
        st.session_state.checkin_done_today = _today
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# ANIMATED MAIN HEADER
# ══════════════════════════════════════════════════════════════════════
render_animated_header(st.session_state.get("current_mood", "Relaxed") or "Relaxed")

# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
(tab_rec, tab_match, tab_social, tab_analytics,
 tab_history, tab_journal, tab_profile, tab_chat,
 tab_report, tab_search, tab_pgen) = st.tabs([
    "🎧 Recommender", "🤝 Taste Match",  "🌐 Community",
    "📈 Analytics",   "📜 History",      "📓 Mood Journal",
    "👤 Profile",     "🤖 AI Chatbot",   "📊 Weekly Report",
    "🔍 Search Songs","🎵 Auto Playlist",
])

# ══════════════════════════════════════════════════════════════════════
# TAB: RECOMMENDER
# ══════════════════════════════════════════════════════════════════════
with tab_rec:
    st.write("---")
    _r1, _r2 = st.columns([2, 1])

    with _r1:
        # Emoji mood card selector
        detected_mood = render_mood_selector(st.session_state.current_mood)
        if detected_mood != st.session_state.current_mood:
            st.session_state.current_mood = detected_mood
            apply_theme(detected_mood)
            st.rerun()

        # Additional text / voice input
        input_mode = st.radio("Or refine with:",
                              ["📝 Text/Sentence", "🎤 Voice Audio"],
                              horizontal=True)

        if input_mode == "📝 Text/Sentence":
            user_text = st.text_area(
                "Tell the AI how your day is going...",
                placeholder="E.g., I had an amazing day but now I just want to chill.")
            if user_text:
                detected_mood = st.session_state.nlp.detect_mood_from_text(user_text)
                if detected_mood != st.session_state.current_mood:
                    st.session_state.current_mood = detected_mood
                    apply_theme(detected_mood)
                st.info(f"🧠 AI Detected Mood: **{detected_mood}**")

        elif input_mode == "🎤 Voice Audio":
            audio_val = st.audio_input("Record a voice note")
            if audio_val is not None:
                with st.spinner("Transcribing..."):
                    try:
                        _txt = st.session_state.nlp.transcribe_audio(audio_val)
                    except Exception:
                        _txt = ""
                if _txt:
                    detected_mood = st.session_state.nlp.detect_mood_from_text(_txt)
                    if detected_mood != st.session_state.current_mood:
                        st.session_state.current_mood = detected_mood
                        apply_theme(detected_mood)
                    st.info(f"🧠 AI Detected Mood: **{detected_mood}**")
                else:
                    st.warning("Voice transcription unavailable on this server. Use Text mode instead.")

    with _r2:
        _hour = datetime.datetime.now().hour
        auto_time = ("Morning"   if 5  <= _hour < 12 else
                     "Afternoon" if 12 <= _hour < 17 else
                     "Evening"   if 17 <= _hour < 21 else "Night")
        if "selected_time" not in st.session_state:
            st.session_state.selected_time = auto_time
        _tidx = (st.session_state.env.times_of_day.index(st.session_state.selected_time)
                 if st.session_state.selected_time in st.session_state.env.times_of_day else 0)
        time_of_day = st.selectbox("Time of Day", st.session_state.env.times_of_day, index=_tidx)
        st.session_state.selected_time = time_of_day
        language = st.selectbox("Language", ["Hindi", "English", "Punjabi", "Tamil", "Telugu"])
        if st.button(f"⚡ Use Current Time ({auto_time})", use_container_width=True):
            st.session_state.selected_time = auto_time
            st.rerun()

    st.session_state.current_language = language
    accent = MOOD_ACCENT.get(detected_mood, "#1DB954")

    if detected_mood in ["Focus", "Relaxed"]:
        render_pomodoro()

    st.write("")
    _rc, _sc = st.columns([3, 1])
    with _rc:
        get_rec  = st.button("🎧 Get AI Recommendations", use_container_width=True, type="primary")
    with _sc:
        surprise = st.button("🎲 Surprise Me!", use_container_width=True)

    # ── Surprise ──────────────────────────────────────────────────────
    if surprise:
        import random as _rnd
        detected_mood = _rnd.choice(st.session_state.env.moods)
        language      = _rnd.choice(["Hindi", "English", "Punjabi", "Tamil", "Telugu"])
        _sact         = _rnd.choice(st.session_state.env.get_actions())
        st.session_state.feedback_given  = False
        st.session_state.current_state   = st.session_state.env.get_state(detected_mood, time_of_day, st.session_state.last_genre)
        st.session_state.current_action  = _sact
        st.session_state.current_songs   = st.session_state.recommender.recommend_songs(detected_mood, _sact, language, n=3)
        st.session_state.current_mood    = detected_mood
        show_toast(f"🎲 Surprise! {detected_mood} + {_sact}", mood=detected_mood)
        st.rerun()

    # ── Get Recommendations ───────────────────────────────────────────
    if get_rec:
        st.session_state.feedback_given = False
        _skel_ph = st.empty()
        with _skel_ph.container():
            render_skeleton_cards(3)
        _state  = st.session_state.env.get_state(detected_mood, time_of_day, st.session_state.last_genre)
        _action = st.session_state.agent.choose_action(_state)
        st.session_state.current_state  = _state
        st.session_state.current_action = _action
        st.session_state.current_songs  = st.session_state.recommender.recommend_songs(
            detected_mood, _action, language, n=3)
        _skel_ph.empty()
        st.rerun()

    # ── Display Songs ─────────────────────────────────────────────────
    if st.session_state.current_songs:
        st.divider()
        _quote = st.session_state.nlp.generate_quote(detected_mood)
        st.markdown(
            f"<div style='text-align:center;border-radius:8px;border:1px solid {accent}44;"
            f"padding:15px;margin-bottom:20px;background:rgba(0,0,0,0.4);backdrop-filter:blur(5px);'>"
            f"<p style='font-style:italic;color:{accent};font-size:1.2rem;margin:0;'>{_quote}</p>"
            f"</div>", unsafe_allow_html=True)

        c_state = st.session_state.current_state
        st.markdown(f"### 🎶 Recommended for: {c_state.replace('_', ' | ') if c_state else ''}")

        _favs_list = [f["song"] for f in load_favourites(st.session_state.username)]

        for _i, _song in enumerate(st.session_state.current_songs):
            _is_fav   = _song["Song"] in _favs_list
            _fav_icon = "❤️" if _is_fav else "🤍"

            render_song_card_with_art(_song, detected_mood)
            st.markdown(get_yt_embed_html(
                _song.get("URL", ""), _song["Song"],
                _song.get("Language", "Hindi"), _song.get("SpotifyURL", "")),
                unsafe_allow_html=True)

            _fc, _qc, _ = st.columns([1, 1, 3])
            with _fc:
                if st.button(f"{_fav_icon} Favourite", key=f"fav_{_i}_{_song['Song']}"):
                    _res = toggle_favourite(st.session_state.username, _song["Song"],
                                           _song["Mood"], _song["Genre"])
                    show_toast(f"{'Added to' if _res == 'added' else 'Removed from'} favourites!",
                               mood=detected_mood)
                    st.rerun()
            with _qc:
                _in_q  = _song["Song"] in st.session_state.playlist_queue
                _q_lbl = "✅ In Queue" if _in_q else "➕ Add to Queue"
                if st.button(_q_lbl, key=f"queue_{_i}_{_song['Song']}", disabled=_in_q):
                    st.session_state.playlist_queue.append(_song["Song"])
                    st.rerun()
            st.write("")

        # xAI expander
        with st.expander("🤖 Why did the AI choose this? (xAI)"):
            _c_action = st.session_state.current_action
            _q_val    = st.session_state.agent.get_q_value(c_state, _c_action)
            st.write(f"Chose **{_c_action}** for state `{c_state}` — Priority Score: **{_q_val:.2f}**")
            st.caption("Likes (+10), Listen (+2), Skip (-5) update this score.")

        # Share playlist
        _sh_col, _ = st.columns([2, 3])
        with _sh_col:
            share_note = st.text_input("Add a note (optional)",
                                       placeholder="Feeling great today!", key="share_note")
            if st.button("🌐 Share this Playlist to Community", use_container_width=True):
                share_playlist(st.session_state.username,
                               [s["Song"] for s in st.session_state.current_songs],
                               detected_mood, share_note)
                st.success("Shared to Community tab!")

        # Feedback
        st.markdown("### 👇 Give Feedback")
        if not st.session_state.feedback_given:
            _ff1, _ff2, _ff3 = st.columns(3)
            _feedback = None; _reward = None
            with _ff1:
                if st.button("👍 Like (+10)",   use_container_width=True): _feedback, _reward = "like",   10
            with _ff2:
                if st.button("🎧 Listen (+2)", use_container_width=True): _feedback, _reward = "listen",  2
            with _ff3:
                if st.button("⏭️ Skip (-5)",   use_container_width=True): _feedback, _reward = "skip",   -5

            if _feedback is not None:
                _state  = st.session_state.current_state
                _action = st.session_state.current_action
                _ns     = st.session_state.env.get_state(detected_mood, time_of_day, _action)
                st.session_state.agent.learn(_state, _action, _reward, _ns)
                st.session_state.last_genre     = _action
                st.session_state.feedback_given = True
                save_history_entry(st.session_state.username,
                                   st.session_state.current_songs,
                                   detected_mood, _action, _feedback)
                # Update now-playing state
                if st.session_state.current_songs:
                    _np = st.session_state.current_songs[0]
                    st.session_state.now_playing_song      = _np["Song"]
                    st.session_state.now_playing_mood      = _np.get("Mood", detected_mood)
                    st.session_state.now_playing_genre     = _np.get("Genre", "")
                    st.session_state.now_playing_song_dict = _np
                _, _new_badges = update_stats(st.session_state.username,
                                              detected_mood, _action, _feedback)
                if _new_badges:
                    st.session_state.new_badges = _new_badges
                if _reward > 0:
                    for _s in st.session_state.current_songs:
                        st.session_state.playlist_queue.append(_s["Song"])
                    st.success(f"✅ {_feedback.capitalize()} recorded! Songs added to queue.")
                else:
                    st.success(f"✅ {_feedback.capitalize()} recorded.")
                time.sleep(1)
                st.rerun()
        else:
            st.success("Feedback recorded. Get new recommendations!")

        # Star ratings
        st.markdown("#### ⭐ Rate These Songs")
        st.caption("Zyada accurate recommendations ke liye har song ko rate karo (1-5 stars).")
        for _song in st.session_state.current_songs:
            _sname    = _song["Song"]
            _curr_r   = get_rating(st.session_state.username, _sname)
            _r_cols   = st.columns([3, 1, 1, 1, 1, 1])
            _r_cols[0].markdown(f"🎵 **{_sname}**")
            for _idx, _slbl in enumerate(["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"], 1):
                _btype = "primary" if _curr_r == _idx else "secondary"
                if _r_cols[_idx].button(_slbl, key=f"rate_{_sname}_{_idx}", type=_btype):
                    _xp_e = save_rating(st.session_state.username, _sname, _idx)
                    if _xp_e:
                        _rstats = load_stats(st.session_state.username)
                        _rstats["xp"] = _rstats.get("xp", 0) + _xp_e
                        save_stats(st.session_state.username, _rstats)
                    show_toast(f"{'⭐' * _idx} Rated {_sname}!", mood=detected_mood)
                    st.rerun()

        # Content-based similar songs
        with st.expander("🔗 Similar Songs (Content AI)"):
            _similar = get_similar_songs(
                st.session_state.current_songs[0]["Song"], n=5,
                language_filter=language)
            if _similar:
                for _sim in _similar:
                    _sp2 = f"https://open.spotify.com/search/{_sim['Song'].replace(' ','%20')}"
                    _yt2 = f"https://www.youtube.com/results?search_query={_sim['Song'].replace(' ','+')}"
                    st.markdown(
                        f"<div class='history-card' style='padding:10px 16px;'>"
                        f"🎵 <b>{_sim['Song']}</b> &nbsp;"
                        f"<span style='opacity:0.65;font-size:0.82rem;'>"
                        f"{_sim['Mood']} · {_sim['Genre']} · Match: {_sim.get('similarity',0)}%"
                        f"</span>&nbsp;&nbsp;"
                        f"<a href='{_sp2}' target='_blank' style='color:#1DB954;font-size:0.82rem;'>Spotify</a> "
                        f"<a href='{_yt2}' target='_blank' style='color:#ff4444;font-size:0.82rem;'>YouTube</a>"
                        f"</div>", unsafe_allow_html=True)
            else:
                st.caption("No similar songs found for this language filter.")

# ══════════════════════════════════════════════════════════════════════
# TAB: TASTE MATCH
# ══════════════════════════════════════════════════════════════════════
with tab_match:
    st.header("🤝 AI Friend Match")
    st.write("Compare your musical DNA with another user's Q-Table.")
    _tm_files = glob.glob(os.path.join(_DIR, "q_table_*.json"))
    _other_users = [
        os.path.basename(_f).replace("q_table_", "").replace(".json", "")
        for _f in _tm_files
        if "admin" not in _f and
        os.path.basename(_f).replace("q_table_", "").replace(".json", "") != st.session_state.username
    ]
    if not _other_users:
        st.info("No other users found. Ask a friend to sign up!")
    else:
        _friend = st.selectbox("Select a friend:", _other_users)
        if st.button("Calculate Match %", type="primary"):
            _f_agent = QLearningAgent(actions=st.session_state.env.get_actions(), username=_friend)
            _my_tbl  = st.session_state.agent.q_table
            _f_tbl   = _f_agent.q_table
            _common  = set(_my_tbl.keys()) & set(_f_tbl.keys())
            if not _common:
                st.warning("Not enough overlapping sessions yet.")
            else:
                _matches = sum(1 for _s in _common
                               if max(_my_tbl[_s], key=_my_tbl[_s].get) ==
                                  max(_f_tbl[_s],  key=_f_tbl[_s].get))
                _pct = int((_matches / len(_common)) * 100)
                _fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=_pct,
                    title={"text": f"You & {_friend}"},
                    gauge={"axis": {"range": [0, 100]},
                           "bar":  {"color": "#1DB954"},
                           "steps": [{"range": [0, 40],  "color": "#2d2d2d"},
                                     {"range": [40, 70], "color": "#1a3a1a"},
                                     {"range": [70, 100],"color": "#0d4d0d"}]}))
                _fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=300)
                st.plotly_chart(_fig, use_container_width=True)
                if _pct > 70:   st.success(f"🎉 {_pct}% Match — You two are musical soulmates!")
                elif _pct > 40: st.info(f"🎵 {_pct}% Match — Good vibes, similar taste!")
                else:           st.warning(f"🎭 {_pct}% Match — Opposites attract!")

# ══════════════════════════════════════════════════════════════════════
# TAB: COMMUNITY
# ══════════════════════════════════════════════════════════════════════
with tab_social:
    st.header("🌐 Community")
    _s1, _s2, _s3 = st.tabs(["🏆 Leaderboard", "👥 Friends", "🎵 Playlists"])

    # ── Leaderboard ──────────────────────────────────────────────────
    with _s1:
        st.subheader("🏆 Global Leaderboard")
        _lb = get_leaderboard_top(20)
        if not _lb:
            st.info("Leaderboard is empty. Start earning XP to appear here!")
        else:
            _my_rank, _my_xp = get_user_rank(st.session_state.username)
            if _my_rank:
                st.markdown(
                    f"<div style='text-align:center;background:rgba(255,255,255,0.05);"
                    f"border:1px solid #1DB95455;border-radius:12px;padding:12px;margin-bottom:16px;'>"
                    f"🎯 Your Rank: <b>#{_my_rank}</b> &nbsp;|&nbsp; ⚡ {_my_xp} XP"
                    f"</div>", unsafe_allow_html=True)
            for _ri, _ru in enumerate(_lb, 1):
                _medal = {1:"🥇",2:"🥈",3:"🥉"}.get(_ri, f"#{_ri}")
                _isme  = _ru["username"] == st.session_state.username
                _rbg   = "rgba(29,185,84,0.12)" if _isme else "rgba(255,255,255,0.04)"
                _rbd   = "#1DB954" if _isme else "rgba(255,255,255,0.1)"
                st.markdown(
                    f"<div style='background:{_rbg};border:1px solid {_rbd};"
                    f"border-radius:10px;padding:10px 16px;margin-bottom:8px;"
                    f"display:flex;justify-content:space-between;align-items:center;'>"
                    f"<span>{_medal} &nbsp; <b>{_ru['username']}</b>"
                    f"{'&nbsp; 👈 You' if _isme else ''}</span>"
                    f"<span style='opacity:0.8;'>{_ru['level']} &nbsp;|&nbsp; ⚡ {_ru['xp']} XP</span>"
                    f"</div>", unsafe_allow_html=True)

    # ── Friends ───────────────────────────────────────────────────────
    with _s2:
        st.subheader("👥 Friends")
        _all_q    = glob.glob(os.path.join(_DIR, "q_table_*.json"))
        _all_us   = [os.path.basename(_f).replace("q_table_","").replace(".json","")
                     for _f in _all_q
                     if "admin" not in _f and
                     os.path.basename(_f).replace("q_table_","").replace(".json","") != st.session_state.username]
        _fr_data  = load_friends(st.session_state.username)
        _following = _fr_data.get("following", [])
        _followers = _fr_data.get("followers", [])

        _frc1, _frc2 = st.columns(2)
        with _frc1:
            st.markdown(f"**Following ({len(_following)})**")
            for _u in _following:
                _uc1, _uc2 = st.columns([3, 1])
                _uc1.write(f"👤 {_u}")
                if _uc2.button("Unfollow", key=f"unfollow_{_u}"):
                    _, _umsg = unfollow_user(st.session_state.username, _u)
                    show_toast(_umsg, mood=st.session_state.current_mood)
                    st.rerun()
            if not _following:
                st.caption("Not following anyone yet.")
        with _frc2:
            st.markdown(f"**Followers ({len(_followers)})**")
            for _u in _followers:
                st.write(f"👤 {_u}")
            if not _followers:
                st.caption("No followers yet.")

        st.divider()
        st.markdown("**Discover Users**")
        if not _all_us:
            st.caption("No other users found yet.")
        else:
            for _u in _all_us:
                _dc1, _dc2 = st.columns([3, 1])
                _dc1.write(f"👤 {_u}")
                if _u in _following:
                    _dc2.button("✅ Following", key=f"already_{_u}", disabled=True)
                else:
                    if _dc2.button("Follow", key=f"follow_{_u}", type="primary"):
                        _, _fmsg = follow_user(st.session_state.username, _u)
                        show_toast(_fmsg, mood=st.session_state.current_mood)
                        st.rerun()

    # ── Community Playlists ───────────────────────────────────────────
    with _s3:
        st.subheader("🎵 Community Playlists")
        _playlists = load_shared_playlists()
        if not _playlists:
            st.info("No shared playlists yet. Be the first to share from the Recommender tab!")
        else:
            _mf = st.selectbox("Filter by Mood",
                               ["All"] + st.session_state.env.moods, key="comm_filter")
            _shown = [_p for _p in reversed(_playlists)
                      if _mf == "All" or _p["mood"] == _mf]
            for _p in _shown[:20]:
                _pc1, _pc2 = st.columns([4, 1])
                with _pc1:
                    st.markdown(
                        f"<div class='history-card'>"
                        f"<b>👤 {_p['username']}</b> &nbsp;"
                        f"<span style='opacity:0.6;font-size:0.85rem;'>{_p['timestamp']}</span><br>"
                        f"🎭 <b>{_p['mood']}</b> &nbsp; 🎵 {', '.join(_p['songs'])}<br>"
                        f"{'<i style=\"opacity:0.7;\">💬 ' + _p['note'] + '</i>' if _p.get('note') else ''}"
                        f"</div>", unsafe_allow_html=True)
                with _pc2:
                    _liked = st.session_state.username in _p.get("liked_by", [])
                    _lbl   = f"❤️ {_p['likes']}" if _liked else f"🤍 {_p['likes']}"
                    if st.button(_lbl, key=f"like_p_{_p['id']}", disabled=_liked):
                        like_shared_playlist(_p["id"], st.session_state.username)
                        st.rerun()
                # Comments
                _cmnts = get_comments(_p["id"])
                with st.expander(f"💬 Comments ({len(_cmnts)})"):
                    for _cm in _cmnts:
                        st.markdown(
                            f"<div class='comment-bubble'>"
                            f"<b style='color:#1DB954;'>@{_cm['username']}</b> "
                            f"<span style='opacity:0.5;font-size:0.78rem;'>{_cm['timestamp']}</span><br>"
                            f"{_cm['text']}</div>", unsafe_allow_html=True)
                    with st.form(key=f"cmt_form_{_p['id']}"):
                        _cmt_txt = st.text_input("Add a comment…",
                                                 key=f"cmt_inp_{_p['id']}",
                                                 label_visibility="collapsed",
                                                 placeholder="Your thoughts…")
                        if st.form_submit_button("Post 💬") and _cmt_txt.strip():
                            add_comment(_p["id"], st.session_state.username, _cmt_txt.strip())
                            st.rerun()

# ══════════════════════════════════════════════════════════════════════
# TAB: ANALYTICS
# ══════════════════════════════════════════════════════════════════════
with tab_analytics:
    render_dashboard(st.session_state.agent)
    _hist_a = load_history(st.session_state.username)
    if len(_hist_a) >= 3:
        st.divider()
        st.subheader("📊 Your Mood Trend Over Time")
        _df_h = pd.DataFrame(_hist_a)
        _df_h["date"] = pd.to_datetime(_df_h["timestamp"]).dt.date
        _mood_trend = _df_h.groupby(["date", "mood"]).size().reset_index(name="count")
        _fig2 = px.line(_mood_trend, x="date", y="count", color="mood",
                        color_discrete_map={"Happy":"#FFD700","Sad":"#6495ED",
                                            "Focus":"#FF8C00","Relaxed":"#1DB954"},
                        title="Mood Frequency Over Time")
        _fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(_fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# TAB: HISTORY
# ══════════════════════════════════════════════════════════════════════
with tab_history:
    st.header("📜 Your Listening History")
    _hist = load_history(st.session_state.username)
    if not _hist:
        st.info("No history yet. Start getting recommendations!")
    else:
        _df_hist = pd.DataFrame(_hist)
        _hc1, _hc2, _hc3, _hc4 = st.columns(4)
        _hc1.metric("Total Sessions",  len(_hist))
        _hc2.metric("Favourite Mood",  _df_hist["mood"].mode()[0])
        _hc3.metric("Favourite Genre", _df_hist["genre"].mode()[0])
        _hc4.metric("Likes",           len(_df_hist[_df_hist["feedback"] == "like"]))
        st.divider()

        # Export favourites
        _favs_exp = load_favourites(st.session_state.username)
        if _favs_exp:
            _exp_txt = export_playlist_text(st.session_state.username, _favs_exp, "Favourites")
            st.download_button("⬇️ Export Favourites as .txt", _exp_txt,
                               file_name=f"{st.session_state.username}_playlist.txt")

        st.subheader("Recent Sessions")
        for _entry in reversed(_hist[-25:]):
            _fc_icon = {"like":"🟢","listen":"🔵","skip":"🔴"}.get(_entry["feedback"], "⚪")
            st.markdown(
                f"<div class='history-card'>"
                f"<b>{_entry['timestamp']}</b> &nbsp; "
                f"{_fc_icon} <b>{_entry['feedback'].capitalize()}</b><br>"
                f"🎭 {_entry['mood']} &nbsp; 🎸 {_entry['genre']}<br>"
                f"🎵 {', '.join(_entry['songs'])}"
                f"</div>", unsafe_allow_html=True)

        if st.button("🗑️ Clear History", type="secondary"):
            _hf = os.path.join(_DIR, f"history_{st.session_state.username}.json")
            if os.path.exists(_hf):
                os.remove(_hf)
            st.success("Cleared.")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════
# TAB: MOOD JOURNAL
# ══════════════════════════════════════════════════════════════════════
with tab_journal:
    st.header("📓 Mood Journal")
    st.write("Write how you're feeling today. Track your emotional journey over time.")
    with st.form("journal_form"):
        j_mood = st.selectbox("Today's Mood", st.session_state.env.moods)
        j_note = st.text_area("Write your thoughts...",
                              placeholder="Today was a tough day but music helped...")
        if st.form_submit_button("Save Entry", use_container_width=True):
            if j_note.strip():
                save_journal_entry(st.session_state.username, j_mood, j_note.strip())
                st.success("Journal entry saved! 📝")
            else:
                st.warning("Write something first.")
    st.divider()
    _journal = load_journal(st.session_state.username)
    if not _journal:
        st.info("No journal entries yet.")
    else:
        st.subheader(f"Your Entries ({len(_journal)})")
        _df_j = pd.DataFrame(_journal)
        _mc   = _df_j["mood"].value_counts().reset_index()
        _mc.columns = ["mood", "count"]
        _fig_pie = px.pie(_mc, names="mood", values="count", color="mood",
                          color_discrete_map={"Happy":"#FFD700","Sad":"#6495ED",
                                              "Focus":"#FF8C00","Relaxed":"#1DB954"},
                          title="Your Mood Distribution")
        _fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(_fig_pie, use_container_width=True)
        for _je in reversed(_journal[-15:]):
            _jc = {"Happy":"#FFD700","Sad":"#6495ED",
                   "Focus":"#FF8C00","Relaxed":"#1DB954"}.get(_je["mood"], "#fff")
            st.markdown(
                f"<div class='history-card' style='border-left:4px solid {_jc};'>"
                f"<span style='opacity:0.6;font-size:0.85rem;'>{_je['date']} {_je['time']}</span>"
                f" &nbsp; <b style='color:{_jc};'>{_je['mood']}</b><br>"
                f"<p style='margin:6px 0 0 0;'>{_je['note']}</p>"
                f"</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# TAB: PROFILE / GAMIFICATION
# ══════════════════════════════════════════════════════════════════════
with tab_profile:
    _pstats = load_stats(st.session_state.username)
    _pxp    = _pstats.get("xp", 0)
    _plevel = get_level(_pxp)
    st.header(f"👤 {st.session_state.username}")

    _lvl_thresh  = [0, 50, 150, 300, 600, 1000]
    _next_thresh = next((t for t in _lvl_thresh if t > _pxp), 1000)
    _prev_thresh = max((t for t in _lvl_thresh if t <= _pxp), default=0)
    _xp_prog     = (_pxp - _prev_thresh) / max(_next_thresh - _prev_thresh, 1)
    st.markdown(f"### {_plevel}")
    st.progress(min(_xp_prog, 1.0))
    st.caption(f"⚡ {_pxp} XP — {_next_thresh - _pxp} XP to next level")
    st.divider()

    _ps1, _ps2, _ps3, _ps4 = st.columns(4)
    _ps1.metric("🔥 Streak",    f"{_pstats.get('streak', 0)} days")
    _ps2.metric("🎵 Sessions",  _pstats.get("total_sessions", 0))
    _ps3.metric("👍 Likes",     _pstats.get("total_likes", 0))
    _ps4.metric("⏭️ Skips",     _pstats.get("total_skips", 0))
    st.divider()

    # Badges
    st.subheader("🏅 Badges")
    _earned = _pstats.get("earned_badges", [])
    _badge_html = ""
    for _badge, _binfo in BADGES.items():
        if _badge in _earned:
            _badge_html += (f"<div class='badge-card'>"
                            f"<div style='font-size:1.5rem;'>{_badge.split()[0]}</div>"
                            f"<div style='font-size:0.8rem;font-weight:bold;'>{' '.join(_badge.split()[1:])}</div>"
                            f"<div style='font-size:0.7rem;opacity:0.7;'>{_binfo['desc']}</div></div>")
        else:
            _badge_html += (f"<div class='badge-card' style='opacity:0.3;filter:grayscale(1);'>"
                            f"<div style='font-size:1.5rem;'>🔒</div>"
                            f"<div style='font-size:0.8rem;'>{' '.join(_badge.split()[1:])}</div>"
                            f"<div style='font-size:0.7rem;opacity:0.7;'>{_binfo['desc']}</div></div>")
    st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:4px;'>{_badge_html}</div>",
                unsafe_allow_html=True)
    st.divider()

    # Moods & Genres tried
    _mc1, _mc2 = st.columns(2)
    with _mc1:
        st.subheader("🎭 Moods Explored")
        for _m in st.session_state.env.moods:
            st.write(f"{'✅' if _m in _pstats.get('moods_tried', []) else '⬜'} {_m}")
    with _mc2:
        st.subheader("🎸 Genres Explored")
        for _g in st.session_state.env.get_actions():
            st.write(f"{'✅' if _g in _pstats.get('genres_tried', []) else '⬜'} {_g}")
    st.divider()

    # Change password
    with st.expander("🔑 Change Password"):
        _old_p  = st.text_input("Current Password",     type="password", key="chg_old")
        _new_p  = st.text_input("New Password",          type="password", key="chg_new")
        _new_p2 = st.text_input("Confirm New Password",  type="password", key="chg_new2")
        if st.button("Update Password"):
            _ok, _ = login_user(st.session_state.username, _old_p)
            if not _ok:            st.error("Current password is wrong.")
            elif _new_p != _new_p2: st.error("Passwords do not match.")
            elif len(_new_p) < 4:   st.error("Too short.")
            else:
                _uf = os.path.join(_DIR, "users.json")
                with open(_uf, "r") as _f: _users = json.load(_f)
                _users[st.session_state.username]["password"] = hashlib.sha256(_new_p.encode()).hexdigest()
                with open(_uf, "w") as _f: json.dump(_users, _f)
                st.success("Password updated!")

    # Music DNA Card
    st.divider()
    st.subheader("🧬 Your Music DNA Card")
    _r_stats   = get_rating_stats(st.session_state.username)
    _top_rated = get_top_rated_songs(st.session_state.username, n=3)
    _fav_mood  = max(_pstats.get("mood_counts", {"Relaxed": 1}),
                     key=_pstats.get("mood_counts", {"Relaxed": 1}).get,
                     default="Relaxed")
    _fav_genre = (_pstats.get("genres_tried", ["—"])[0]
                  if _pstats.get("genres_tried") else "—")
    _dna_acc   = MOOD_ACCENT.get(_fav_mood, "#1DB954")
    _top_html  = "".join(f"<div style='margin:3px 0;'>{'⭐'*_r} {_sn}</div>"
                         for _sn, _r in _top_rated) or \
                 "<div style='opacity:0.5;'>Rate songs to see your top picks!</div>"
    st.markdown(f"""
    <div class='dna-card' style='border-color:{_dna_acc}55;'>
        <div style='font-size:2.5rem;margin-bottom:4px;'>{MOOD_EMOJI.get(_fav_mood,'🎵')}</div>
        <h2 style='margin:0;background:-webkit-linear-gradient(45deg,{_dna_acc},#fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            {st.session_state.username}
        </h2>
        <p style='opacity:0.6;margin:4px 0 18px 0;font-size:0.9rem;'>{_plevel}</p>
        <div style='display:flex;justify-content:center;gap:32px;flex-wrap:wrap;margin-bottom:18px;'>
            <div><div style='font-size:1.6rem;font-weight:800;color:{_dna_acc};'>{_pstats.get('total_sessions',0)}</div><div style='opacity:0.6;font-size:0.8rem;'>Sessions</div></div>
            <div><div style='font-size:1.6rem;font-weight:800;color:{_dna_acc};'>{_pstats.get('streak',0)}🔥</div><div style='opacity:0.6;font-size:0.8rem;'>Streak</div></div>
            <div><div style='font-size:1.6rem;font-weight:800;color:{_dna_acc};'>{_pxp}⚡</div><div style='opacity:0.6;font-size:0.8rem;'>XP</div></div>
            <div><div style='font-size:1.6rem;font-weight:800;color:{_dna_acc};'>{_r_stats["avg"]}★</div><div style='opacity:0.6;font-size:0.8rem;'>Avg Rating</div></div>
        </div>
        <div style='display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-bottom:16px;'>
            <span style='background:{_dna_acc}22;border:1px solid {_dna_acc}55;border-radius:20px;padding:4px 14px;font-size:0.85rem;'>🎭 {_fav_mood} Lover</span>
            <span style='background:{_dna_acc}22;border:1px solid {_dna_acc}55;border-radius:20px;padding:4px 14px;font-size:0.85rem;'>🎸 {_fav_genre} Fan</span>
            <span style='background:{_dna_acc}22;border:1px solid {_dna_acc}55;border-radius:20px;padding:4px 14px;font-size:0.85rem;'>🏅 {len(_earned)} Badges</span>
        </div>
        <div style='text-align:left;max-width:320px;margin:0 auto;'>
            <div style='opacity:0.6;font-size:0.78rem;margin-bottom:6px;'>🏆 TOP RATED SONGS</div>
            {_top_html}
        </div>
        <p style='opacity:0.3;font-size:0.7rem;margin:16px 0 0 0;'>
            PLM Devs AI Music Recommender · {datetime.date.today().strftime("%d %b %Y")}
        </p>
    </div>""", unsafe_allow_html=True)
    st.caption("💡 Screenshot karo aur share karo dosto ke saath!")

# ══════════════════════════════════════════════════════════════════════
# TAB: AI CHATBOT
# ══════════════════════════════════════════════════════════════════════
with tab_chat:
    st.header("🤖 AI Music Chatbot")
    st.write("Baat karo AI se — koi bhi song request karo natural language mein!")

    # Streak reminder
    _cn_stats   = load_stats(st.session_state.username)
    _last_act   = _cn_stats.get("last_active_date")
    _yest       = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if _last_act and _last_act < _yest:
        st.warning(
            f"⚠️ **Streak Alert!** Tumhari 🔥 {_cn_stats.get('streak',0)}-day streak "
            f"toot sakti hai! Aaj koi recommendation lo.")
    st.divider()

    # Chat history display
    for _msg in st.session_state.chat_history:
        if _msg["role"] == "user":
            st.markdown(
                f"<div style='text-align:right;margin:8px 0;'>"
                f"<span style='background:#1DB954;color:black;padding:8px 14px;"
                f"border-radius:18px 18px 4px 18px;display:inline-block;max-width:80%;'>"
                f"👤 {_msg['content']}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='text-align:left;margin:8px 0;'>"
                f"<span style='background:rgba(255,255,255,0.1);color:white;padding:8px 14px;"
                f"border-radius:18px 18px 18px 4px;display:inline-block;max-width:80%;'>"
                f"🤖 {_msg['content']}</span></div>", unsafe_allow_html=True)
        if _msg.get("songs"):
            for _csong in _msg["songs"]:
                _csp = f"https://open.spotify.com/search/{_csong['Song'].replace(' ','%20')}"
                _cyt = f"https://www.youtube.com/results?search_query={_csong['Song'].replace(' ','+')}"
                st.markdown(
                    f"<div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.15);"
                    f"border-radius:12px;padding:12px 16px;margin:4px 0 4px 20px;'>"
                    f"<b>🎵 {_csong['Song']}</b> &nbsp;"
                    f"<span style='opacity:0.7;font-size:0.85rem;'>"
                    f"{_csong['Mood']} · {_csong['Genre']} · {_csong.get('Language','')}</span><br>"
                    f"<a href='{_csp}' target='_blank' style='color:#1DB954;margin-right:12px;'>🎧 Spotify</a>"
                    f"<a href='{_cyt}' target='_blank' style='color:#FF4444;'>▶ YouTube</a>"
                    f"</div>", unsafe_allow_html=True)

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        _cc1, _cc2 = st.columns([5, 1])
        _user_msg  = _cc1.text_input("Message", placeholder="e.g. 'sad hindi songs do' or 'party punjabi'",
                                     label_visibility="collapsed")
        _sent      = _cc2.form_submit_button("Send 📤", use_container_width=True)

    if _sent and _user_msg.strip():
        st.session_state.chat_history.append({"role":"user","content":_user_msg,"songs":[]})
        _resp = st.session_state.chatbot.respond(_user_msg)
        st.session_state.chat_history.append({
            "role":"bot","content":_resp["text"],"songs":_resp["songs"]})
        st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# TAB: WEEKLY REPORT
# ══════════════════════════════════════════════════════════════════════
with tab_report:
    st.header("📊 Weekly Music Report")
    st.write("Teri is hafte ki poori music journey ek jagah.")
    _report = generate_weekly_report(st.session_state.username)
    if not _report:
        st.info("Abhi tak koi data nahi hai. Recommendations lo aur feedback do!")
    else:
        st.markdown(f"### 📅 Period: {_report['period']}")
        st.divider()
        _rm1,_rm2,_rm3,_rm4,_rm5 = st.columns(5)
        _rm1.metric("🎵 Sessions", _report["total_sessions"])
        _rm2.metric("👍 Likes",    _report["likes"])
        _rm3.metric("🎧 Listens",  _report["listens"])
        _rm4.metric("⏭️ Skips",    _report["skips"])
        _rm5.metric("🔥 Streak",   f"{_report['streak']} days")
        st.divider()
        _racc = MOOD_ACCENT.get(_report["top_mood"], "#1DB954")
        st.markdown(
            f"<div style='background:{_racc}22;border:1px solid {_racc};border-radius:12px;"
            f"padding:16px 20px;margin-bottom:16px;'>"
            f"<h3 style='margin:0;color:{_racc};'>💡 Weekly Insight</h3>"
            f"<p style='margin:8px 0 0 0;font-size:1.1rem;'>{_report['insight']}</p>"
            f"<p style='margin:4px 0 0 0;opacity:0.7;'>Top Mood: <b>{_report['top_mood']}</b> &nbsp;|&nbsp; "
            f"Top Genre: <b>{_report['top_genre']}</b> &nbsp;|&nbsp; ⚡ XP Gained: <b>{_report['xp_gained']}</b></p>"
            f"</div>", unsafe_allow_html=True)
        _rch1, _rch2 = st.columns(2)
        with _rch1:
            if _report["mood_counts"]:
                _dfm = pd.DataFrame(list(_report["mood_counts"].items()), columns=["Mood","Count"])
                _figm = px.bar(_dfm, x="Mood", y="Count", color="Mood",
                               color_discrete_map={"Happy":"#FFD700","Sad":"#6495ED",
                                                   "Focus":"#FF8C00","Relaxed":"#1DB954"},
                               title="Mood Breakdown")
                _figm.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    font_color="white", showlegend=False)
                st.plotly_chart(_figm, use_container_width=True)
        with _rch2:
            if _report["genre_counts"]:
                _dfg = pd.DataFrame(list(_report["genre_counts"].items()), columns=["Genre","Count"])
                _figg = px.pie(_dfg, names="Genre", values="Count", title="Genre Mix",
                               color_discrete_sequence=px.colors.qualitative.Set3)
                _figg.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(_figg, use_container_width=True)
        if not _report["daily_activity"].empty:
            _figd = px.bar(_report["daily_activity"], x="date", y="sessions",
                           title="Daily Activity This Week",
                           color_discrete_sequence=[_racc])
            _figd.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(_figd, use_container_width=True)
        if _report["top_songs"]:
            st.subheader("🏆 Top Songs This Week")
            for _ri2, (_rsong, _rcount) in enumerate(_report["top_songs"], 1):
                _rsp = f"https://open.spotify.com/search/{_rsong.replace(' ','%20')}"
                st.markdown(
                    f"<div class='history-card'><b>#{_ri2}</b> &nbsp; 🎵 {_rsong} &nbsp;"
                    f"<span style='opacity:0.6;'>({_rcount}x)</span> &nbsp;"
                    f"<a href='{_rsp}' target='_blank' style='color:#1DB954;'>🎧 Spotify</a>"
                    f"</div>", unsafe_allow_html=True)
        st.divider()
        st.download_button(
            "⬇️ Download Report as .txt",
            export_report_text(st.session_state.username, _report),
            file_name=f"{st.session_state.username}_weekly_report.txt",
            mime="text/plain")

# ══════════════════════════════════════════════════════════════════════
# TAB: SEARCH SONGS
# ══════════════════════════════════════════════════════════════════════
with tab_search:
    st.header("🔍 Search Songs")
    st.write("Directly search the entire database by name, mood, genre, or language.")
    try:
        _df_all = pd.read_csv(os.path.join(_DIR, "data", "songs.csv"))
    except Exception:
        _df_all = pd.DataFrame()

    # ── Lyrics / Keyword Search ──────────────────────────────────────
    render_lyrics_search(_df_all)
    st.divider()

    _sf1,_sf2,_sf3,_sf4 = st.columns([3,1,1,1])
    with _sf1:
        _sq = st.text_input("🔎 Search by song name",
                            placeholder="e.g. Kesariya, Espresso, Naatu...",
                            key="search_q")
    with _sf2:
        _fm = st.selectbox("Mood",     ["All"]+st.session_state.env.moods, key="sf_mood")
    with _sf3:
        _fg = st.selectbox("Genre",    ["All"]+st.session_state.env.get_actions(), key="sf_genre")
    with _sf4:
        _fl = st.selectbox("Language", ["All","Hindi","English","Punjabi","Tamil","Telugu"], key="sf_lang")

    _results = _df_all.copy()
    if _sq.strip():
        _results = _results[_results["Song"].str.contains(_sq.strip(), case=False, na=False)]
    if _fm != "All": _results = _results[_results["Mood"] == _fm]
    if _fg != "All": _results = _results[_results["Genre"] == _fg]
    if _fl != "All": _results = _results[_results["Language"].str.lower() == _fl.lower()]

    st.caption(f"Showing {len(_results)} of {len(_df_all)} songs")
    st.divider()

    if _results.empty:
        st.info("No songs found. Try different filters.")
    else:
        _favs_s = [f["song"] for f in load_favourites(st.session_state.username)]
        for _idx, _row in _results.iterrows():
            _sp3  = f"https://open.spotify.com/search/{str(_row['Song']).replace(' ','%20')}"
            _yt3  = f"https://www.youtube.com/results?search_query={str(_row['Song']).replace(' ','+')}"
            _ifav = _row["Song"] in _favs_s
            _fic  = "❤️" if _ifav else "🤍"
            _mc   = {"Happy":"#FFD700","Sad":"#6495ED",
                     "Focus":"#FF8C00","Relaxed":"#1DB954"}.get(_row.get("Mood",""), "#1DB954")
            _scc, _acc = st.columns([4,1])
            with _scc:
                st.markdown(
                    f"<div class='history-card' style='border-left:4px solid {_mc};'>"
                    f"<b style='font-size:1.05rem;'>🎵 {_row['Song']}</b><br>"
                    f"<span style='opacity:0.7;font-size:0.85rem;'>"
                    f"🎭 {_row.get('Mood','')} &nbsp;·&nbsp; 🎸 {_row.get('Genre','')} &nbsp;·&nbsp; "
                    f"🌐 {_row.get('Language','')} &nbsp;·&nbsp; ⚡ {_row.get('Energy','')}</span><br>"
                    f"<a href='{_sp3}' target='_blank' style='color:#1DB954;margin-right:14px;font-size:0.85rem;'>🎧 Spotify</a>"
                    f"<a href='{_yt3}' target='_blank' style='color:#FF4444;font-size:0.85rem;'>▶ YouTube</a>"
                    f"</div>", unsafe_allow_html=True)
            with _acc:
                if st.button(_fic, key=f"sfav_{_idx}_{_row['Song']}", help="Add/Remove Favourite"):
                    toggle_favourite(st.session_state.username,
                                     _row["Song"], _row.get("Mood",""), _row.get("Genre",""))
                    st.rerun()
                _inqs = _row["Song"] in st.session_state.playlist_queue
                if st.button("✅" if _inqs else "➕",
                             key=f"sq_{_idx}_{_row['Song']}", disabled=_inqs):
                    st.session_state.playlist_queue.append(_row["Song"])
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════
# TAB: AUTO PLAYLIST GENERATOR
# ══════════════════════════════════════════════════════════════════════
with tab_pgen:
    st.header("🎵 Auto Playlist Generator")
    st.write("Apni zaroorat batao — duration, mood, language — AI khud poora playlist bana dega!")

    _pg1, _pg2 = st.columns([1,1])
    with _pg1:
        st.subheader("⚡ Quick Presets")
        for _preset in get_preset_playlists():
            if st.button(_preset["name"], use_container_width=True, key=f"preset_{_preset['name']}"):
                with st.spinner("Generating playlist..."):
                    _psongs, _ptotal = generate_playlist(
                        mood=_preset["mood"], language=_preset["language"],
                        duration_minutes=_preset["duration"],
                        genre=_preset.get("genre"), energy=_preset.get("energy"),
                        avoid_songs=st.session_state.playlist_queue)
                st.session_state.gen_playlist       = _psongs
                st.session_state.gen_playlist_total = _ptotal
                st.rerun()

    with _pg2:
        st.subheader("🎛️ Custom Generator")
        _pgm  = st.selectbox("Mood",      st.session_state.env.moods, key="pg_mood")
        _pgl  = st.selectbox("Language",  ["Hindi","English","Punjabi","Tamil","Telugu"], key="pg_lang")
        _pgd  = st.slider("Duration (minutes)", 10, 120, 30, 5, key="pg_dur")
        _pgg  = st.selectbox("Genre (optional)",  ["Any"]+st.session_state.env.get_actions(), key="pg_genre")
        _pge  = st.selectbox("Energy (optional)", ["Any","Low","Medium","High"], key="pg_energy")
        if st.button("🎵 Generate My Playlist", use_container_width=True,
                     type="primary", key="pg_generate"):
            with st.spinner("Building your playlist..."):
                _psongs, _ptotal = generate_playlist(
                    mood=_pgm, language=_pgl, duration_minutes=_pgd,
                    genre=None if _pgg=="Any" else _pgg,
                    energy=None if _pge=="Any" else _pge,
                    avoid_songs=st.session_state.playlist_queue)
            st.session_state.gen_playlist       = _psongs
            st.session_state.gen_playlist_total = _ptotal
            st.rerun()

    if st.session_state.gen_playlist:
        st.divider()
        st.markdown(
            f"<div style='text-align:center;background:rgba(29,185,84,0.1);"
            f"border:1px solid #1DB95444;border-radius:12px;padding:12px;margin-bottom:16px;'>"
            f"✅ <b>{len(st.session_state.gen_playlist)} songs</b> &nbsp;|&nbsp; "
            f"⏱️ ~{int(st.session_state.gen_playlist_total)} minutes"
            f"</div>", unsafe_allow_html=True)
        if st.button("➕ Add All to Queue", type="primary", key="pg_add_all"):
            for _pgs in st.session_state.gen_playlist:
                if _pgs["Song"] not in st.session_state.playlist_queue:
                    st.session_state.playlist_queue.append(_pgs["Song"])
            st.toast(f"✅ {len(st.session_state.gen_playlist)} songs added!")
            st.rerun()
        for _pi, _pgsong in enumerate(st.session_state.gen_playlist, 1):
            _pgsp = f"https://open.spotify.com/search/{_pgsong['Song'].replace(' ','%20')}"
            _pgyt = f"https://www.youtube.com/results?search_query={_pgsong['Song'].replace(' ','+')}"
            _pgmc = {"Happy":"#FFD700","Sad":"#6495ED",
                     "Focus":"#FF8C00","Relaxed":"#1DB954"}.get(_pgsong.get("Mood",""), "#1DB954")
            _pgc1, _pgc2 = st.columns([4,1])
            with _pgc1:
                st.markdown(
                    f"<div class='pgen-card' style='border-left:4px solid {_pgmc};'>"
                    f"<span style='opacity:0.5;font-size:0.8rem;'>#{_pi} · ⏱️ ~{_pgsong.get('est_duration_min',4.0):.1f} min</span><br>"
                    f"<b style='font-size:1rem;'>🎵 {_pgsong['Song']}</b><br>"
                    f"<span style='opacity:0.65;font-size:0.82rem;'>"
                    f"🎭 {_pgsong.get('Mood','')} · 🎸 {_pgsong.get('Genre','')} · "
                    f"🌐 {_pgsong.get('Language','')} · ⚡ {_pgsong.get('Energy','')}</span><br>"
                    f"<a href='{_pgsp}' target='_blank' style='color:#1DB954;font-size:0.82rem;margin-right:10px;'>🎧 Spotify</a>"
                    f"<a href='{_pgyt}' target='_blank' style='color:#ff4444;font-size:0.82rem;'>▶ YouTube</a>"
                    f"</div>", unsafe_allow_html=True)
            with _pgc2:
                _inqp = _pgsong["Song"] in st.session_state.playlist_queue
                if st.button("✅" if _inqp else "➕",
                             key=f"pgq_{_pi}_{_pgsong['Song']}", disabled=_inqp):
                    st.session_state.playlist_queue.append(_pgsong["Song"])
                    st.rerun()
        st.divider()
        _exp_lines = [f"🎵 Auto Playlist — {st.session_state.username}", "="*40]
        for _ei, _es in enumerate(st.session_state.gen_playlist, 1):
            _exp_lines.append(f"{_ei}. {_es['Song']} ({_es.get('Mood','')} / {_es.get('Genre','')}) "
                              f"~{_es.get('est_duration_min',4.0):.1f}min")
        _exp_lines.append(f"\nTotal: ~{int(st.session_state.gen_playlist_total)} minutes")
        _exp_lines.append("Generated by PLM Devs AI Music Recommender")
        st.download_button("⬇️ Export Playlist as .txt", "\n".join(_exp_lines),
                           file_name=f"{st.session_state.username}_auto_playlist.txt",
                           mime="text/plain")

# ══════════════════════════════════════════════════════════════════════
# NOW PLAYING — sticky bottom bar
# ══════════════════════════════════════════════════════════════════════
if st.session_state.get("now_playing_song"):
    _np_mood  = st.session_state.get("now_playing_mood", "Relaxed")
    _np_color = MOOD_ACCENT.get(_np_mood, "#1DB954")
    render_now_playing_bar_v2(
        song_name   = st.session_state.now_playing_song,
        mood        = _np_mood,
        genre       = st.session_state.get("now_playing_genre", ""),
        queue_count = len(st.session_state.playlist_queue),
        mood_color  = _np_color,
        song        = st.session_state.get("now_playing_song_dict"),
    )
