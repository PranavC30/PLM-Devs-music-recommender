"""ui_components.py — All reusable HTML/CSS/JS UI components for PLM Devs Music AI."""
import streamlit as st

MOOD_ACCENT = {"Happy":"#FFD700","Sad":"#6495ED","Focus":"#FF8C00","Relaxed":"#1DB954"}
MOOD_GRADIENTS = {
    "Happy":   "linear-gradient(135deg,#1a1a2e 0%,#16213e 40%,#1a3a1a 100%)",
    "Sad":     "linear-gradient(135deg,#0d0d1a 0%,#1a1a3e 40%,#0d1a2e 100%)",
    "Focus":   "linear-gradient(135deg,#1a0d00 0%,#2e1a00 40%,#1a1a00 100%)",
    "Relaxed": "linear-gradient(135deg,#001a1a 0%,#001a2e 40%,#0d1a1a 100%)",
}
MOOD_EMOJI = {"Happy":"😄","Sad":"😢","Focus":"🎯","Relaxed":"😌"}

def inject_global_css(accent="#1DB954", bg=""):
    if not bg: bg = MOOD_GRADIENTS["Relaxed"]
    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html,body,.stApp{{font-family:'Inter',sans-serif!important;background:{bg}!important;color:#fff;}}
    #MainMenu,footer{{visibility:hidden;}}
    .stApp{{background-size:400% 400%!important;animation:bgShift 18s ease infinite!important;}}
    @keyframes bgShift{{0%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}100%{{background-position:0% 50%;}}}}
    ::-webkit-scrollbar{{width:6px;}} ::-webkit-scrollbar-track{{background:rgba(255,255,255,0.03);}}
    ::-webkit-scrollbar-thumb{{background:{accent}66;border-radius:3px;}}
    .stTextInput>div>div>input,.stTextArea>div>div>textarea,.stSelectbox>div>div>div{{
        background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.15)!important;
        border-radius:10px!important;color:white!important;}}
    .stButton>button{{border-radius:10px!important;font-weight:700!important;transition:transform 0.15s,box-shadow 0.15s!important;}}
    .stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(0,0,0,0.3)!important;}}
    .stButton>button[kind="primary"]{{background:linear-gradient(135deg,{accent},{accent}cc)!important;border:none!important;color:#000!important;box-shadow:0 4px 15px {accent}44!important;}}
    hr{{border-color:rgba(255,255,255,0.08)!important;}}
    .song-card{{position:relative;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);
        backdrop-filter:blur(20px);border-radius:20px;padding:28px 32px;margin-bottom:22px;
        border-left:5px solid {accent};box-shadow:0 8px 32px rgba(0,0,0,0.45);
        transition:transform 0.25s cubic-bezier(.4,2,.6,1),box-shadow 0.25s ease;overflow:hidden;}}
    .song-card:hover{{transform:translateY(-6px) scale(1.01);box-shadow:0 16px 48px rgba(0,0,0,0.6),0 0 32px {accent}22;}}
    .song-card h2{{margin:0 0 6px 0;font-size:1.35rem;font-weight:800;}}
    .song-card .meta{{opacity:0.7;font-size:0.88rem;margin-bottom:14px;}}
    .pill-btn{{display:inline-block;margin:4px 6px 4px 0;padding:7px 18px;border-radius:50px;font-weight:700;font-size:0.85rem;text-decoration:none;transition:transform 0.15s;}}
    .pill-btn:hover{{transform:scale(1.06);}}
    .song-box{{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);backdrop-filter:blur(12px);
        padding:25px;border-radius:16px;border-left:6px solid {accent};color:white;text-align:center;
        margin-bottom:20px;box-shadow:0 8px 32px rgba(0,0,0,0.4);transition:transform 0.3s ease;}}
    .song-box:hover{{transform:translateY(-5px);}}
    .history-card{{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:15px 20px;margin-bottom:12px;}}
    .badge-card{{display:inline-block;background:rgba(255,255,255,0.08);border:1px solid {accent}55;border-radius:12px;padding:10px 16px;margin:6px;text-align:center;min-width:140px;}}
    .dna-card{{background:linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.02));border:1px solid {accent}55;border-radius:20px;padding:28px 32px;text-align:center;box-shadow:0 8px 40px rgba(0,0,0,0.5);}}
    .pgen-card{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:16px 20px;margin-bottom:10px;}}
    .comment-bubble{{background:rgba(255,255,255,0.06);border-radius:10px;padding:8px 14px;margin:4px 0;font-size:0.88rem;}}
    .title-text{{text-align:center;font-weight:800;background:-webkit-linear-gradient(45deg,{accent},#FFFFFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:'Inter',sans-serif;padding-bottom:10px;}}
    @keyframes shimmer{{0%{{background-position:0% center;}}100%{{background-position:200% center;}}}}
    @keyframes floatNote{{0%{{opacity:0;transform:translateY(0) rotate(-10deg);}}20%{{opacity:0.7;}}80%{{opacity:0.4;}}100%{{opacity:0;transform:translateY(-70px) rotate(15deg);}}}}
    .plm-header{{text-align:center;padding:28px 0 10px 0;position:relative;}}
    .plm-header h1{{font-size:2.6rem;font-weight:800;letter-spacing:-1px;background:linear-gradient(90deg,{accent},#ffffff,{accent});background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 3s linear infinite;margin:0;}}
    .note{{position:absolute;font-size:1.5rem;opacity:0;animation:floatNote 4s ease-in-out infinite;}}
    .skeleton{{background:linear-gradient(90deg,rgba(255,255,255,0.06) 25%,rgba(255,255,255,0.13) 50%,rgba(255,255,255,0.06) 75%);background-size:200% 100%;animation:skeletonPulse 1.4s ease infinite;border-radius:12px;}}
    @keyframes skeletonPulse{{0%{{background-position:200% 0;}}100%{{background-position:-200% 0;}}}}
    .skeleton-card{{border-radius:20px;padding:28px 32px;margin-bottom:22px;border:1px solid rgba(255,255,255,0.07);}}
    .plm-toast{{position:fixed;top:20px;right:20px;z-index:99999;min-width:280px;max-width:360px;background:rgba(20,20,30,0.92);border:1px solid {accent}66;border-left:4px solid {accent};border-radius:14px;padding:14px 18px;backdrop-filter:blur(16px);box-shadow:0 8px 32px rgba(0,0,0,0.5);display:flex;align-items:center;gap:12px;animation:toastIn 0.35s cubic-bezier(.4,2,.6,1) forwards,toastOut 0.35s ease 3.5s forwards;color:white;font-size:0.95rem;font-weight:600;}}
    @keyframes toastIn{{from{{opacity:0;transform:translateX(60px) scale(0.9);}}to{{opacity:1;transform:translateX(0) scale(1);}}}}
    @keyframes toastOut{{from{{opacity:1;transform:translateX(0) scale(1);}}to{{opacity:0;transform:translateX(60px) scale(0.9);}}}}
    .now-playing-bar{{position:fixed;bottom:0;left:0;right:0;z-index:9999;background:rgba(10,10,18,0.88);border-top:1px solid {accent}44;backdrop-filter:blur(20px);padding:10px 24px;display:flex;align-items:center;gap:16px;box-shadow:0 -4px 30px rgba(0,0,0,0.5);}}
    .np-pulse{{width:10px;height:10px;border-radius:50%;background:{accent};animation:npPulse 1.2s ease-in-out infinite;flex-shrink:0;}}
    @keyframes npPulse{{0%,100%{{transform:scale(1);opacity:1;}}50%{{transform:scale(1.7);opacity:0.6;}}}}
    .np-eq{{display:flex;align-items:flex-end;gap:3px;height:22px;flex-shrink:0;}}
    .np-eq span{{display:inline-block;width:4px;background:{accent};border-radius:2px;animation:eqBounce 0.8s ease-in-out infinite;}}
    .np-eq span:nth-child(2){{animation-delay:0.15s;}} .np-eq span:nth-child(3){{animation-delay:0.3s;}} .np-eq span:nth-child(4){{animation-delay:0.1s;}}
    @keyframes eqBounce{{0%,100%{{height:4px;}}50%{{height:18px;}}}}
    .main .block-container{{padding-bottom:80px!important;}}
    section[data-testid="stSidebar"]>div{{background:rgba(10,10,20,0.82)!important;border-right:1px solid {accent}22!important;backdrop-filter:blur(24px)!important;padding:1.2rem 1rem!important;}}
    .sidebar-avatar{{width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,{accent},{accent}88);display:flex;align-items:center;justify-content:center;font-size:1.8rem;margin:0 auto 10px auto;box-shadow:0 0 20px {accent}55;}}
    .queue-item{{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.04);border-radius:8px;padding:6px 10px;margin-bottom:5px;font-size:0.85rem;border-left:3px solid {accent}55;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
    .onboard-wrap{{max-width:640px;margin:40px auto;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);border-radius:24px;padding:40px 44px;backdrop-filter:blur(20px);box-shadow:0 16px 60px rgba(0,0,0,0.5);text-align:center;}}
    .stTabs [data-baseweb="tab-list"]{{gap:6px;}}
    .stTabs [data-baseweb="tab"]{{height:42px;background-color:rgba(255,255,255,0.04)!important;border-radius:10px 10px 0 0;padding:6px 14px;font-size:0.92rem;transition:background 0.2s;}}
    .stTabs [data-baseweb="tab"]:hover{{background-color:rgba(255,255,255,0.09)!important;}}
    .stTabs [aria-selected="true"]{{background-color:{accent}22!important;border-bottom:2px solid {accent}!important;}}
    @media(max-width:768px){{
        .song-card{{padding:16px 14px;border-radius:14px;}} .song-card h2{{font-size:1.1rem;}}
        .plm-header h1{{font-size:1.8rem;}} .dna-card{{padding:18px 14px;}}
        .badge-card{{min-width:90px;padding:8px 10px;}} .onboard-wrap{{padding:24px 18px;margin:16px;}}
        .now-playing-bar{{padding:8px 14px;}}
        .stTabs [data-baseweb="tab"]{{padding:5px 7px;font-size:0.75rem;height:36px;}}
        section[data-testid="stSidebar"]>div{{padding:1rem 0.6rem!important;}}
    }}
    @media(max-width:480px){{
        .plm-header h1{{font-size:1.4rem;}} .stTabs [data-baseweb="tab"]{{padding:4px 5px;font-size:0.68rem;}}
    }}
    </style>""", unsafe_allow_html=True)

def render_animated_header(mood="Relaxed"):
    import random
    accent = MOOD_ACCENT.get(mood,"#1DB954")
    notes = ["♪","♫","♬","🎵","🎶"]
    notes_html = "".join(
        f"<span class='note' style='left:{random.randint(5,95)}%;animation-delay:{round(random.uniform(0,4),1)}s;'>{notes[i%5]}</span>"
        for i in range(8))
    st.markdown(f"""<div class='plm-header'>
        <div style='position:absolute;top:18px;left:50%;transform:translateX(-50%);width:100%;overflow:hidden;height:80px;pointer-events:none;'>{notes_html}</div>
        <h1>🎵 PLM Devs Music AI</h1>
        <p style='opacity:0.6;font-size:1rem;margin:6px 0 0 0;'>{MOOD_EMOJI.get(mood,'')} {mood} Mode &nbsp;·&nbsp; Powered by Q-Learning AI</p>
    </div>""", unsafe_allow_html=True)

def render_song_card(song: dict, mood="Relaxed"):
    accent = MOOD_ACCENT.get(song.get("Mood",mood),"#1DB954")
    sp = f"https://open.spotify.com/search/{song['Song'].replace(' ','%20')}"
    yt = f"https://www.youtube.com/results?search_query={song['Song'].replace(' ','+')} "
    energy_badge = {"High":f"<span style='background:#ff444422;color:#ff8888;border:1px solid #ff444444;border-radius:20px;padding:2px 10px;font-size:0.78rem;'>⚡ High</span>",
                    "Medium":f"<span style='background:#ffa50022;color:#ffcc66;border:1px solid #ffa50044;border-radius:20px;padding:2px 10px;font-size:0.78rem;'>⚡ Med</span>",
                    "Low":f"<span style='background:#1db95422;color:#1db954;border:1px solid #1db95444;border-radius:20px;padding:2px 10px;font-size:0.78rem;'>⚡ Low</span>"
                    }.get(str(song.get("Energy","")),"")
    st.markdown(f"""<div class='song-card' style='border-left-color:{accent};'>
        <h2>{song['Song']}</h2>
        <div class='meta'>🎭 {song.get('Mood','')} &nbsp;·&nbsp; 🎸 {song.get('Genre','')} &nbsp;·&nbsp; 🌐 {song.get('Language','')} &nbsp; {energy_badge}</div>
        <a class='pill-btn' href='{sp}' target='_blank' style='background:#1DB954;color:#000;'>🎧 Spotify</a>
        <a class='pill-btn' href='{yt}' target='_blank' style='background:#FF0000;color:#fff;'>▶ YouTube</a>
    </div>""", unsafe_allow_html=True)

def render_skeleton_cards(n=3):
    for _ in range(n):
        st.markdown("""<div class='skeleton-card skeleton'>
            <div class='skeleton' style='height:22px;width:60%;border-radius:8px;margin-bottom:14px;'></div>
            <div class='skeleton' style='height:14px;width:45%;border-radius:7px;margin:10px 0;'></div>
            <div class='skeleton' style='height:14px;width:70%;border-radius:7px;margin:10px 0;'></div>
            <div style='display:flex;gap:10px;margin-top:16px;'>
                <div class='skeleton' style='height:34px;width:100px;border-radius:20px;'></div>
                <div class='skeleton' style='height:34px;width:100px;border-radius:20px;'></div>
            </div></div>""", unsafe_allow_html=True)

def render_mood_selector(current_mood="Relaxed") -> str:
    st.markdown("<p style='font-weight:700;font-size:1rem;margin-bottom:4px;'>🎭 Pick Your Mood</p>", unsafe_allow_html=True)
    moods = [("Happy","😄","#FFD700","Party / Upbeat"),("Sad","😢","#6495ED","Heartbreak / Calm"),
             ("Focus","🎯","#FF8C00","Study / Work"),("Relaxed","😌","#1DB954","Chill / Sleep")]
    cols = st.columns(4); selected = current_mood
    for col, (mn, emoji, color, subtitle) in zip(cols, moods):
        is_active = current_mood == mn
        border = f"2px solid {color}" if is_active else "2px solid rgba(255,255,255,0.12)"
        bg = f"{color}22" if is_active else "rgba(255,255,255,0.05)"
        shadow = f"0 0 18px {color}44" if is_active else "none"
        glow = f"text-shadow:0 0 12px {color};" if is_active else ""
        with col:
            st.markdown(f"""<div style='background:{bg};border:{border};border-radius:18px;padding:16px 10px;text-align:center;box-shadow:{shadow};'>
                <div style='font-size:2.2rem;{glow}'>{emoji}</div>
                <div style='font-weight:800;font-size:0.92rem;margin-top:6px;'>{mn}</div>
                <div style='font-size:0.72rem;opacity:0.6;margin-top:2px;'>{subtitle}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Select {mn}", key=f"moodsel_{mn}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                selected = mn
    return selected

def show_toast(message, icon="🎵", mood="Relaxed"):
    accent = MOOD_ACCENT.get(mood,"#1DB954")
    st.markdown(f"<div class='plm-toast' style='border-left-color:{accent};'><span style='font-size:1.4rem;'>{icon}</span><span>{message}</span></div>", unsafe_allow_html=True)

def render_now_playing_bar(song_name, mood, genre, queue_count=0, mood_color="#1DB954"):
    sp = f"https://open.spotify.com/search/{song_name.replace(' ','%20')}"
    yt = f"https://www.youtube.com/results?search_query={song_name.replace(' ','+')} "
    qbadge = f"<span style='background:rgba(255,255,255,0.1);border-radius:20px;padding:3px 10px;font-size:0.78rem;'>🗂️ {queue_count} in queue</span>" if queue_count > 0 else ""
    st.markdown(f"""<div class='now-playing-bar'>
        <div class='np-pulse' style='background:{mood_color};'></div>
        <div class='np-eq'><span style='height:8px;'></span><span style='height:14px;'></span><span style='height:18px;'></span><span style='height:10px;'></span></div>
        <div style='flex:1;min-width:0;'><div style='font-weight:700;font-size:0.92rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>🎵 {song_name}</div>
        <div style='font-size:0.78rem;opacity:0.6;margin-top:1px;'>🎭 {mood} &nbsp;·&nbsp; 🎸 {genre} &nbsp; {qbadge}</div></div>
        <div style='display:flex;gap:8px;flex-shrink:0;'>
            <a href='{sp}' target='_blank' style='background:#1DB954;color:#000;border-radius:20px;padding:5px 14px;font-size:0.8rem;font-weight:700;text-decoration:none;'>🎧 Spotify</a>
            <a href='{yt}' target='_blank' style='background:#FF0000;color:#fff;border-radius:20px;padding:5px 14px;font-size:0.8rem;font-weight:700;text-decoration:none;'>▶ YouTube</a>
        </div></div>""", unsafe_allow_html=True)

def render_sidebar(username, xp, level, streak, queue, favs, mood="Relaxed"):
    accent = MOOD_ACCENT.get(mood,"#1DB954")
    initials = username[:2].upper() if username else "??"
    lvl_thresh = [0,50,150,300,600,1000]
    next_t = next((t for t in lvl_thresh if t > xp),1000)
    prev_t = max((t for t in lvl_thresh if t <= xp),default=0)
    pct = int((xp-prev_t)/max(next_t-prev_t,1)*100)
    st.markdown(f"""<div class='sidebar-avatar'>{initials}</div>
    <div style='text-align:center;font-weight:800;font-size:1.1rem;margin-bottom:2px;'>{username}</div>
    <div style='text-align:center;font-size:0.8rem;opacity:0.6;margin-bottom:12px;'>{level}</div>
    <div style='display:flex;justify-content:space-between;font-size:0.75rem;opacity:0.6;margin-bottom:4px;'><span>⚡ {xp} XP</span><span>{next_t-xp} to next</span></div>
    <div style='background:rgba(255,255,255,0.1);border-radius:20px;height:6px;margin-bottom:14px;'><div style='background:{accent};width:{pct}%;height:6px;border-radius:20px;box-shadow:0 0 8px {accent}88;'></div></div>
    <div style='display:flex;justify-content:space-around;background:rgba(255,255,255,0.05);border-radius:12px;padding:10px 8px;margin-bottom:16px;'>
        <div style='text-align:center;'><div style='font-weight:800;font-size:1.1rem;color:{accent};'>🔥{streak}</div><div style='font-size:0.72rem;opacity:0.55;'>Streak</div></div>
        <div style='text-align:center;'><div style='font-weight:800;font-size:1.1rem;color:{accent};'>{xp}</div><div style='font-size:0.72rem;opacity:0.55;'>XP</div></div>
        <div style='text-align:center;'><div style='font-weight:800;font-size:1.1rem;color:{accent};'>❤️{len(favs)}</div><div style='font-size:0.72rem;opacity:0.55;'>Favs</div></div>
    </div>
    <p style='font-weight:700;font-size:0.85rem;opacity:0.7;margin:0 0 6px 0;'>🗂️ Queue ({len(queue)})</p>""", unsafe_allow_html=True)
    if not queue:
        st.markdown("<p style='font-size:0.8rem;opacity:0.4;font-style:italic;'>Empty — like a song!</p>", unsafe_allow_html=True)
    else:
        for item in queue[::-1][:6]:
            st.markdown(f"<div class='queue-item'>🎵 {item}</div>", unsafe_allow_html=True)
        if len(queue) > 6:
            st.markdown(f"<p style='font-size:0.75rem;opacity:0.4;text-align:center;'>+{len(queue)-6} more</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def render_onboarding():
    if "onboard_step" not in st.session_state: st.session_state.onboard_step = 1
    step = st.session_state.onboard_step
    dots = "".join(f"<div style='width:10px;height:10px;border-radius:50%;background:{'#1DB954' if i==step else 'rgba(255,255,255,0.2)'};display:inline-block;margin:0 4px;'></div>" for i in range(1,4))
    STEPS = {1:("👋","Welcome to PLM Music AI!","Ek personal AI jo tere saath music taste seekhta hai.",["🧠 Q-Learning Engine","🎭 Mood Detection","🏆 Gamification"]),
             2:("🎭","Apna Pehla Mood Batao","Abhi is waqt kaisa feel ho raha hai?",None),
             3:("🌍","Language Choose Karo","Kaunsi language mein gaane sunna chahte ho?",None)}
    icon,title,subtitle,features = STEPS[step]
    st.markdown(f"""<style>.onboard-wrap{{max-width:640px;margin:40px auto;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12);border-radius:24px;padding:40px 44px;backdrop-filter:blur(20px);box-shadow:0 16px 60px rgba(0,0,0,0.5);text-align:center;}}</style>
    <div class='onboard-wrap'><div style='font-size:3.5rem;margin-bottom:12px;'>{icon}</div>
    <h2 style='margin:0 0 8px 0;font-size:1.5rem;font-weight:800;'>{title}</h2>
    <p style='opacity:0.7;margin:0 0 4px 0;font-size:0.95rem;'>{subtitle}</p>
    <div style='display:flex;justify-content:center;gap:8px;margin:24px 0 8px 0;'>{dots}</div></div>""", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1,2,1])
    with center_col:
        if step == 1:
            if features:
                for feat in features:
                    st.markdown(f"<div style='background:rgba(29,185,84,0.1);border:1px solid #1DB95444;border-radius:10px;padding:10px 16px;margin:6px 0;font-weight:600;'>{feat}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Chalo Shuru Karte Hain! 🚀", use_container_width=True, type="primary"):
                st.session_state.onboard_step = 2; st.rerun()
        elif step == 2:
            for label, val in [("😄 Happy","Happy"),("😢 Sad","Sad"),("🎯 Focus","Focus"),("😌 Relaxed","Relaxed")]:
                if st.button(label, use_container_width=True, key=f"ob_mood_{val}"):
                    st.session_state.current_mood = val; st.session_state.onboard_step = 3; st.rerun()
        elif step == 3:
            for label, val in [("🇮🇳 Hindi","Hindi"),("🇬🇧 English","English"),("🎺 Punjabi","Punjabi"),("🎵 Tamil","Tamil"),("🎶 Telugu","Telugu")]:
                if st.button(label, use_container_width=True, key=f"ob_lang_{label}"):
                    st.session_state.current_language = val; st.session_state.onboard_done = True; st.session_state.onboard_step = 1; st.rerun()
