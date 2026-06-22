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

    /* ══ TASK 1: BETTER COLOUR PALETTE PER MOOD ══ */
    /* Richer background gradients with radial glow overlay */
    .mood-bg-happy  {{ background: radial-gradient(ellipse at 20% 50%, #3a2a00 0%, #1a1a0a 40%, #0d1a0d 100%) !important; }}
    .mood-bg-sad    {{ background: radial-gradient(ellipse at 80% 20%, #0a0a2e 0%, #0d0d1a 40%, #060612 100%) !important; }}
    .mood-bg-focus  {{ background: radial-gradient(ellipse at 50% 80%, #2a1000 0%, #1a0d00 40%, #0d0800 100%) !important; }}
    .mood-bg-relaxed{{ background: radial-gradient(ellipse at 30% 30%, #002a12 0%, #001a0d 40%, #000d08 100%) !important; }}
    /* Mood-specific glow on interactive elements */
    .mood-happy  .stButton>button[kind="primary"] {{ box-shadow: 0 4px 20px #FFD70066 !important; }}
    .mood-sad    .stButton>button[kind="primary"] {{ box-shadow: 0 4px 20px #6495ED66 !important; }}
    .mood-focus  .stButton>button[kind="primary"] {{ box-shadow: 0 4px 20px #FF8C0066 !important; }}
    .mood-relaxed .stButton>button[kind="primary"]{{ box-shadow: 0 4px 20px #1DB95466 !important; }}
    /* Particle glow dots in background */
    .stApp::before {{
        content: '';
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none; z-index: 0;
        background:
            radial-gradient(circle at 15% 25%, {accent}18 0%, transparent 25%),
            radial-gradient(circle at 85% 75%, {accent}12 0%, transparent 20%),
            radial-gradient(circle at 50% 10%, {accent}08 0%, transparent 30%);
        animation: glowShift 8s ease-in-out infinite alternate;
    }}
    @keyframes glowShift {{
        from {{ opacity: 0.6; transform: scale(1); }}
        to   {{ opacity: 1;   transform: scale(1.05); }}
    }}

    /* ══ TASK 2: ENHANCED SONG CARD HOVER EFFECT ══ */
    .song-card {{
        transition: transform 0.3s cubic-bezier(.4,2,.3,1),
                    box-shadow 0.3s ease,
                    border-color 0.3s ease !important;
    }}
    .song-card:hover {{
        transform: translateY(-8px) scale(1.015) !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.7),
                    0 0 40px {accent}33,
                    0 0 80px {accent}11 !important;
        border-left-color: {accent} !important;
    }}
    .song-card:hover h2 {{
        background: linear-gradient(90deg, {accent}, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .song-card:active {{ transform: translateY(-4px) scale(1.008) !important; }}

    /* ══ TASK 5: MOOD RING / BADGE PULSE ANIMATION ══ */
    .mood-ring {{
        display: inline-flex; align-items: center; gap: 8px;
        background: {accent}18;
        border: 1.5px solid {accent};
        border-radius: 30px;
        padding: 8px 22px;
        font-size: 1.1rem;
        font-weight: 700;
        position: relative;
        animation: moodRingPulse 2.5s ease-in-out infinite;
    }}
    .mood-ring::before, .mood-ring::after {{
        content: '';
        position: absolute; inset: -4px;
        border-radius: 34px;
        border: 1.5px solid {accent};
        animation: moodRingRipple 2.5s ease-out infinite;
        opacity: 0;
    }}
    .mood-ring::after {{ animation-delay: 1.25s; }}
    @keyframes moodRingPulse {{
        0%,100% {{ box-shadow: 0 0 10px {accent}44; }}
        50%      {{ box-shadow: 0 0 25px {accent}88, 0 0 50px {accent}33; }}
    }}
    @keyframes moodRingRipple {{
        0%   {{ transform: scale(1);    opacity: 0.6; }}
        100% {{ transform: scale(1.35); opacity: 0; }}
    }}
    .mood-ring-dot {{
        width: 9px; height: 9px; border-radius: 50%;
        background: {accent};
        animation: dotBlink 1.5s ease-in-out infinite;
        box-shadow: 0 0 8px {accent};
    }}
    @keyframes dotBlink {{
        0%,100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.4; transform: scale(0.7); }}
    }}

    /* ══ TASK 6: SONG CARD FLIP ANIMATION ══ */
    .flip-container {{
        perspective: 1000px;
        margin-bottom: 22px;
    }}
    .flip-card {{
        position: relative;
        transform-style: preserve-3d;
        animation: cardFlipReveal 0.7s cubic-bezier(.4,2,.3,1) both;
    }}
    @keyframes cardFlipReveal {{
        0%   {{ transform: rotateY(-90deg) translateY(20px); opacity: 0; }}
        60%  {{ transform: rotateY(8deg)  translateY(-4px);  opacity: 1; }}
        100% {{ transform: rotateY(0deg)  translateY(0);     opacity: 1; }}
    }}
    .flip-card:nth-child(1) {{ animation-delay: 0.0s; }}
    .flip-card:nth-child(2) {{ animation-delay: 0.12s; }}
    .flip-card:nth-child(3) {{ animation-delay: 0.24s; }}

    /* ══ TASK 3: ANIMATED COUNTER ══ */
    .animated-counter {{
        display: inline-block;
        font-weight: 800;
        font-size: 2.2rem;
        color: {accent};
        animation: counterPop 0.5s cubic-bezier(.4,2,.3,1) both;
    }}
    @keyframes counterPop {{
        0%   {{ transform: scale(0.5); opacity: 0; }}
        70%  {{ transform: scale(1.15); }}
        100% {{ transform: scale(1);   opacity: 1; }}
    }}

    /* ══ TASK 4: PROFILE AVATAR ══ */
    .profile-avatar-wrap {{
        display: flex; flex-direction: column; align-items: center;
        margin-bottom: 20px;
    }}
    .profile-avatar-ring {{
        width: 96px; height: 96px; border-radius: 50%;
        padding: 3px;
        background: conic-gradient(
            {accent} 0deg,
            {accent}88 120deg,
            transparent 120deg,
            transparent 180deg,
            {accent}88 180deg,
            {accent} 360deg
        );
        animation: avatarRingSpin 4s linear infinite;
        margin-bottom: 12px;
    }}
    @keyframes avatarRingSpin {{
        to {{ transform: rotate(360deg); }}
    }}
    .profile-avatar-inner {{
        width: 90px; height: 90px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 2.2rem; font-weight: 800;
        letter-spacing: -1px;
        background: #0a0a12;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }}
    </style>""", unsafe_allow_html=True)
    /* ══ SMOOTH PAGE TRANSITIONS ══ */
    .stTabs [data-baseweb="tab-panel"] {{
        animation: fadeSlideIn 0.35s cubic-bezier(.4,0,.2,1);
    }}
    @keyframes fadeSlideIn {{
        from {{ opacity:0; transform:translateY(10px); }}
        to   {{ opacity:1; transform:translateY(0); }}
    }}
    /* ══ LOADING SCREEN ══ */
    .plm-splash {{
        position:fixed; top:0; left:0; right:0; bottom:0; z-index:999999;
        background:linear-gradient(135deg,#060610,#0a120a);
        display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        animation: splashFade 0.6s ease 2.5s forwards;
    }}
    @keyframes splashFade {{
        from {{ opacity:1; pointer-events:all; }}
        to   {{ opacity:0; pointer-events:none; visibility:hidden; }}
    }}
    .plm-splash-logo {{
        font-size:5rem; display:block;
        animation: logoBounce 0.7s cubic-bezier(.4,2,.6,1) 0.2s both;
    }}
    @keyframes logoBounce {{
        from {{ transform:scale(0.3) rotate(-15deg); opacity:0; }}
        to   {{ transform:scale(1) rotate(0deg); opacity:1; }}
    }}
    .plm-splash-title {{
        font-size:2rem; font-weight:800; margin:16px 0 6px 0;
        background:linear-gradient(90deg,{accent},#fff,{accent});
        background-size:200% auto;
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        animation: shimmer 2s linear infinite, fadeUp 0.5s ease 0.5s both;
    }}
    .plm-splash-sub {{
        font-size:0.9rem; opacity:0.55; letter-spacing:1px;
        animation: fadeUp 0.5s ease 0.8s both;
    }}
    .plm-splash-dots {{
        display:flex; gap:8px; margin-top:32px;
        animation: fadeUp 0.5s ease 1s both;
    }}
    .plm-splash-dot {{
        width:8px; height:8px; border-radius:50%; background:{accent};
        animation: dotPulse 1s ease-in-out infinite;
    }}
    .plm-splash-dot:nth-child(2) {{ animation-delay:0.15s; }}
    .plm-splash-dot:nth-child(3) {{ animation-delay:0.3s; }}
    @keyframes dotPulse {{
        0%,100% {{ transform:scale(1); opacity:0.4; }}
        50%      {{ transform:scale(1.5); opacity:1; }}
    }}
    @keyframes fadeUp {{
        from {{ opacity:0; transform:translateY(14px); }}
        to   {{ opacity:1; transform:translateY(0); }}
    }}
    /* ══ ALBUM ART PLACEHOLDER ══ */
    .album-art {{
        width:68px; height:68px; border-radius:10px; flex-shrink:0;
        display:flex; align-items:center; justify-content:center;
        font-size:1.6rem; position:relative; overflow:hidden;
        box-shadow:0 4px 16px rgba(0,0,0,0.5);
    }}
    .album-art::before {{
        content:'';
        position:absolute; inset:0;
        background:linear-gradient(135deg,rgba(255,255,255,0.18) 0%,transparent 60%);
        z-index:1;
    }}
    .album-vinyl {{
        position:absolute; width:28px; height:28px; border-radius:50%;
        border:3px solid rgba(0,0,0,0.25); right:-6px; bottom:-6px;
        opacity:0.7; z-index:2;
    }}
    .album-vinyl::after {{
        content:''; position:absolute; inset:6px; border-radius:50%;
        background:rgba(0,0,0,0.4);
    }}
    /* ══ ENHANCED VISUALIZER BARS ══ */
    .viz-bar-wrap {{
        display:flex; align-items:flex-end; gap:3px; height:28px;
    }}
    .vbar {{
        width:4px; border-radius:3px; background:{accent};
        box-shadow:0 0 6px {accent}88;
        animation:vbarAnim 0.7s ease-in-out infinite alternate;
    }}
    .vbar:nth-child(1){{animation-duration:0.6s;}}
    .vbar:nth-child(2){{animation-duration:0.8s;animation-delay:0.1s;}}
    .vbar:nth-child(3){{animation-duration:0.5s;animation-delay:0.2s;}}
    .vbar:nth-child(4){{animation-duration:0.9s;animation-delay:0.05s;}}
    .vbar:nth-child(5){{animation-duration:0.7s;animation-delay:0.15s;}}
    .vbar:nth-child(6){{animation-duration:0.6s;animation-delay:0.25s;}}
    @keyframes vbarAnim {{
        from {{ height:3px; }}
        to   {{ height:24px; }}
    }}
    /* ══ LYRICS SEARCH ══ */
    .lyrics-result {{
        background:rgba(255,255,255,0.05);
        border:1px solid rgba(255,255,255,0.1);
        border-radius:14px; padding:14px 18px; margin-bottom:10px;
        border-left:4px solid {accent};
        transition:all 0.2s;
    }}
    .lyrics-result:hover {{ transform:translateX(4px); background:rgba(255,255,255,0.08); }}
    .lyrics-match {{ color:{accent}; font-weight:700; }}
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
    # Inject base CSS so onboarding renders correctly before full theme loads
    inject_global_css(accent="#1DB954", bg=MOOD_GRADIENTS["Relaxed"])

    if "onboard_step" not in st.session_state:
        st.session_state.onboard_step = 1
    step = st.session_state.onboard_step

    # Progress dots
    dots = "".join(
        f"<div style='width:10px;height:10px;border-radius:50%;"
        f"background:{'#1DB954' if i == step else 'rgba(255,255,255,0.2)'};"
        f"display:inline-block;margin:0 4px;'></div>"
        for i in range(1, 4)
    )

    STEPS = {
        1: ("👋", "Welcome to PLM Music AI!",
            "Ek personal AI jo tere saath music taste seekhta hai.",
            ["🧠 Q-Learning Engine", "🎭 Mood Detection", "🏆 Gamification"]),
        2: ("🎭", "Apna Pehla Mood Batao",
            "Abhi is waqt kaisa feel ho raha hai?", None),
        3: ("🌍", "Language Choose Karo",
            "Kaunsi language mein gaane sunna chahte ho?", None),
    }
    icon, title, subtitle, features = STEPS[step]

    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown(
            f"<div style='text-align:center;padding:40px 20px 20px 20px;'>"
            f"<div style='font-size:3.5rem;margin-bottom:12px;'>{icon}</div>"
            f"<h2 style='margin:0 0 8px 0;font-size:1.5rem;font-weight:800;color:white;'>{title}</h2>"
            f"<p style='opacity:0.7;margin:0 0 16px 0;font-size:0.95rem;color:white;'>{subtitle}</p>"
            f"<div style='display:flex;justify-content:center;gap:8px;margin-bottom:24px;'>{dots}</div>"
            f"</div>",
            unsafe_allow_html=True)

        if step == 1:
            if features:
                for feat in features:
                    st.markdown(
                        f"<div style='background:rgba(29,185,84,0.12);border:1px solid #1DB95444;"
                        f"border-radius:12px;padding:12px 18px;margin:6px 0;"
                        f"font-weight:600;font-size:0.95rem;color:white;'>{feat}</div>",
                        unsafe_allow_html=True)
            st.write("")
            if st.button("Chalo Shuru Karte Hain! 🚀",
                         use_container_width=True, type="primary"):
                st.session_state.onboard_step = 2
                st.rerun()

        elif step == 2:
            for label, val in [("😄 Happy", "Happy"), ("😢 Sad", "Sad"),
                                ("🎯 Focus", "Focus"), ("😌 Relaxed", "Relaxed")]:
                if st.button(label, use_container_width=True, key=f"ob_mood_{val}"):
                    st.session_state.current_mood = val
                    st.session_state.onboard_step = 3
                    st.rerun()

        elif step == 3:
            lang_map = {"🇮🇳 Hindi": "Hindi", "🇬🇧 English": "English",
                        "🎺 Punjabi": "Punjabi", "🎵 Tamil": "Tamil", "🎶 Telugu": "Telugu"}
            for label, val in lang_map.items():
                if st.button(label, use_container_width=True, key=f"ob_lang_{label}"):
                    st.session_state.current_language = val
                    st.session_state.onboard_done    = True
                    st.session_state.onboard_step    = 1
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────
# LOADING / SPLASH SCREEN
# ─────────────────────────────────────────────────────────────────────
def render_splash_screen():
    """Show an animated splash screen that auto-fades after ~2.5s."""
    st.markdown("""
    <div class='plm-splash'>
        <span class='plm-splash-logo'>🎵</span>
        <div class='plm-splash-title'>PLM Devs Music AI</div>
        <div class='plm-splash-sub'>✦ crafted by Pranav Chakravorty ✦</div>
        <div class='plm-splash-dots'>
            <div class='plm-splash-dot'></div>
            <div class='plm-splash-dot'></div>
            <div class='plm-splash-dot'></div>
        </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# ALBUM ART PLACEHOLDER (mood + genre based gradient thumbnail)
# ─────────────────────────────────────────────────────────────────────
_GENRE_EMOJI = {
    "Pop": "🎤", "Rock": "🎸", "Lo-fi": "🎹",
    "Classical": "🎻", "Instrumental": "🎺",
}
_MOOD_ART_COLORS = {
    "Happy":   ("linear-gradient(135deg,#FFD700,#FF8C00)", "#FFD70033"),
    "Sad":     ("linear-gradient(135deg,#6495ED,#3a5fc8)", "#6495ED33"),
    "Focus":   ("linear-gradient(135deg,#FF8C00,#cc4400)", "#FF8C0033"),
    "Relaxed": ("linear-gradient(135deg,#1DB954,#0a8a3a)", "#1DB95433"),
}

def get_album_art_html(song: dict, size: int = 68) -> str:
    mood  = song.get("Mood", "Relaxed")
    genre = song.get("Genre", "Pop")
    emoji = _GENRE_EMOJI.get(genre, "🎵")
    gradient, shadow = _MOOD_ART_COLORS.get(mood, _MOOD_ART_COLORS["Relaxed"])
    vinyl_color = MOOD_ACCENT.get(mood, "#1DB954")
    return (
        f"<div class='album-art' style='background:{gradient};"
        f"box-shadow:0 4px 20px {shadow};width:{size}px;height:{size}px;'>"
        f"<span style='position:relative;z-index:2;'>{emoji}</span>"
        f"<div class='album-vinyl' style='background:{vinyl_color}33;'></div>"
        f"</div>"
    )


def render_song_card_with_art(song: dict, mood: str = "Relaxed"):
    """Glassmorphism song card with album art thumbnail on the left."""
    accent    = MOOD_ACCENT.get(song.get("Mood", mood), "#1DB954")
    sp_url    = f"https://open.spotify.com/search/{song['Song'].replace(' ','%20')}"
    yt_url    = f"https://www.youtube.com/results?search_query={song['Song'].replace(' ','+')} "
    art_html  = get_album_art_html(song)
    energy    = str(song.get("Energy", ""))
    e_color   = {"High":"#ff8888","Medium":"#ffcc66","Low":"#1db954"}.get(energy, "#aaa")
    e_badge   = (f"<span style='background:{e_color}22;color:{e_color};"
                 f"border:1px solid {e_color}44;border-radius:20px;"
                 f"padding:2px 10px;font-size:0.75rem;'>⚡ {energy}</span>"
                 if energy else "")
    st.markdown(f"""
    <div class='song-card' style='border-left-color:{accent};'>
        <div style='display:flex;align-items:flex-start;gap:16px;'>
            {art_html}
            <div style='flex:1;min-width:0;'>
                <h2 style='margin:0 0 4px 0;'>{song['Song']}</h2>
                <div class='meta'>
                    🎭 {song.get('Mood','')} &nbsp;·&nbsp;
                    🎸 {song.get('Genre','')} &nbsp;·&nbsp;
                    🌐 {song.get('Language','')} &nbsp; {e_badge}
                </div>
                <a class='pill-btn' href='{sp_url}' target='_blank'
                   style='background:#1DB954;color:#000;'>🎧 Spotify</a>
                <a class='pill-btn' href='{yt_url}' target='_blank'
                   style='background:#FF0000;color:#fff;'>▶ YouTube</a>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# ENHANCED NOW PLAYING BAR (with better visualizer)
# ─────────────────────────────────────────────────────────────────────
def render_now_playing_bar_v2(song_name: str, mood: str, genre: str,
                               queue_count: int = 0, mood_color: str = "#1DB954",
                               song: dict = None):
    """Enhanced now playing bar with album art + better visualizer."""
    sp_url  = f"https://open.spotify.com/search/{song_name.replace(' ','%20')}"
    yt_url  = f"https://www.youtube.com/results?search_query={song_name.replace(' ','+')} "
    art_html = get_album_art_html(song or {"Mood": mood, "Genre": genre}, size=44)
    qbadge  = (f"<span style='background:rgba(255,255,255,0.1);border-radius:20px;"
               f"padding:2px 10px;font-size:0.76rem;'>🗂️ {queue_count}</span>"
               if queue_count > 0 else "")
    # 6-bar visualizer with varying heights
    bars = ""
    for h in [8, 18, 12, 24, 10, 20]:
        bars += (f"<div class='vbar' style='height:{h}px;'></div>")

    st.markdown(f"""
    <div class='now-playing-bar'>
        {art_html}
        <div class='viz-bar-wrap'>{bars}</div>
        <div style='flex:1;min-width:0;margin-left:12px;'>
            <div style='font-weight:700;font-size:0.9rem;white-space:nowrap;
                overflow:hidden;text-overflow:ellipsis;'>
                🎵 {song_name}
            </div>
            <div style='font-size:0.76rem;opacity:0.6;margin-top:1px;'>
                🎭 {mood} &nbsp;·&nbsp; 🎸 {genre} &nbsp; {qbadge}
            </div>
        </div>
        <div style='display:flex;gap:8px;flex-shrink:0;'>
            <a href='{sp_url}' target='_blank'
               style='background:#1DB954;color:#000;border-radius:20px;
               padding:5px 14px;font-size:0.8rem;font-weight:700;text-decoration:none;'>
               🎧 Spotify</a>
            <a href='{yt_url}' target='_blank'
               style='background:#FF0000;color:#fff;border-radius:20px;
               padding:5px 14px;font-size:0.8rem;font-weight:700;text-decoration:none;'>
               ▶ YouTube</a>
        </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# LYRICS / KEYWORD SEARCH
# ─────────────────────────────────────────────────────────────────────
def render_lyrics_search(df):
    """
    Search songs by partial lyrics keywords or song fragment.
    df: the songs DataFrame (Song, Mood, Genre, Language, Energy, URL, SpotifyURL)
    """
    st.subheader("🎼 Lyrics / Keyword Search")
    st.caption("Koi bhi lyrics fragment, song ka hissa, ya keyword type karo — matching songs milenge!")

    query = st.text_input(
        "Lyrics ya keyword",
        placeholder="e.g. 'tum hi ho', 'baby', 'zindagi', 'love you'...",
        key="lyrics_search_q",
        label_visibility="collapsed"
    )

    if not query.strip():
        st.markdown("<p style='opacity:0.4;font-size:0.88rem;'>⬆️ Kuch type karo...</p>",
                    unsafe_allow_html=True)
        return

    q = query.strip().lower()
    # Match against song name (word-level partial match)
    results = df[df["Song"].str.lower().str.contains(q, na=False)]

    # If no match on exact, try word-by-word
    if results.empty:
        words = q.split()
        for word in words:
            if len(word) > 2:
                match = df[df["Song"].str.lower().str.contains(word, na=False)]
                results = match if results.empty else results
                break

    if results.empty:
        st.info(f"Koi match nahi mila '{query}' ke liye. Different keywords try karo!")
        return

    accent = "#1DB954"
    st.caption(f"**{len(results)}** song(s) mila:")
    for _, row in results.head(10).iterrows():
        sp  = f"https://open.spotify.com/search/{str(row['Song']).replace(' ','%20')}"
        yt  = f"https://www.youtube.com/results?search_query={str(row['Song']).replace(' ','+')}"
        mood_color = MOOD_ACCENT.get(row.get("Mood", ""), "#1DB954")
        # Highlight matching part in song name
        song_display = str(row["Song"])
        song_lower   = song_display.lower()
        if q in song_lower:
            idx  = song_lower.index(q)
            song_display = (
                song_display[:idx]
                + f"<span class='lyrics-match'>{song_display[idx:idx+len(q)]}</span>"
                + song_display[idx+len(q):]
            )
        st.markdown(f"""
        <div class='lyrics-result' style='border-left-color:{mood_color};'>
            <b style='font-size:1rem;'>🎵 {song_display}</b><br>
            <span style='opacity:0.65;font-size:0.82rem;'>
                🎭 {row.get('Mood','')} &nbsp;·&nbsp;
                🎸 {row.get('Genre','')} &nbsp;·&nbsp;
                🌐 {row.get('Language','')} &nbsp;·&nbsp;
                ⚡ {row.get('Energy','')}
            </span><br>
            <a href='{sp}' target='_blank'
               style='color:#1DB954;font-size:0.82rem;margin-right:12px;'>🎧 Spotify</a>
            <a href='{yt}' target='_blank'
               style='color:#ff4444;font-size:0.82rem;'>▶ YouTube</a>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# TASK 3: ANIMATED COUNTER (JS count-up)
# ─────────────────────────────────────────────────────────────────────
def render_animated_counter(value: int, label: str, accent: str = "#1DB954"):
    """Renders a JS count-up animated number with a label below it."""
    # Safe ID — remove all non-alphanumeric chars
    import re as _re
    uid = "ctr_" + _re.sub(r'[^a-z0-9]', '_', label.lower())[:20]
    st.markdown(f"""
    <div style='text-align:center;padding:8px 12px;'>
        <div id='{uid}' class='animated-counter' style='color:{accent};'>0</div>
        <div style='font-size:0.78rem;opacity:0.55;margin-top:4px;'>{label}</div>
    </div>
    <script>
    (function() {{
        var el = document.getElementById('{uid}');
        if (!el) return;
        var target = {value};
        var duration = 900;
        var start = null;
        function easeOut(t) {{ return 1 - Math.pow(1-t, 3); }}
        function step(ts) {{
            if (!start) start = ts;
            var progress = Math.min((ts - start) / duration, 1);
            el.textContent = Math.round(easeOut(progress) * target);
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = target;
        }}
        requestAnimationFrame(step);
    }})();
    </script>
    """, unsafe_allow_html=True)


def render_stats_row(sessions: int, likes: int, skips: int, streak: int,
                     accent: str = "#1DB954"):
    """4-column animated stats row for the Profile page."""
    cols = st.columns(4)
    stats = [
        (sessions, "🎵 Sessions"),
        (likes,    "👍 Likes"),
        (skips,    "⏭️ Skips"),
        (streak,   "🔥 Streak days"),
    ]
    for col, (val, lbl) in zip(cols, stats):
        with col:
            render_animated_counter(val, lbl, accent)


# ─────────────────────────────────────────────────────────────────────
# TASK 4: PROFILE AVATAR (spinning gradient ring + initials/emoji)
# ─────────────────────────────────────────────────────────────────────
_AVATAR_PALETTES = [
    ("#FFD700", "#FF8C00"),  # gold
    ("#1DB954", "#0a8a3a"),  # green
    ("#6495ED", "#3a5fc8"),  # blue
    ("#FF6B9D", "#c0245a"),  # pink
    ("#FF8C00", "#cc4400"),  # orange
    ("#A855F7", "#7c3aed"),  # purple
]

def render_profile_avatar(username: str, mood: str = "Relaxed", xp: int = 0):
    initials   = (username[:2].upper() if username else "??")
    mood_emoji = MOOD_EMOJI.get(mood, "🎵")
    accent     = MOOD_ACCENT.get(mood, "#1DB954")

    palette_idx = sum(ord(c) for c in (username or "?")) % len(_AVATAR_PALETTES)
    c1, c2 = _AVATAR_PALETTES[palette_idx]

    st.markdown(f"""
    <div class='profile-avatar-wrap'>
        <div class='profile-avatar-ring'
             style='background:conic-gradient({c1} 0deg,{c2} 120deg,
                    transparent 120deg,transparent 180deg,
                    {c2} 180deg,{c1} 360deg);'>
            <div class='profile-avatar-inner'
                 style='background:linear-gradient(135deg,#0a0a18,#12121f);'>
                <span style='background:linear-gradient(135deg,{c1},{c2});
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-size:2rem;font-weight:800;'>{initials}</span>
            </div>
        </div>
        <div style='font-size:2rem;margin:-14px 0 6px 0;
                    filter:drop-shadow(0 0 8px {accent});'>{mood_emoji}</div>
        <div style='font-size:1.2rem;font-weight:800;letter-spacing:0.5px;'>{username}</div>
        <div style='font-size:0.8rem;opacity:0.5;margin-top:2px;'>⚡ {xp} XP</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# TASK 5: MOOD RING BADGE
# ─────────────────────────────────────────────────────────────────────
def render_mood_ring(mood: str):
    """Renders the pulsing mood ring badge."""
    accent = MOOD_ACCENT.get(mood, "#1DB954")
    emoji  = MOOD_EMOJI.get(mood, "🎵")
    st.markdown(f"""
    <div style='text-align:center;margin:14px 0;'>
        <span class='mood-ring' style='
            background:{accent}18;
            border-color:{accent};
            color:white;'>
            <span class='mood-ring-dot' style='background:{accent};
                box-shadow:0 0 8px {accent};'></span>
            {emoji} {mood} Mode
        </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# TASK 6: FLIP ANIMATION WRAPPER FOR SONG CARDS
# ─────────────────────────────────────────────────────────────────────
def flip_card_wrap_start(index: int = 0):
    """Wraps the next song card in a flip animation container."""
    delay = index * 0.12
    st.markdown(
        f"<div class='flip-container'>"
        f"<div class='flip-card' style='animation-delay:{delay}s;'>",
        unsafe_allow_html=True)

def flip_card_wrap_end():
    """Closes the flip animation container."""
    st.markdown("</div></div>", unsafe_allow_html=True)
