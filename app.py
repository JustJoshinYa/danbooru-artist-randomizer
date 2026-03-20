import streamlit as st
import pandas as pd
import random
import numpy as np

st.set_page_config(page_title="Danbooru Artist Randomizer", layout="wide")

st.title("🎨 Danbooru Artist Combo Randomizer")

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
# User UI - Filters
# ────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    min_posts = st.slider("Min Posts", 10, 5000, 100, step=10)
    max_posts = st.slider("Max Posts", 100, 50000, 5000, step=100)
    
    st.divider()
    min_k = st.slider("Min artists per combo", 1, 10, 2)
    max_k = st.slider("Max artists per combo", min_k, 20, 6)
    num_combos = st.number_input("Number of combos", 1, 100, 10)
    
    st.divider()
    weight_by_popularity = st.checkbox("Weight by popularity", value=True)
    add_weights = st.checkbox("Add NovelAI Weights", value=False)

# Apply Filters
filtered = df_artists[(df_artists['posts'] >= min_posts) & (df_artists['posts'] <= max_posts)]
artists_list = filtered['artist'].tolist()
posts_list = filtered['posts'].tolist()

# ────────────────────────────────────────
# THE "LIVE COUNT" UI
# ────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    # This gives the user that "Feedback" they liked
    if not filtered.empty:
        st.success(f"✅ **{len(filtered):,} artists** available in this range ({min_posts} to {max_posts} posts).")
    else:
        st.error("❌ No artists found. Try lowering your 'Min Posts' filter.")

with col2:
    generate_ready = not filtered.empty
    gen_btn = st.button("🚀 Generate!", type="primary", disabled=not generate_ready, use_container_width=True)

# ────────────────────────────────────────
# Logic & Display
# ────────────────────────────────────────
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

if gen_btn:
    combos = [generate_combo() for _ in range(num_combos)]
    st.divider()
    
    for i, combo in enumerate(combos, 1):
        st.markdown(f"**Combo {i}** ({len(combo.split(', '))} artists)")
        st.code(combo, language="text")

    st.download_button("💾 Download .txt", data="\n".join(combos), file_name="combos.txt")
