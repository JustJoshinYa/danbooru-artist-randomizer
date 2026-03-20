import streamlit as st
import pandas as pd
import random

st.title("Danbooru Artist Combo Randomizer")
st.write("Generate random artist tag combinations (from artists with 30+ posts)")

# Load data once
@st.cache_data
def load_artists():
    url = "https://huggingface.co/datasets/Takenoko3333/danbooru-artist/raw/main/csv/artist.csv"
    df = pd.read_csv(url, header=None, on_bad_lines="skip")
    return df[0].dropna().astype(str).str.strip().tolist()

artists = load_artists()

st.write(f"Loaded {len(artists):,} artists")

# User controls
min_artists = st.slider("Min artists in combo", 1, 10, 2)
max_artists = st.slider("Max artists in combo", min_artists, 15, 6)
num_combos  = st.number_input("How many to generate", 1, 100, 10)
weight_pop  = st.checkbox("Weight by popularity (if count available)", value=True)
add_weights = st.checkbox("Add strength weights like (artist:1.2)", value=False)

if st.button("Generate Combos!"):
    combos = []
    for _ in range(num_combos):
        k = random.randint(min_artists, max_artists)
        chosen = random.sample(artists, k)  # or use weighted choices if you parse counts
        if add_weights:
            parts = [f"({a}:{round(random.uniform(1.05, 1.35), 2)})" for a in chosen]
        else:
            parts = chosen
        combos.append(", ".join(parts))
    
    for i, combo in enumerate(combos, 1):
        st.write(f"**{i}.** {combo}")