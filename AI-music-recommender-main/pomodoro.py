import streamlit as st
import time

def render_pomodoro():
    """Real working Pomodoro countdown timer with sleep timer."""

    for key, val in [('pomo_active', False), ('pomo_end_time', 0),
                     ('pomo_duration', 25*60), ('pomo_completed', 0),
                     ('sleep_active', False), ('sleep_end_time', 0)]:
        if key not in st.session_state:
            st.session_state[key] = val

    with st.expander("⏱️ Pomodoro & Sleep Timer", expanded=st.session_state.pomo_active or st.session_state.sleep_active):
        pomo_tab, sleep_tab = st.tabs(["🍅 Pomodoro", "😴 Sleep Timer"])

        # ── Pomodoro ──
        with pomo_tab:
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                preset = st.selectbox("Preset", ["25 min Focus", "50 min Deep Work", "5 min Break", "10 min Break", "Custom"],
                                      key="pomo_preset", disabled=st.session_state.pomo_active)
                preset_map = {"25 min Focus": 25, "50 min Deep Work": 50, "5 min Break": 5, "10 min Break": 10}
                mins = st.number_input("Minutes", 1, 120, 25, disabled=st.session_state.pomo_active, key="pomo_mins") \
                    if preset == "Custom" else preset_map[preset]
            with c2:
                if not st.session_state.pomo_active:
                    if st.button("▶ Start", use_container_width=True, type="primary", key="pomo_start"):
                        st.session_state.pomo_active = True
                        st.session_state.pomo_duration = mins * 60
                        st.session_state.pomo_end_time = time.time() + mins * 60
                        st.rerun()
                else:
                    if st.button("⏹ Stop", use_container_width=True, key="pomo_stop"):
                        st.session_state.pomo_active = False
                        st.rerun()
            with c3:
                st.metric("Sessions Done", st.session_state.pomo_completed)

            if st.session_state.pomo_active:
                remaining = int(st.session_state.pomo_end_time - time.time())
                if remaining <= 0:
                    st.session_state.pomo_active = False
                    st.session_state.pomo_completed += 1
                    st.success("🎉 Session complete! Take a break.")
                    st.balloons()
                    st.rerun()
                else:
                    progress = 1 - (remaining / st.session_state.pomo_duration)
                    st.progress(progress)
                    m, s = divmod(remaining, 60)
                    st.markdown(f"<h2 style='text-align:center;color:#1DB954;font-size:3rem;'>⏳ {m:02d}:{s:02d}</h2>",
                                unsafe_allow_html=True)
                    st.info("Stay focused! 🎵")
                    time.sleep(1)
                    st.rerun()

        # ── Sleep Timer ──
        with sleep_tab:
            st.write("Music will stop after the set time.")
            s1, s2 = st.columns([2, 1])
            with s1:
                sleep_mins = st.number_input("Stop music after (minutes)", 5, 120, 30,
                                             disabled=st.session_state.sleep_active, key="sleep_mins")
            with s2:
                if not st.session_state.sleep_active:
                    if st.button("▶ Start Sleep Timer", use_container_width=True, key="sleep_start"):
                        st.session_state.sleep_active = True
                        st.session_state.sleep_end_time = time.time() + sleep_mins * 60
                        st.rerun()
                else:
                    if st.button("⏹ Cancel", use_container_width=True, key="sleep_stop"):
                        st.session_state.sleep_active = False
                        st.rerun()

            if st.session_state.sleep_active:
                remaining = int(st.session_state.sleep_end_time - time.time())
                if remaining <= 0:
                    st.session_state.sleep_active = False
                    st.warning("😴 Sleep timer ended. Time to rest!")
                    st.rerun()
                else:
                    m, s = divmod(remaining, 60)
                    st.progress(1 - remaining / (sleep_mins * 60))
                    st.markdown(f"<p style='text-align:center;color:#aaa;font-size:1.5rem;'>😴 Stopping in {m:02d}:{s:02d}</p>",
                                unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
