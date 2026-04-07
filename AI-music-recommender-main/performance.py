import streamlit as st
import pandas as pd
import functools

"""
Performance optimizations for the music recommender app
Includes caching strategies, lazy loading, and pagination utilities
"""

# ═════════════════════════════════════════════════════════════════════
#  CACHING LAYER
# ═════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_songs_dataframe(data_path="data/songs.csv"):
    """Cache the songs CSV to avoid repeated reads"""
    return pd.read_csv(data_path)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_unique_song_values(data_path="data/songs.csv"):
    """Get unique values for filters"""
    df = load_songs_dataframe(data_path)
    return {
        "moods": sorted(df["Mood"].unique().tolist()),
        "genres": sorted(df["Genre"].unique().tolist()),
        "languages": sorted(df["Language"].unique().tolist()),
        "energies": sorted(df["Energy"].unique().tolist()),
    }

# ═════════════════════════════════════════════════════════════════════
#  PAGINATION UTILITIES
# ═════════════════════════════════════════════════════════════════════

def paginate_items(items, page_size=10):
    """Create paginated view of items"""
    total_pages = (len(items) + page_size - 1) // page_size
    
    if "pagination_page" not in st.session_state:
        st.session_state.pagination_page = 1
    
    current_page = st.session_state.pagination_page
    
    if total_pages == 0:
        return [], 0
    
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    current_items = items[start_idx:end_idx]
    
    return current_items, total_pages

def render_pagination_controls(total_pages, page_key="pagination_page"):
    """Render pagination buttons"""
    if total_pages <= 1:
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.get(page_key, 1) > 1:
            if st.button("← Previous", use_container_width=True):
                st.session_state[page_key] -= 1
                st.rerun()
    
    with col2:
        st.markdown(f"<p style='text-align:center;'>Page {st.session_state.get(page_key, 1)} of {total_pages}</p>", 
                    unsafe_allow_html=True)
    
    with col3:
        if st.session_state.get(page_key, 1) < total_pages:
            if st.button("Next →", use_container_width=True):
                st.session_state[page_key] += 1
                st.rerun()

# ═════════════════════════════════════════════════════════════════════
#  LAZY LOADING UTILITIES
# ═════════════════════════════════════════════════════════════════════

def render_song_card(song, username=None, show_feedback=True):
    """Render a single song card with consistent styling"""
    song_name = song.get("Song", "Unknown")
    mood = song.get("Mood", "")
    genre = song.get("Genre", "")
    url = song.get("URL", "")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class='song-box'>
            <h4>{song_name}</h4>
            <small>{mood} • {genre}</small>
        </div>
        """, unsafe_allow_html=True)
    
    if show_feedback:
        with col2:
            if st.button("♥️", key=f"fav_{song_name}_{id(song)}", use_container_width=True):
                st.toast(f"Added {song_name} to favorites!")

def render_user_stats_mini(xp, level, streak):
    """Render mini user stats in a compact format"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Level", level)
    with col2:
        st.metric("XP", xp)
    with col3:
        st.metric("Streak", f"{streak}d")

# ═════════════════════════════════════════════════════════════════════
#  DEBOUNCING UTILITIES (for search)
# ═════════════════════════════════════════════════════════════════════

def setup_debounce_state(key, delay=500):
    """Setup debouncing for UI elements like search"""
    if f"{key}_debounce" not in st.session_state:
        st.session_state[f"{key}_debounce"] = None
