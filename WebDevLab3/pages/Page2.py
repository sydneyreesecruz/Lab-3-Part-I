#Page 2
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time, requests

CLIENT_ID = "d3ea9e806b19499d84797f544a112140"
CLIENT_SECRET = "a0d20c154a80451bb7bc2431365b5b8a"

TOKEN_URL = "https://accounts.spotify.com/api/token"
BASE = "https://api.spotify.com/v1"

_token = {"access": None, "exp": 0}

def _get_token():
    now = time.time()
    if _token["access"] and _token["exp"] > now:
        return _token["access"]
    r = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=15
    )
    r.raise_for_status()
    data = r.json()
    _token["access"] = data["access_token"]
    _token["exp"] = now + data["expires_in"] - 30
    return _token["access"]

def _headers():
    return {"Authorization": f"Bearer {_get_token()}"}

def search_artist(name, limit=1):
    r = requests.get(
        f"{BASE}/search",
        headers=_headers(),
        params={"q": name, "type": "artist", "limit": limit},
        timeout=15
    )
    r.raise_for_status()
    return r.json()["artists"]["items"]

def artist_top_tracks(artist_id, market="US"):
    r = requests.get(
        f"{BASE}/artists/{artist_id}/top-tracks",
        headers=_headers(),
        params={"market": market},
        timeout=15
    )
    r.raise_for_status()
    return r.json()["tracks"]

#User can choose songs from favorite artists 

st.title("How many top streamed songs do you like?")
st.header("Choose your top artist (Up to 3)")

if "fav_songs" not in st.session_state:
    st.session_state["fav_songs"] = {} 

artist_name = st.text_input("Enter an artist name").strip()

if artist_name:
    artists = search_artist(artist_name, limit=1)
    if artists:
        artist = artists[0]
        top_tracks = artist_top_tracks(artist["id"])
        track_names = [t["name"] for t in top_tracks]

        st.write(f"**Top tracks for {artist['name']}:**")
        selected = st.multiselect(
            "Pick up to 5 favorite songs",
            options=track_names,
            max_selections=5
        )

        if st.button("Add to favorites"):
            st.session_state["fav_songs"][artist['name']] = selected
            st.success(f"Added {len(selected)} song(s) for {artist['name']}")
    else:
        st.warning("No artist found.")
else:
    st.info("Type an artist name to begin.")
    
if st.session_state["fav_songs"]:
    st.subheader("Current favorites")
    for artist, songs in st.session_state["fav_songs"].items():
        st.write(f"- **{artist}**: {len(songs)} songs")

    df = pd.DataFrame([
        {"Artist": a, "Count": len(s)} for a, s in st.session_state["fav_songs"].items()
    ])
    fig, ax = plt.subplots()
    colors = ["lightcoral", "skyblue", "lightgreen", "plum", "gold"]
    ax.bar(df["Artist"], df["Count"], color=colors[:len(df)])
    ax.set_ylabel("# Favorite Songs")
    st.pyplot(fig)

#Chart of songs user chose

st.subheader("Songs You Chose")

rows = []
for artist in sorted(st.session_state["fav_songs"].keys()):
    songs = st.session_state["fav_songs"][artist]
    if not songs:
        rows.append({"Artist": artist, "Song": "(no songs selected)"})
        continue
    rows.append({"Artist": artist, "Song": songs[0]})
    for s in songs[1:]:
        rows.append({"Artist": "", "Song": s})

df_songs = pd.DataFrame(rows, columns=["Artist", "Song"])
if df_songs.empty:
    st.info("No songs added yet.")
else:
    st.dataframe(df_songs, hide_index=True)
