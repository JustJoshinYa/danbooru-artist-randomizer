import streamlit as st
import pandas as pd
import random

st.title("Danbooru Artist Combo Randomizer")
st.write("Generate random artist tag combinations from Danbooru artists")

# ────────────────────────────────────────
# Load data from local file (faster & more reliable)
# ────────────────────────────────────────
@st.cache_data
def load_artists():
    file_path = "artist.csv"  # must be in the same folder as this app.py in your repo
    
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
    df = df[(df['artist'].str.len() >= 2) & (df['posts'] > 0)]
    
    return df

df_artists = load_artists()

st.write(f"Loaded {len(df_artists):,} artists (post counts from {df_artists['posts'].min()} to {df_artists['posts'].max()})")

# ────────────────────────────────────────
# User controls – Post count range
# ────────────────────────────────────────
st.subheader("Artist Popularity Filter")

col_min, col_max = st.columns(2)

with col_min:
    min_posts = st.slider(
        "Minimum posts",
        min_value=31,
        max_value=5000,
        value=100,
        step=25,
        key="min_posts",
        help="Artists must have at least this many posts"
    )

with col_max:
    max_posts = st.slider(
        "Maximum posts",
        min_value=31,
        max_value=5000,
        value=5000,
        step=100,
        key="max_posts",
        help="Artists must have no more than this many posts (set high to disable)"
    )

if min_posts > max_posts:
    st.warning("Minimum posts cannot be higher than maximum. Adjusting max to match min.")
    max_posts = min_posts

min_artists_combo = st.slider("Min artists in each combo", 1, 10, 2)
max_artists_combo = st.slider("Max artists in each combo", min_artists_combo, 15, 6)
num_combos = st.number_input("How many combos to generate", 1, 200, 10)

weight_by_popularity = st.checkbox("Weight selection by popularity (more posts = more likely)", value=True)
add_strength_weights = st.checkbox("Add random strength weights like (artist:1.2)", value=False)

# Filter artists
filtered = df_artists[
    (df_artists['posts'] >= min_posts) & 
    (df_artists['posts'] <= max_posts)
]

artists = filtered['artist'].tolist()
posts = filtered['posts'].tolist()

if not artists:
    st.error(f"No artists found in the selected post count range ({min_posts}–{max_posts}). Try widening the range.")
    st.stop()

st.write(f"→ {len(artists):,} artists available after filtering ({min_posts}–{max_posts} posts)")

# ────────────────────────────────────────
# Generate combo function
# ────────────────────────────────────────
def generate_combo(k: int) -> str:
    if weight_by_popularity and posts:
        chosen_idx = random.choices(range(len(artists)), weights=posts, k=k)
        chosen = [artists[i] for i in chosen_idx]
    else:
        chosen = random.sample(artists, k)

    if add_strength_weights:
        parts = [f"({a}:{round(random.uniform(1.05, 1.35), 2)})" for a in chosen]
    else:
        parts = chosen

    return ", ".join(parts)


# ────────────────────────────────────────
# Generate button & output with colored artist count
# ────────────────────────────────────────
if st.button("Generate Combos!", type="primary"):
    with st.spinner("Generating..."):
        combos = []
        for _ in range(num_combos):
            k = random.randint(min_artists_combo, max_artists_combo)
            combo = generate_combo(k)
            combos.append(combo)

    for i, combo in enumerate(combos, 1):
        artist_count = len(combo.split(", "))
        
        # Colored count + normal tags
        st.markdown(
            f'<span style="color: #6b7280; font-weight: bold;">**{i}. ({artist_count} artists)**</span>  {combo}',
            unsafe_allow_html=True
        )

    # Download option
    st.download_button(
        label="Download all combos as .txt",
        data="\n".join(combos),
        file_name="danbooru_artist_combos.txt",
        mime="text/plain"
    )

# Footer
st.markdown("---")
st.caption("Data from: huggingface.co/datasets/Takenoko3333/danbooru-artist • Local CSV for speed")
