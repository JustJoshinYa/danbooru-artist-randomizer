import streamlit as st
import pandas as pd
import random
import numpy as np

st.set_page_config(page_title="Danbooru Artist Randomizer", layout="wide")

# ────────────────────────────────────────
# Data Loading
# ────────────────────────────────────────
@st.cache_data
def load_artists():
    file_path = "artist.csv" 
    try:
        df = pd.read_csv(file_path, header=None, on_bad_lines="skip", encoding="utf-8")
        df = df.iloc[:, :3]
        df.columns = ['artist', 'flag', 'posts']
        df = df.dropna(subset=['artist', 'posts'])
        df['artist'] = df['artist'].astype(str).str.strip()
        df['posts'] = pd.to_numeric(df['posts'], errors='coerce').fillna(0).astype(int)
        return df[(df['artist'].str.len() >= 2) & (df['posts'] > 0)]
    except FileNotFoundError:
        return pd.DataFrame(columns=['artist', 'flag', 'posts'])

df_artists = load_artists()

# ────────────────────────────────────────
# Sidebar: Filters & Live Stats
# ────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. Popularity Filters
    st.subheader("Artist Filters")
    min_posts = st.slider("Min Posts", 10, 5000, 100, step=10)
    max_posts = st.slider("Max Posts", 100, 50000, 5000, step=100)
    
    # Apply Filters immediately for the sidebar stat
    filtered = df_artists[(df_artists['posts'] >= min_posts) & (df_artists['posts'] <= max_posts)]
    artists_list = filtered['artist'].tolist()
    posts_list = filtered['posts'].tolist()

    # 2. THE LIVE STAT (Requested Change)
    st.divider()
    st.metric(label="Artists Available", value=f"{len(filtered):,}")
    if len(filtered) == 0:
        st.error("No artists match these filters!")
    st.divider()

    # 3. Combo Settings
    st.subheader("Combo Settings")
    min_k = st.slider("Min artists per combo", 1, 10, 2)
    max_k = st.slider("Max artists per combo", min_k, 20, 6)
    num_combos = st.number_input("Number of combos", 1, 100, 10)
    
    st.divider()
    weight_by_popularity = st.checkbox("Weight by popularity", value=True)
    add_weights = st.checkbox("Add NovelAI Weights", value=False)

# ────────────────────────────────────────
# Main Area: Title & Generation
# ────────────────────────────────────────
st.title("🎨 Artist Combo Randomizer")
st.write("Adjust filters in the sidebar to update the artist pool.")

# Big Generate Button
generate_ready = not filtered.empty
if st.button("🚀 Generate Artist Combos", type="primary", disabled=not generate_ready, use_container_width=True):
    
    def generate_combo():
        k = min(random.randint(min_k, max_k), len(artists_list))
        if weight_by_popularity:
            weights = np.array(posts_list)
            prob = weights / weights.sum()
            chosen = np.random.choice(artists_list, size=k, replace=False, p=prob)
        else:
            chosen = random.sample(artists_list, k)

        if add_weights:
            return ", ".join([f"{round(random.uniform(0.5, 2.5), 1)}::{a}::" for a in chosen])
        return ", ".join(chosen)

    combos = [generate_combo() for _ in range(num_combos)]
    
    st.subheader("Generated Tags")
    for i, combo in enumerate(combos, 1):
        count = len(combo.split(', '))
        st.markdown(f"**#{i}** — {count} artists")
        st.code(combo, language="text")

    st.download_button(
        "💾 Download .txt", 
        data="\n".join(combos), 
        file_name="artist_combos.txt",
        use_container_width=True
    )

st.divider()
st.caption("Data Source: Takenoko3333/danbooru-artist Dataset")
