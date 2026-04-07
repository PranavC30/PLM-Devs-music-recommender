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
from gamification import update_stats, load_stats, get_level, BADGES
from social import (share_playlist, load_shared_playlists, like_shared_playlist,
                    load_favourites, toggle_favourite, export_playlist_text,
                    follow_user, unfollow_user, load_friends, get_leaderboard_top,
                    get_user_rank, update_leaderboard)
from chatbot import MusicChatbot
from weekly_report import generate_weekly_report, export_report_text
from search import SongSearchEngine
from performance import load_songs_dataframe, get_unique_song_values, paginate_items, render_pagination_controls

st.set_page_config(page_title="PLM Devs AI Recommender", page_icon="🎵", layout="wide")

# ═══════════════════════════════════════════════════════
#  MOOD THEME — dynamic background color per mood
# ═══════════════════════════════════════════════════════
MOOD_GRADIENTS = {
    "Happy":   "linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #1a3a1a 100%)",
    "Sad":     "linear-gradient(135deg, #0d0d1a 0%, #1a1a3e 40%, #0d1a2e 100%)",
    "Focus":   "linear-gradient(135deg, #1a0d00 0%, #2e1a00 40%, #1a1a00 100%)",
    "Relaxed": "linear-gradient(135deg, #001a1a 0%, #001a2e 40%, #0d1a1a 100%)",
}
MOOD_ACCENT = {
    "Happy": "#FFD700", "Sad": "#6495ED", "Focus": "#FF8C00", "Relaxed": "#1DB954"
}

def get_yt_embed_html(url: str, song_name: str, language: str = "Hindi", spotify_url: str = "") -> str:
    """
    Priority:
    1. SpotifyURL present → Spotify embed (30-sec preview, works for all languages)
    2. English + YouTube URL → nocookie embed
    3. Fallback → Play on YouTube button
    """
    import re
    query = f"{song_name} official audio {language}".replace(' ', '+')
    yt_direct = str(url).strip() if url and str(url).strip().lower() != 'nan' else \
                f"https://www.youtube.com/results?search_query={query}"

    # 1. Spotify embed
    sp = str(spotify_url).strip() if spotify_url else ""
    if sp and sp.lower() != 'nan' and sp.startswith('http'):
        if '/embed/' not in sp:
            sp = sp.replace('open.spotify.com/track/', 'open.spotify.com/embed/track/')
        return (
            f"<div style='border-radius:14px;overflow:hidden;margin:10px 0 16px 0;"
            f"box-shadow:0 4px 20px rgba(0,0,0,0.4);'>"
            f"<iframe src='{sp}?utm_source=generator&theme=0' "
            f"width='100%' height='152' frameborder='0' allowfullscreen='' "
            f"allow='autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture' "
            f"loading='lazy' style='border-radius:14px;display:block;'></iframe>"
            f"</div>"
        )

    # 2. English — YouTube nocookie embed
    vid_id = None
    if url and str(url).strip() and str(url).strip().lower() != 'nan':
        m = re.search(r'(?:v=|youtu\.be/|/embed/)([A-Za-z0-9_-]{11})', str(url))
        if m:
            vid_id = m.group(1)

    if vid_id and language == 'English':
        return (
            f"<div style='border-radius:14px;overflow:hidden;margin:10px 0 16px 0;"
            f"box-shadow:0 4px 20px rgba(0,0,0,0.5);'>"
            f"<iframe width='100%' height='240' "
            f"src='https://www.youtube-nocookie.com/embed/{vid_id}?rel=0&modestbranding=1' "
            f"frameborder='0' "
            f"allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' "
            f"allowfullscreen style='display:block;'></iframe></div>"
        )

    # 3. Fallback button
    return (
        f"<div style='text-align:center;margin:8px 0 18px 0;'>"
        f"<a href='{yt_direct}' target='_blank' "
        f"style='display:inline-block;padding:12px 32px;background:#FF0000;"
        f"color:white;text-decoration:none;border-radius:25px;font-weight:bold;"
        f"font-size:1rem;box-shadow:0 4px 15px rgba(255,0,0,0.4);'>▶ Play on YouTube</a>"
        f"</div>"
    )

def apply_theme(mood):
    accent = MOOD_ACCENT.get(mood, "#1DB954")
    bg = MOOD_GRADIENTS.get(mood, MOOD_GRADIENTS["Relaxed"])
    st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; }}
    .song-box {{
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(12px);
        padding: 25px; border-radius: 16px;
        border-left: 6px solid {accent};
        color: white; text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        transition: transform 0.3s ease;
    }}
    .song-box:hover {{ transform: translateY(-5px); }}
    .title-text {{
        text-align: center; font-weight: 800;
        background: -webkit-linear-gradient(45deg, {accent}, #FFFFFF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-family: 'Helvetica Neue', sans-serif; padding-bottom: 10px;
    }}
    .badge-card {{
        display: inline-block; background: rgba(255,255,255,0.08);
        border: 1px solid {accent}55; border-radius: 12px;
        padding: 10px 16px; margin: 6px; text-align: center; min-width: 140px;
    }}
    .history-card {{
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 15px 20px; margin-bottom: 12px;
    }}
    .xp-bar-wrap {{
        background: rgba(255,255,255,0.1); border-radius: 20px;
        height: 12px; width: 100%; margin: 6px 0;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        height: 46px; background-color: transparent;
        border-radius: 8px 8px 0 0; padding: 8px 14px; font-size: 1rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════
defaults = {
    'logged_in': False, 'is_admin': False, 'username': None,
    'env': None, 'nlp': None, 'recommender': None, 'agent': None, 'chatbot': None,
    'search_engine': None,
    'last_genre': 'None', 'current_songs': [], 'playlist_queue': [],
    'current_state': None, 'current_action': None, 'feedback_given': False,
    'current_mood': 'Relaxed', 'current_language': 'Hindi',
    'new_badges': [], 'chat_history': [],
    'search_results': [], 'previous_search_query': '',
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.env is None:       st.session_state.env = MusicEnv()
if st.session_state.nlp is None:       st.session_state.nlp = NLPEngine()
if st.session_state.recommender is None: st.session_state.recommender = Recommender()
if st.session_state.chatbot is None:   st.session_state.chatbot = MusicChatbot()
if st.session_state.search_engine is None: st.session_state.search_engine = SongSearchEngine()

apply_theme(st.session_state.get('current_mood', 'Relaxed') or 'Relaxed')

# ═══════════════════════════════════════════════════════
#  LOGIN PAGE
# ═══════════════════════════════════════════════════════
if not st.session_state.logged_in:
    # Full-page login styling
    st.markdown("""
    <style>
    .login-hero {
        text-align: center;
        padding: 40px 20px 10px 20px;
    }
    .login-tagline {
        text-align: center;
        font-size: 1.15rem;
        opacity: 0.7;
        margin-bottom: 8px;
    }
    .login-features {
        display: flex;
        justify-content: center;
        gap: 24px;
        flex-wrap: wrap;
        margin: 18px 0 30px 0;
    }
    .login-feat-chip {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-hero'>", unsafe_allow_html=True)
    st.markdown("<h1 class='title-text'>🎵 PLM Devs Music AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='login-tagline'>Your personal AI that learns your music taste and gets smarter every day.</p>",
                unsafe_allow_html=True)
    st.markdown("""
    <div class='login-features'>
        <span class='login-feat-chip'>🧠 Q-Learning AI</span>
        <span class='login-feat-chip'>🎭 Mood Detection</span>
        <span class='login-feat-chip'>🌍 5 Languages</span>
        <span class='login-feat-chip'>🏆 Gamification</span>
        <span class='login-feat-chip'>🌐 Community</span>
        <span class='login-feat-chip'>📊 Weekly Reports</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        login_tab, signup_tab = st.tabs(["🔑 Login", "📝 Sign Up"])
        with login_tab:
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
                    ok, msg = login_user(l_user.strip(), l_pass)
                    if ok:
                        st.session_state.username = l_user.strip()
                        st.session_state.agent = QLearningAgent(
                            actions=st.session_state.env.get_actions(),
                            username=st.session_state.username)
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error(msg)
            st.markdown("<p style='text-align:center;opacity:0.5;font-size:0.8rem;margin-top:12px;'>"
                        "New here? Switch to Sign Up tab 👆</p>", unsafe_allow_html=True)

        with signup_tab:
            st.markdown("<br>", unsafe_allow_html=True)
            s_user  = st.text_input("Choose Username", key="s_user", placeholder="e.g. pranav123")
            s_pass  = st.text_input("Choose Password", type="password", key="s_pass", placeholder="Min 4 characters")
            s_pass2 = st.text_input("Confirm Password", type="password", key="s_pass2", placeholder="Repeat password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create My AI Brain 🧠", use_container_width=True, type="primary"):
                if not s_user.strip():
                    st.error("Username cannot be empty.")
                elif s_pass != s_pass2:
                    st.error("Passwords do not match.")
                elif len(s_pass) < 4:
                    st.error("Password must be at least 4 characters.")
                else:
                    ok, msg = register_user(s_user.strip(), s_pass)
                    st.success(f"✅ {msg} Now login!") if ok else st.error(msg)
            st.markdown("<p style='text-align:center;opacity:0.5;font-size:0.8rem;margin-top:12px;'>"
                        "Each account gets its own personalized AI 🎵</p>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;margin-top:40px;'>
        <p style='opacity:0.4;font-size:0.75rem;margin:0;'>Built with ❤️ by PLM Devs</p>
        <p style='opacity:0.6;font-size:0.85rem;margin:4px 0 0 0;'>
            🚀 Designed &amp; Developed by <b>Pranav Chakravorty</b>
        </p>
        <p style='opacity:0.35;font-size:0.72rem;margin:2px 0 0 0;font-style:italic;'>
            "Turning mood into music, one algorithm at a time."
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════
if st.session_state.is_admin:
    st.markdown("<h1 class='title-text'>🛡️ PLM Devs God Mode</h1>", unsafe_allow_html=True)
    if st.button("🚪 Exit God Mode", type="primary"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()
    st.write("---")

    st.header("1. Global AI Matrices")
    files = glob.glob("q_table_*.json")
    if not files:
        st.info("No user data recorded yet.")
    else:
        st.write(f"Total Active User Brains: **{len(files)}**")
        for file in files:
            user_n = file.replace("q_table_", "").replace(".json", "")
            with st.expander(f"View Q-Table: {user_n}"):
                ag = QLearningAgent(actions=st.session_state.env.get_actions(), username=user_n)
                st.json(ag.q_table)
                if st.button(f"🗑️ Delete {user_n}", key=f"del_{user_n}"):
                    delete_user(user_n)
                    st.success("Deleted!")
                    st.rerun()

    st.write("---")
    st.header("2. Catalog Expansion")
    with st.form("add_song_form"):
        new_song  = st.text_input("Song Name")
        new_mood  = st.selectbox("Mood", st.session_state.env.moods)
        new_genre = st.selectbox("Genre", st.session_state.env.get_actions())
        new_energy = st.selectbox("Energy", ["Low", "Medium", "High"])
        new_lang  = st.selectbox("Language", ["Hindi", "English", "Punjabi", "Tamil", "Telugu"])
        new_url   = st.text_input("YouTube URL (Optional)")
        if st.form_submit_button("Add to Universe") and new_song.strip():
            with open("data/songs.csv", "a", encoding="utf-8") as f:
                f.write(f"\n{new_song},{new_mood},{new_genre},{new_energy},{new_lang},{new_url}")
            st.success("Injected!")
            # Reload both recommender and chatbot so new song is available immediately
            st.session_state.recommender = Recommender()
            st.session_state.chatbot = MusicChatbot()

    st.write("---")
    st.header("3. All Users History")
    for hf in glob.glob("history_*.json"):
        uname = hf.replace("history_", "").replace(".json", "")
        with st.expander(f"History: {uname}"):
            with open(hf) as fp: data = json.load(fp)
            st.write(f"Sessions: {len(data)}")
            for entry in reversed(data[-10:]):
                st.markdown(f"**{entry['timestamp']}** — `{entry['mood']}` | `{entry['genre']}` | `{entry['feedback']}`")
    st.stop()

# ═══════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    stats = load_stats(st.session_state.username) if st.session_state.username else {}
    xp = stats.get("xp", 0)
    level = get_level(xp)
    streak = stats.get("streak", 0)

    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"**{level}** &nbsp; | &nbsp; ⚡ {xp} XP &nbsp; | &nbsp; 🔥 {streak} day streak")
    st.divider()

    st.markdown("### 🗂️ Session Queue")
    if not st.session_state.playlist_queue:
        st.caption("Queue is empty. Like a song to add it!")
    else:
        for item in st.session_state.playlist_queue[::-1][:8]:
            st.markdown(f"- 🎵 {item}")
        if st.button("🗑️ Clear Queue", use_container_width=True, key="clear_queue"):
            st.session_state.playlist_queue = []
            st.rerun()

    st.divider()
    favs = load_favourites(st.session_state.username) if st.session_state.username else []
    st.markdown(f"### ❤️ Favourites ({len(favs)})")
    if favs:
        for fav in favs[-5:][::-1]:
            st.caption(f"🎵 {fav['song']}")
    else:
        st.caption("No favourites yet.")

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ═══════════════════════════════════════════════════════
#  BADGE POPUP
# ═══════════════════════════════════════════════════════
if st.session_state.new_badges:
    for badge in st.session_state.new_badges:
        st.toast(f"🏅 New Badge Unlocked: {badge}", icon="🎉")
    st.session_state.new_badges = []

# ═══════════════════════════════════════════════════════
#  MAIN HEADER
# ═══════════════════════════════════════════════════════
st.markdown("<h1 class='title-text'>🎵 Mood-Based AI Music Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;font-size:1.1rem;opacity:0.7;'>By PLM Devs 🚀</p>", unsafe_allow_html=True)

(tab_rec, tab_match, tab_social, tab_analytics,
 tab_history, tab_journal, tab_profile, tab_chat, tab_report, tab_search) = st.tabs([
    "🎧 Recommender", "🤝 Taste Match", "🌐 Community",
    "📈 Analytics", "📜 History", "📓 Mood Journal", "👤 Profile",
    "🤖 AI Chatbot", "📊 Weekly Report", "🔍 Search Songs"
])

# ═══════════════════════════════════════════════════════
#  TAB: RECOMMENDER CORE
# ═══════════════════════════════════════════════════════
with tab_rec:
    st.write("---")
    ui_col1, ui_col2 = st.columns([2, 1])

    with ui_col1:
        input_mode = st.radio("Express your mood:",
                              ["📝 Text/Sentence", "🎤 Voice Audio", "⬇️ Select Dropdown"],
                              horizontal=True)
        detected_mood = st.session_state.current_mood

        if input_mode == "⬇️ Select Dropdown":
            detected_mood = st.selectbox("Select Mood:", st.session_state.env.moods)

        elif input_mode == "📝 Text/Sentence":
            user_text = st.text_area("Tell the AI how your day is going...",
                                     placeholder="E.g., I had an amazing day but now I just want to chill.")
            if user_text:
                detected_mood = st.session_state.nlp.detect_mood_from_text(user_text)
                st.info(f"🧠 AI Detected Mood: **{detected_mood}**")

        elif input_mode == "🎤 Voice Audio":
            audio_val = st.audio_input("Record a voice note")
            if audio_val is not None:
                with st.spinner("Transcribing..."):
                    try:
                        text = st.session_state.nlp.transcribe_audio(audio_val)
                    except Exception:
                        text = ""
                if text:
                    st.success(f"You said: '{text}'")
                    detected_mood = st.session_state.nlp.detect_mood_from_text(text)
                    st.info(f"🧠 AI Detected Mood: **{detected_mood}**")
                else:
                    st.warning("Could not transcribe (needs internet). Defaulting to Focus.")
                    detected_mood = "Focus"

    with ui_col2:
        # Auto time detection
        hour = datetime.datetime.now().hour
        auto_time = ("Morning" if 5 <= hour < 12 else
                     "Afternoon" if 12 <= hour < 17 else
                     "Evening" if 17 <= hour < 21 else "Night")

        if 'selected_time' not in st.session_state:
            st.session_state.selected_time = auto_time

        time_idx = st.session_state.env.times_of_day.index(st.session_state.selected_time) \
                   if st.session_state.selected_time in st.session_state.env.times_of_day else 0

        time_of_day = st.selectbox("Time of Day", st.session_state.env.times_of_day, index=time_idx)
        st.session_state.selected_time = time_of_day

        language = st.selectbox("Language", ["Hindi", "English", "Punjabi", "Tamil", "Telugu"])

        # One-click auto apply button
        if st.button(f"⚡ Use Current Time ({auto_time})", use_container_width=True):
            st.session_state.selected_time = auto_time
            st.rerun()

    # Update theme live
    if detected_mood != st.session_state.current_mood:
        st.session_state.current_mood = detected_mood
        apply_theme(detected_mood)

    st.session_state.current_language = language

    # Mood color badge
    mood_emoji = {"Happy": "😄", "Sad": "😢", "Focus": "🎯", "Relaxed": "😌"}
    accent = MOOD_ACCENT.get(detected_mood, "#1DB954")
    st.markdown(
        f"<div style='text-align:center;margin:10px 0;'>"
        f"<span style='background:{accent}22;border:1px solid {accent};border-radius:20px;"
        f"padding:6px 20px;font-size:1.1rem;'>{mood_emoji.get(detected_mood,'')} {detected_mood} Mode</span></div>",
        unsafe_allow_html=True)

    if detected_mood in ['Focus', 'Relaxed']:
        render_pomodoro()

    st.write("")
    rec_col, surprise_col = st.columns([3, 1])
    with rec_col:
        get_rec = st.button("🎧 Get AI Recommendations", use_container_width=True, type="primary")
    with surprise_col:
        surprise = st.button("🎲 Surprise Me!", use_container_width=True)

    if surprise:
        import random as _random
        detected_mood = _random.choice(st.session_state.env.moods)
        language = _random.choice(["Hindi", "English", "Punjabi", "Tamil", "Telugu"])
        action = _random.choice(st.session_state.env.get_actions())
        st.session_state.feedback_given = False
        state = st.session_state.env.get_state(detected_mood, time_of_day, st.session_state.last_genre)
        st.session_state.current_state = state
        st.session_state.current_action = action
        songs = st.session_state.recommender.recommend_songs(detected_mood, action, language, n=3)
        st.session_state.current_songs = songs
        st.session_state.current_mood = detected_mood
        st.toast(f"🎲 Surprise! {detected_mood} + {action} + {language}")
        st.rerun()

    if get_rec:
        st.session_state.feedback_given = False
        state = st.session_state.env.get_state(detected_mood, time_of_day, st.session_state.last_genre)
        st.session_state.current_state = state
        action = st.session_state.agent.choose_action(state)
        st.session_state.current_action = action
        songs = st.session_state.recommender.recommend_songs(detected_mood, action, language, n=3)
        st.session_state.current_songs = songs
        st.rerun()

    if st.session_state.current_songs:
        st.divider()
        quote = st.session_state.nlp.generate_quote(detected_mood)
        st.markdown(
            f"<div style='text-align:center;border-radius:8px;border:1px solid {accent}44;"
            f"padding:15px;margin-bottom:20px;background:rgba(0,0,0,0.4);backdrop-filter:blur(5px);'>"
            f"<p style='font-style:italic;color:{accent};font-size:1.2rem;margin:0;'>{quote}</p></div>",
            unsafe_allow_html=True)

        c_state = st.session_state.current_state
        st.markdown(f"### 🎶 Recommended for: {c_state.replace('_', ' | ') if c_state else ''}")

        favs_list = [f["song"] for f in load_favourites(st.session_state.username)]

        for i, song in enumerate(st.session_state.current_songs):
            spotify_url = f"https://open.spotify.com/search/{song['Song'].replace(' ', '%20')}"
            yt_url = f"https://www.youtube.com/results?search_query={song['Song'].replace(' ', '+')}"
            is_fav = song['Song'] in favs_list
            fav_icon = "❤️" if is_fav else "🤍"
            song_url = song.get('URL', '')

            st.markdown(f"""
            <div class="song-box">
                <h2>{song['Song']}</h2>
                <p style='opacity:0.8;'>🎭 {song['Mood']} &nbsp;|&nbsp; 🎸 {song['Genre']} &nbsp;|&nbsp; 🌐 {song.get('Language','English')}</p>
                <a href="{spotify_url}" target="_blank"
                   style="display:inline-block;margin:8px 4px;padding:8px 16px;background:#1DB954;
                   color:white;text-decoration:none;border-radius:20px;font-weight:bold;">🎧 Spotify</a>
                <a href="{yt_url}" target="_blank"
                   style="display:inline-block;margin:8px 4px;padding:8px 16px;background:#FF0000;
                   color:white;text-decoration:none;border-radius:20px;font-weight:bold;">▶ Open YouTube</a>
            </div>
            """, unsafe_allow_html=True)

            # YouTube nocookie embed player
            st.markdown(
                get_yt_embed_html(song.get('URL', ''), song['Song'], song.get('Language', 'Hindi'), song.get('SpotifyURL', '')),
                unsafe_allow_html=True
            )

            fav_col, queue_col, _ = st.columns([1, 1, 3])
            with fav_col:
                if st.button(f"{fav_icon} Favourite", key=f"fav_{i}_{song['Song']}"):
                    action_done = toggle_favourite(
                        st.session_state.username, song['Song'],
                        song['Mood'], song['Genre'])
                    st.toast(f"{'Added to' if action_done == 'added' else 'Removed from'} favourites!")
                    st.rerun()
            with queue_col:
                in_queue = song['Song'] in st.session_state.playlist_queue
                q_icon = "✅ In Queue" if in_queue else "➕ Add to Queue"
                if st.button(q_icon, key=f"queue_{i}_{song['Song']}", disabled=in_queue):
                    st.session_state.playlist_queue.append(song['Song'])
                    st.toast(f"➕ {song['Song']} added to queue!")
                    st.rerun()

            st.write("")

        with st.expander("🤖 Why did the AI choose this? (xAI)"):
            c_action = st.session_state.current_action
            q_val = st.session_state.agent.get_q_value(c_state, c_action)
            st.write(f"Chose **{c_action}** for state `{c_state}` — Priority Score: **{q_val:.2f}**")
            st.caption("Likes (+10), Listen (+2), Skip (-5) update this score.")

        # Share playlist button
        share_col, _ = st.columns([2, 3])
        with share_col:
            share_note = st.text_input("Add a note (optional)", placeholder="Feeling great today!", key="share_note")
            if st.button("🌐 Share this Playlist to Community", use_container_width=True):
                share_playlist(
                    st.session_state.username,
                    [s['Song'] for s in st.session_state.current_songs],
                    detected_mood, share_note)
                st.success("Shared to Community tab!")

        st.markdown("### 👇 Give Feedback")

        if not st.session_state.feedback_given:
            f1, f2, f3 = st.columns(3)
            feedback = None
            reward = None
            with f1:
                if st.button("👍 Like (+10)", use_container_width=True): feedback, reward = "like", 10
            with f2:
                if st.button("🎧 Listen (+2)", use_container_width=True): feedback, reward = "listen", 2
            with f3:
                if st.button("⏭️ Skip (-5)", use_container_width=True): feedback, reward = "skip", -5

            if feedback is not None:
                state = st.session_state.current_state
                action = st.session_state.current_action
                next_state = st.session_state.env.get_state(detected_mood, time_of_day, action)
                st.session_state.agent.learn(state, action, reward, next_state)
                st.session_state.last_genre = action
                st.session_state.feedback_given = True

                save_history_entry(st.session_state.username,
                                   st.session_state.current_songs,
                                   detected_mood, action, feedback)

                # Update gamification
                _, new_badges = update_stats(st.session_state.username, detected_mood, action, feedback)
                if new_badges:
                    st.session_state.new_badges = new_badges

                if reward > 0:
                    for s in st.session_state.current_songs:
                        st.session_state.playlist_queue.append(s['Song'])
                    st.success(f"✅ {feedback.capitalize()} recorded! Songs added to queue.")
                else:
                    st.success(f"✅ {feedback.capitalize()} recorded.")

                time.sleep(1)
                st.rerun()
        else:
            st.success("Feedback recorded. Get new recommendations!")

# ═══════════════════════════════════════════════════════
#  TAB: TASTE MATCH
# ═══════════════════════════════════════════════════════
with tab_match:
    st.header("🤝 AI Friend Match")
    st.write("Compare your musical DNA with another user's Q-Table.")
    files = glob.glob("q_table_*.json")
    other_users = [f.replace("q_table_", "").replace(".json", "")
                   for f in files if "admin" not in f and
                   f.replace("q_table_", "").replace(".json", "") != st.session_state.username]

    if not other_users:
        st.info("No other users found. Ask a friend to sign up!")
    else:
        friend_choice = st.selectbox("Select a friend:", other_users)
        if st.button("Calculate Match %", type="primary"):
            friend_agent = QLearningAgent(actions=st.session_state.env.get_actions(), username=friend_choice)
            my_table = st.session_state.agent.q_table
            f_table = friend_agent.q_table
            common = set(my_table.keys()) & set(f_table.keys())
            if not common:
                st.warning("Not enough overlapping sessions yet.")
            else:
                matches = sum(1 for s in common
                              if max(my_table[s], key=my_table[s].get) ==
                                 max(f_table[s], key=f_table[s].get))
                pct = int((matches / len(common)) * 100)
                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pct,
                    title={"text": f"You & {friend_choice}"},
                    gauge={"axis": {"range": [0, 100]},
                           "bar": {"color": "#1DB954"},
                           "steps": [{"range": [0, 40], "color": "#2d2d2d"},
                                     {"range": [40, 70], "color": "#1a3a1a"},
                                     {"range": [70, 100], "color": "#0d4d0d"}]}))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=300)
                st.plotly_chart(fig, use_container_width=True)
                if pct > 70:
                    st.success(f"🎉 {pct}% Match — You two are musical soulmates!")
                elif pct > 40:
                    st.info(f"🎵 {pct}% Match — Good vibes, similar taste!")
                else:
                    st.warning(f"🎭 {pct}% Match — Opposites attract!")

# ═══════════════════════════════════════════════════════
#  TAB: COMMUNITY
# ═══════════════════════════════════════════════════════
with tab_social:
    st.header("🌐 Community")
    
    # Tabs within social
    subtab_leaderboard, subtab_friends, subtab_playlists = st.tabs(["🏆 Leaderboard", "👥 Friends", "🎵 Playlists"])
    
    # ──── LEADERBOARD ────
    with subtab_leaderboard:
        st.subheader("🏆 Global Leaderboard")
        st.write("Top players by XP points!")
        
        leaderboard = get_leaderboard_top(limit=50)
        
        if not leaderboard:
            st.info("No leaderboard data yet. Be the first to earn XP!")
        else:
            # Display current user's rank
            my_rank, my_xp = get_user_rank(st.session_state.username)
            if my_rank:
                rank_color = {1: "🥇", 2: "🥈", 3: "🥉"}.get(my_rank, f"#{my_rank}")
                st.success(f"{rank_color} Your Rank: **#{my_rank}** with **{my_xp} XP**")
            
            st.divider()
            
            # Leaderboard table
            top_n = 20
            lb_data = []
            for i, user in enumerate(leaderboard[:top_n], 1):
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
                lb_data.append({
                    "Rank": medal,
                    "User": user["username"],
                    "Level": user["level"],
                    "XP": user["xp"],
                })
            
            df_lb = pd.DataFrame(lb_data)
            st.dataframe(df_lb, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Players", len(leaderboard))
            with col2:
                top_xp = leaderboard[0]["xp"] if leaderboard else 0
                st.metric("Top Score", f"{top_xp} XP")
    
    # ──── FRIENDS ────
    with subtab_friends:
        st.subheader("👥 Friends")
        
        friends_data = load_friends(st.session_state.username)
        following = friends_data.get("following", [])
        followers = friends_data.get("followers", [])
        
        col_follow, col_followers = st.columns(2)
        with col_follow:
            st.metric("Following", len(following))
        with col_followers:
            st.metric("Followers", len(followers))
        
        st.divider()
        
        # Find and follow users
        st.write("### 🔍 Find & Follow Users")
        available_users = []
        try:
            all_users = json.load(open("users.json"))
            available_users = [u for u in all_users.keys() if u != st.session_state.username and u not in following]
        except:
            pass
        
        if available_users:
            user_to_follow = st.selectbox("Select user to follow", [""] + available_users)
            if user_to_follow and st.button(f"Follow @{user_to_follow} →", use_container_width=True):
                success, msg = follow_user(st.session_state.username, user_to_follow)
                if success:
                    st.success(msg)
                    st.rerun()
        else:
            st.caption("No users available to follow or already following everyone!")
        
        st.divider()
        
        # Show following list
        if following:
            st.write("### 👤 Following")
            for user in following:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"@{user}")
                with col2:
                    if st.button("💔 Unfollow", key=f"unf_{user}", use_container_width=True):
                        unfollow_user(st.session_state.username, user)
                        st.rerun()
        
        st.divider()
        
        # Show followers list
        if followers:
            st.write("### 👥 Followers")
            st.caption(f"You have **{len(followers)}** followers!")
            for follower in followers[:10]:
                st.caption(f"@{follower} follows you")
    
    # ──── PLAYLISTS ────
    with subtab_playlists:
        st.subheader("🎵 Community Playlists")
        st.write("See what others are listening to. Like their playlists!")

        playlists = load_shared_playlists()
        if not playlists:
            st.info("No shared playlists yet. Be the first to share from the Recommender tab!")
        else:
            mood_filter = st.selectbox("Filter by Mood", ["All"] + st.session_state.env.moods, key="comm_filter")
            shown = [p for p in reversed(playlists) if mood_filter == "All" or p["mood"] == mood_filter]

            for p in shown[:20]:
                with st.container():
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"""
                        <div class="history-card">
                            <b>👤 {p['username']}</b> &nbsp; <span style='opacity:0.6;font-size:0.85rem;'>{p['timestamp']}</span><br>
                            🎭 <b>{p['mood']}</b> &nbsp; 🎵 {', '.join(p['songs'])}<br>
                            {f"<i style='opacity:0.7;'>💬 {p['note']}</i>" if p.get('note') else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        already_liked = st.session_state.username in p.get("liked_by", [])
                        btn_label = f"❤️ {p['likes']}" if already_liked else f"🤍 {p['likes']}"
                        if st.button(btn_label, key=f"like_p_{p['id']}", disabled=already_liked):
                            like_shared_playlist(p["id"], st.session_state.username)
                            st.rerun()

# ═══════════════════════════════════════════════════════
#  TAB: ANALYTICS
# ═══════════════════════════════════════════════════════
with tab_analytics:
    render_dashboard(st.session_state.agent)

    # Mood trend chart from history
    history = load_history(st.session_state.username)
    if len(history) >= 3:
        st.divider()
        st.subheader("📊 Your Mood Trend Over Time")
        df_h = pd.DataFrame(history)
        df_h["date"] = pd.to_datetime(df_h["timestamp"]).dt.date
        mood_trend = df_h.groupby(["date", "mood"]).size().reset_index(name="count")
        fig2 = px.line(mood_trend, x="date", y="count", color="mood",
                       color_discrete_map={"Happy": "#FFD700", "Sad": "#6495ED",
                                           "Focus": "#FF8C00", "Relaxed": "#1DB954"},
                       title="Mood Frequency Over Time")
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="white")
        st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════
#  TAB: HISTORY
# ═══════════════════════════════════════════════════════
with tab_history:
    st.header("📜 Your Listening History")
    history = load_history(st.session_state.username)
    if not history:
        st.info("No history yet. Start getting recommendations!")
    else:
        df_hist = pd.DataFrame(history)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Sessions", len(history))
        c2.metric("Favourite Mood", df_hist['mood'].mode()[0])
        c3.metric("Favourite Genre", df_hist['genre'].mode()[0])
        c4.metric("Likes", len(df_hist[df_hist['feedback'] == 'like']))

        st.divider()

        # Export
        favs_data = load_favourites(st.session_state.username)
        if favs_data:
            export_text = export_playlist_text(st.session_state.username, favs_data, "Favourites")
            st.download_button("⬇️ Export Favourites as .txt", export_text,
                               file_name=f"{st.session_state.username}_playlist.txt")

        st.subheader("Recent Sessions")
        for entry in reversed(history[-25:]):
            fc = {"like": "🟢", "listen": "🔵", "skip": "🔴"}.get(entry['feedback'], "⚪")
            st.markdown(f"""
            <div class="history-card">
                <b>{entry['timestamp']}</b> &nbsp; {fc} <b>{entry['feedback'].capitalize()}</b><br>
                🎭 {entry['mood']} &nbsp; 🎸 {entry['genre']}<br>
                🎵 {', '.join(entry['songs'])}
            </div>""", unsafe_allow_html=True)

        if st.button("🗑️ Clear History", type="secondary"):
            hf = f"history_{st.session_state.username}.json"
            if os.path.exists(hf): os.remove(hf)
            st.success("Cleared.")
            st.rerun()

# ═══════════════════════════════════════════════════════
#  TAB: MOOD JOURNAL
# ═══════════════════════════════════════════════════════
with tab_journal:
    st.header("📓 Mood Journal")
    st.write("Write how you're feeling today. Track your emotional journey over time.")

    with st.form("journal_form"):
        j_mood = st.selectbox("Today's Mood", st.session_state.env.moods)
        j_note = st.text_area("Write your thoughts...", placeholder="Today was a tough day but music helped...")
        if st.form_submit_button("Save Entry", use_container_width=True):
            if j_note.strip():
                save_journal_entry(st.session_state.username, j_mood, j_note.strip())
                st.success("Journal entry saved! 📝")
            else:
                st.warning("Write something first.")

    st.divider()
    journal = load_journal(st.session_state.username)
    if not journal:
        st.info("No journal entries yet.")
    else:
        st.subheader(f"Your Entries ({len(journal)})")

        # Mood distribution pie
        df_j = pd.DataFrame(journal)
        mood_counts = df_j['mood'].value_counts().reset_index()
        mood_counts.columns = ['mood', 'count']
        fig_pie = px.pie(mood_counts, names='mood', values='count',
                         color='mood',
                         color_discrete_map={"Happy": "#FFD700", "Sad": "#6495ED",
                                             "Focus": "#FF8C00", "Relaxed": "#1DB954"},
                         title="Your Mood Distribution")
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_pie, use_container_width=True)

        for entry in reversed(journal[-15:]):
            mood_color = {"Happy": "#FFD700", "Sad": "#6495ED",
                          "Focus": "#FF8C00", "Relaxed": "#1DB954"}.get(entry['mood'], "#fff")
            st.markdown(f"""
            <div class="history-card" style="border-left: 4px solid {mood_color};">
                <span style='opacity:0.6;font-size:0.85rem;'>{entry['date']} {entry['time']}</span>
                &nbsp; <b style='color:{mood_color};'>{entry['mood']}</b><br>
                <p style='margin:6px 0 0 0;'>{entry['note']}</p>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  TAB: PROFILE / GAMIFICATION
# ═══════════════════════════════════════════════════════
with tab_profile:
    stats = load_stats(st.session_state.username)
    xp = stats.get("xp", 0)
    level = get_level(xp)

    st.header(f"👤 {st.session_state.username}")

    # Level & XP
    level_thresholds = [0, 50, 150, 300, 600, 1000]
    next_thresh = next((t for t in level_thresholds if t > xp), 1000)
    prev_thresh = max((t for t in level_thresholds if t <= xp), default=0)
    xp_progress = (xp - prev_thresh) / max(next_thresh - prev_thresh, 1)

    st.markdown(f"### {level}")
    st.progress(min(xp_progress, 1.0))
    st.caption(f"⚡ {xp} XP — {next_thresh - xp} XP to next level")

    st.divider()

    # Stats row
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("🔥 Streak", f"{stats.get('streak', 0)} days")
    s2.metric("🎵 Sessions", stats.get("total_sessions", 0))
    s3.metric("👍 Likes", stats.get("total_likes", 0))
    s4.metric("⏭️ Skips", stats.get("total_skips", 0))

    st.divider()

    # Badges
    st.subheader("🏅 Badges")
    earned = stats.get("earned_badges", [])
    badge_html = ""
    for badge, info in BADGES.items():
        if badge in earned:
            badge_html += f"<div class='badge-card'><div style='font-size:1.5rem;'>{badge.split()[0]}</div><div style='font-size:0.8rem;font-weight:bold;'>{' '.join(badge.split()[1:])}</div><div style='font-size:0.7rem;opacity:0.7;'>{info['desc']}</div></div>"
        else:
            badge_html += f"<div class='badge-card' style='opacity:0.3;filter:grayscale(1);'><div style='font-size:1.5rem;'>🔒</div><div style='font-size:0.8rem;'>{' '.join(badge.split()[1:])}</div><div style='font-size:0.7rem;opacity:0.7;'>{info['desc']}</div></div>"
    st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:4px;'>{badge_html}</div>", unsafe_allow_html=True)

    st.divider()

    # Moods & Genres tried
    mc1, mc2 = st.columns(2)
    with mc1:
        st.subheader("🎭 Moods Explored")
        for m in st.session_state.env.moods:
            icon = "✅" if m in stats.get("moods_tried", []) else "⬜"
            st.write(f"{icon} {m}")
    with mc2:
        st.subheader("🎸 Genres Explored")
        for g in st.session_state.env.get_actions():
            icon = "✅" if g in stats.get("genres_tried", []) else "⬜"
            st.write(f"{icon} {g}")

    st.divider()

    # Change password
    with st.expander("🔑 Change Password"):
        old_p = st.text_input("Current Password", type="password", key="chg_old")
        new_p = st.text_input("New Password", type="password", key="chg_new")
        new_p2 = st.text_input("Confirm New Password", type="password", key="chg_new2")
        if st.button("Update Password"):
            ok, _ = login_user(st.session_state.username, old_p)
            if not ok:
                st.error("Current password is wrong.")
            elif new_p != new_p2:
                st.error("Passwords do not match.")
            elif len(new_p) < 4:
                st.error("Too short.")
            else:
                USERS_FILE = "users.json"
                with open(USERS_FILE, 'r') as f: users = json.load(f)
                users[st.session_state.username]["password"] = hashlib.sha256(new_p.encode()).hexdigest()
                with open(USERS_FILE, 'w') as f: json.dump(users, f)
                st.success("Password updated!")

# ═══════════════════════════════════════════════════════
#  TAB: AI CHATBOT
# ═══════════════════════════════════════════════════════
with tab_chat:
    st.header("🤖 AI Music Chatbot")
    st.write("Baat karo AI se — koi bhi song request karo natural language mein!")

    # Streak reminder notification (browser)
    stats_for_notif = load_stats(st.session_state.username)
    last_active = stats_for_notif.get("last_active_date")
    today_str = datetime.date.today().isoformat()
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    show_reminder = last_active and last_active < yesterday_str

    if show_reminder:
        st.warning(
            f"⚠️ **Streak Alert!** Tumhari 🔥 {stats_for_notif.get('streak', 0)}-day streak toot sakti hai! "
            f"Aaj koi recommendation lo aur streak bachao!"
        )
        # Browser notification via JS
        st.markdown("""
        <script>
        if (Notification.permission === "granted") {
            new Notification("🎵 PLM Music AI", {
                body: "Aaj music nahi suna? Streak toot jayegi! App kholo 🔥",
                icon: "https://cdn-icons-png.flaticon.com/512/727/727245.png"
            });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(p => {
                if (p === "granted") {
                    new Notification("🎵 PLM Music AI", {
                        body: "Notifications on! Streak reminders milenge 🔥"
                    });
                }
            });
        }
        </script>
        """, unsafe_allow_html=True)

    # Enable notifications button
    st.markdown("""
    <script>
    function enableNotif() {
        Notification.requestPermission().then(p => {
            if (p === "granted") alert("✅ Notifications enabled! Streak reminders milenge.");
            else alert("❌ Notifications blocked. Browser settings se allow karo.");
        });
    }
    </script>
    <button onclick="enableNotif()"
        style="background:#1DB954;color:white;border:none;padding:8px 18px;
        border-radius:20px;cursor:pointer;font-size:0.9rem;margin-bottom:16px;">
        🔔 Enable Streak Reminders
    </button>
    """, unsafe_allow_html=True)

    st.divider()

    # Chat UI
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(
                    f"<div style='text-align:right;margin:8px 0;'>"
                    f"<span style='background:#1DB954;color:black;padding:8px 14px;"
                    f"border-radius:18px 18px 4px 18px;display:inline-block;max-width:80%;'>"
                    f"👤 {content}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div style='text-align:left;margin:8px 0;'>"
                    f"<span style='background:rgba(255,255,255,0.1);color:white;padding:8px 14px;"
                    f"border-radius:18px 18px 18px 4px;display:inline-block;max-width:80%;'>"
                    f"🤖 {content}</span></div>", unsafe_allow_html=True)
            # Show song cards if any
            if msg.get("songs"):
                for song in msg["songs"]:
                    sp = f"https://open.spotify.com/search/{song['Song'].replace(' ', '%20')}"
                    yt = f"https://www.youtube.com/results?search_query={song['Song'].replace(' ', '+')}"
                    st.markdown(f"""
                    <div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.15);
                    border-radius:12px;padding:12px 16px;margin:4px 0 4px 20px;'>
                        <b>🎵 {song['Song']}</b> &nbsp;
                        <span style='opacity:0.7;font-size:0.85rem;'>{song['Mood']} · {song['Genre']} · {song.get('Language','')}</span><br>
                        <a href="{sp}" target="_blank" style="color:#1DB954;margin-right:12px;">🎧 Spotify</a>
                        <a href="{yt}" target="_blank" style="color:#FF4444;">▶ YouTube</a>
                    </div>""", unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        user_msg = c1.text_input("", placeholder="e.g. 'sad hindi songs do' or 'party punjabi' or 'surprise me'",
                                  label_visibility="collapsed")
        sent = c2.form_submit_button("Send 📤", use_container_width=True)

    if sent and user_msg.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_msg, "songs": []})
        response = st.session_state.chatbot.respond(user_msg)
        st.session_state.chat_history.append({
            "role": "bot",
            "content": response["text"],
            "songs": response["songs"]
        })
        st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

# ═══════════════════════════════════════════════════════
#  TAB: WEEKLY REPORT
# ═══════════════════════════════════════════════════════
with tab_report:
    st.header("📊 Weekly Music Report")
    st.write("Teri is hafte ki poori music journey ek jagah.")

    report = generate_weekly_report(st.session_state.username)

    if not report:
        st.info("Abhi tak koi data nahi hai. Recommendations lo aur feedback do — report automatically ban jayegi!")
    else:
        st.markdown(f"### 📅 Period: {report['period']}")
        st.divider()

        # Top metrics
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("🎵 Sessions",  report['total_sessions'])
        m2.metric("👍 Likes",     report['likes'])
        m3.metric("🎧 Listens",   report['listens'])
        m4.metric("⏭️ Skips",     report['skips'])
        m5.metric("🔥 Streak",    f"{report['streak']} days")

        st.divider()

        # Insight card
        accent = MOOD_ACCENT.get(report['top_mood'], "#1DB954")
        st.markdown(
            f"<div style='background:{accent}22;border:1px solid {accent};border-radius:12px;"
            f"padding:16px 20px;margin-bottom:16px;'>"
            f"<h3 style='margin:0;color:{accent};'>💡 Weekly Insight</h3>"
            f"<p style='margin:8px 0 0 0;font-size:1.1rem;'>{report['insight']}</p>"
            f"<p style='margin:4px 0 0 0;opacity:0.7;'>Top Mood: <b>{report['top_mood']}</b> &nbsp;|&nbsp; "
            f"Top Genre: <b>{report['top_genre']}</b> &nbsp;|&nbsp; ⚡ XP Gained: <b>{report['xp_gained']}</b></p>"
            f"</div>", unsafe_allow_html=True)

        # Charts side by side
        ch1, ch2 = st.columns(2)
        with ch1:
            if report['mood_counts']:
                df_mood = pd.DataFrame(list(report['mood_counts'].items()), columns=['Mood', 'Count'])
                fig_m = px.bar(df_mood, x='Mood', y='Count', color='Mood',
                               color_discrete_map={"Happy": "#FFD700", "Sad": "#6495ED",
                                                   "Focus": "#FF8C00", "Relaxed": "#1DB954"},
                               title="Mood Breakdown")
                fig_m.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                    font_color="white", showlegend=False)
                st.plotly_chart(fig_m, use_container_width=True)

        with ch2:
            if report['genre_counts']:
                df_genre = pd.DataFrame(list(report['genre_counts'].items()), columns=['Genre', 'Count'])
                fig_g = px.pie(df_genre, names='Genre', values='Count', title="Genre Mix",
                               color_discrete_sequence=px.colors.qualitative.Set3)
                fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_g, use_container_width=True)

        # Daily activity bar
        if not report['daily_activity'].empty:
            fig_d = px.bar(report['daily_activity'], x='date', y='sessions',
                           title="Daily Activity This Week",
                           color_discrete_sequence=[accent])
            fig_d.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                font_color="white")
            st.plotly_chart(fig_d, use_container_width=True)

        # Top songs
        if report['top_songs']:
            st.subheader("🏆 Top Songs This Week")
            for i, (song, count) in enumerate(report['top_songs'], 1):
                sp = f"https://open.spotify.com/search/{song.replace(' ', '%20')}"
                st.markdown(
                    f"<div class='history-card'><b>#{i}</b> &nbsp; 🎵 {song} &nbsp;"
                    f"<span style='opacity:0.6;'>({count}x)</span> &nbsp;"
                    f"<a href='{sp}' target='_blank' style='color:#1DB954;'>🎧 Spotify</a></div>",
                    unsafe_allow_html=True)

        st.divider()
        # Download report
        report_text = export_report_text(st.session_state.username, report)
        st.download_button(
            "⬇️ Download Report as .txt",
            report_text,
            file_name=f"{st.session_state.username}_weekly_report.txt",
            mime="text/plain"
        )

# ═══════════════════════════════════════════════════════
#  TAB: SONG SEARCH
# ═══════════════════════════════════════════════════════
with tab_search:
    st.header("🔍 Search Songs")
    st.write("Directly search the entire database by name, mood, genre, or language.")

    # Load fresh data
    try:
        df_all = pd.read_csv("data/songs.csv")
    except Exception:
        df_all = pd.DataFrame()

    # ── Filters row ──
    f1, f2, f3, f4 = st.columns([3, 1, 1, 1])
    with f1:
        search_query = st.text_input("🔎 Search by song name",
                                     placeholder="e.g. Kesariya, Espresso, Naatu...",
                                     key="search_q")
    with f2:
        filter_mood = st.selectbox("Mood", ["All"] + st.session_state.env.moods, key="sf_mood")
    with f3:
        filter_genre = st.selectbox("Genre", ["All"] + st.session_state.env.get_actions(), key="sf_genre")
    with f4:
        filter_lang = st.selectbox("Language", ["All", "Hindi", "English", "Punjabi", "Tamil", "Telugu"], key="sf_lang")

    # ── Apply filters ──
    results = df_all.copy()
    if search_query.strip():
        results = results[results['Song'].str.contains(search_query.strip(), case=False, na=False)]
    if filter_mood != "All":
        results = results[results['Mood'] == filter_mood]
    if filter_genre != "All":
        results = results[results['Genre'] == filter_genre]
    if filter_lang != "All":
        results = results[results['Language'].str.lower() == filter_lang.lower()]

    st.caption(f"Showing {len(results)} of {len(df_all)} songs")
    st.divider()

    if results.empty:
        st.info("No songs found. Try different filters.")
    else:
        favs_list_s = [f["song"] for f in load_favourites(st.session_state.username)]
        for idx, row in results.iterrows():
            sp  = f"https://open.spotify.com/search/{str(row['Song']).replace(' ', '%20')}"
            yt  = f"https://www.youtube.com/results?search_query={str(row['Song']).replace(' ', '+')}"
            is_fav = row['Song'] in favs_list_s
            fav_icon = "❤️" if is_fav else "🤍"

            mood_color = {"Happy": "#FFD700", "Sad": "#6495ED",
                          "Focus": "#FF8C00", "Relaxed": "#1DB954"}.get(row.get('Mood', ''), "#1DB954")

            c_song, c_actions = st.columns([4, 1])
            with c_song:
                st.markdown(f"""
                <div class="history-card" style="border-left:4px solid {mood_color};">
                    <b style="font-size:1.05rem;">🎵 {row['Song']}</b><br>
                    <span style="opacity:0.7;font-size:0.85rem;">
                        🎭 {row.get('Mood','')} &nbsp;·&nbsp;
                        🎸 {row.get('Genre','')} &nbsp;·&nbsp;
                        🌐 {row.get('Language','')} &nbsp;·&nbsp;
                        ⚡ {row.get('Energy','')}
                    </span><br>
                    <a href="{sp}" target="_blank"
                       style="color:#1DB954;margin-right:14px;font-size:0.85rem;">🎧 Spotify</a>
                    <a href="{yt}" target="_blank"
                       style="color:#FF4444;font-size:0.85rem;">▶ YouTube</a>
                </div>""", unsafe_allow_html=True)
            with c_actions:
                if st.button(fav_icon, key=f"sfav_{idx}_{row['Song']}",
                             help="Add/Remove from Favourites"):
                    toggle_favourite(st.session_state.username,
                                     row['Song'], row.get('Mood',''), row.get('Genre',''))
                    st.rerun()
                in_queue_s = row['Song'] in st.session_state.playlist_queue
                if st.button("✅" if in_queue_s else "➕", key=f"sq_{idx}_{row['Song']}",
                             help="Add to Queue", disabled=in_queue_s):
                    st.session_state.playlist_queue.append(row['Song'])
                    st.toast(f"➕ {row['Song']} added to queue!")
                    st.rerun()
