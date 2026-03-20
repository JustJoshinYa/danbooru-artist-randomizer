import streamlit as st
import pandas as pd
import random
import numpy as np

st.set_page_config(page_title="Danbooru Artist Randomizer", layout="wide")

st.title("🎨 Danbooru Artist Combo Randomizer")
st.write("Generate unique artist tag combinations with optional popularity weighting.")

# ────────────────────────────────────────
# Data Loading
# ────────────────────────────────────────
@st.cache_data
def load_artists():
    file_path = "artist.csv"  # Ensure this is in your project root
    try:
        df = pd.read_csv(
            file_path,
            header=None,
            on_bad_lines="skip",
            encoding="utf-8"
        )
        
        df = df.iloc[:, :3]
        df.columns = ['artist', 'flag', 'posts']
        
        df = df.dropna(subset=['artist', 'posts'])
        df['artist'] = df['artist'].astype(str).str.strip()
        df['posts'] = pd.to_numeric(df['posts'], errors='coerce').fillna(0).astype(int)
        
        # Filter out tiny accounts or empty names
        df = df[(df['artist'].str.len() >= 2) & (df['posts'] > 0)]
        return df
    except FileNotFoundError:
        st.error("CSV file not found. Please ensure 'artist.csv' is in the app folder.")
        return pd.DataFrame(columns=['artist', 'flag', 'posts'])

df_artists = load_artists()

# ────────────────────────────────────────
# User UI - Sidebar for Controls
# ────────────────────────────────────────
with st.sidebar:
    st.header("📊 Dataset Stats")
    if not df_artists.empty:
        st.write(f"Total Artists: {len(df_artists):,}")
    
    st.divider()
    st.subheader("Filter Artists")
    min_posts = st.number_input("Min Posts", 0, 100000, 100)
    max_posts = st.number_input("Max Posts", 0, 100000, 5000)
    
    st.subheader("Combo Settings")
    min_k = st.slider("Min artists per combo", 1, 10, 2)
    max_k = st.slider("Max artists per combo", min_k, 20, 6)
    num_combos = st.number_input("Number of combos", 1, 100, 10)
    
    st.divider()
    weight_by_popularity = st.checkbox("Weight by popularity", value=True, help="Artists with more posts appear more often.")
    add_weights = st.checkbox("Add NovelAI Weights", value=False, help="Adds random [0.5 to 2.5]::artist:: formatting.")

    # Filter data based on UI (moved inside sidebar to drive the green bar)
    filtered = df_artists[
        (df_artists['posts'] >= min_posts) & 
        (df_artists['posts'] <= max_posts)
    ]
    artists_list = filtered['artist'].tolist()
    posts_list = filtered['posts'].tolist()

    st.write("") # Spacer
    
    # ────────────────────────────────────────
    # THE SMALL STATUS BAR
    # ────────────────────────────────────────
    if not filtered.empty:
        st.markdown(
            f"""
            <div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; border: 1px solid #c3e6cb; font-size: 14px; text-align: center;">
                ✅ <b>{len(filtered):,}</b> artists available
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; border: 1px solid #f5c6cb; font-size: 14px; text-align: center;">
                ❌ No artists match filters
            </div>
            """,
            unsafe_allow_html=True
        )

# ────────────────────────────────────────
# Generation Logic
# ────────────────────────────────────────
def generate_combo():
    k = random.randint(min_k, max_k)
    k = min(k, len(artists_list))

    if weight_by_popularity:
        weights = np.array(posts_list)
        prob = weights / weights.sum()
        chosen = np.random.choice(artists_list, size=k, replace=False, p=prob)
    else:
        chosen = random.sample(artists_list, k)

    if add_weights:
        return ", ".join([f"{round(random.uniform(0.5, 2.5), 1)}::{a}::" for a in chosen])
    
    return ", ".join(chosen)

# ────────────────────────────────────────
# Display Results
# ────────────────────────────────────────
if not artists_list:
    st.warning("No artists found with current filters. Adjust the sidebar to continue.")
else:
    if st.button("🚀 Generate Artist Combos", type="primary", use_container_width=True):
        combos = [generate_combo() for _ in range(num_combos)]
        
        st.subheader("Your Results")
        for i, combo in enumerate(combos, 1):
            count = len(combo.split(", "))
            st.markdown(f"**Combo #{i}** ({count} artists)")
            st.code(combo, language="text")

        # Download functionality
        all_text = "\n".join(combos)
        st.download_button(
            "💾 Download as .txt",
            data=all_text,
            file_name="artist_combos.txt",
            mime="text/plain",
            use_container_width=True
        )

st.divider()
st.caption("Data Source: Takenoko3333/danbooru-artist Dataset")
