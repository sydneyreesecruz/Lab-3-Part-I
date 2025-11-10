import streamlit as st
import requests
import base64

st.set_page_config(page_title="🎵 Artist Top 5 Songs", page_icon="🎵", layout="centered")

# --- HEADER ---
st.title("🎵 Artist Top 5 Songs")
st.write("Discover the most popular songs from your favorite artist, powered by Spotify.")

# --- Spotify credentials ---
CLIENT_ID = "6aa4c0984b9149c6a1f336d847bfd1b5"
CLIENT_SECRET = "35a12792c06b4a1ca660662879ac4c51"

# --- Helper function to get token ---
def get_token(client_id, client_secret):
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(auth_url, headers=headers, data=data)
    return response.json().get("access_token")

# --- Get Spotify token ---
token = get_token(CLIENT_ID, CLIENT_SECRET)
headers = {"Authorization": f"Bearer {token}"}

# --- User input ---
with st.container():
    st.markdown("### 🔍 Search for an Artist")
    artist_name = st.text_input("Enter an artist name:", "Taylor Swift")

# --- Main content ---
if artist_name and token:
    with st.spinner("Fetching data..."):
        # Search for artist
        search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist"
        response = requests.get(search_url, headers=headers)

        if response.ok:
            data = response.json()
            if data["artists"]["items"]:
                artist = data["artists"]["items"][0]
                artist_id = artist["id"]

                # Artist section container
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if artist["images"]:
                            st.image(artist["images"][0]["url"], width=250)
                        else:
                            st.write("No artist image available.")
                    with col2:
                        st.subheader(artist["name"])
                        st.write(f"**Followers:** {artist['followers']['total']:,}")
                        st.write(f"**Genre(s):** {', '.join(artist['genres'][:3]) if artist['genres'] else 'N/A'}")

                st.divider()

                # Get top tracks
                top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
                tracks_response = requests.get(top_tracks_url, headers=headers)

                if tracks_response.ok:
                    tracks_data = tracks_response.json()["tracks"][:5]

                    with st.container():
                        st.markdown(f"### 🎶 Top 5 Songs by {artist_name}")

                        for i, track in enumerate(tracks_data, start=1):
                            release_year = track["album"]["release_date"].split("-")[0]
                            with st.container():
                                cols = st.columns([1, 4])
                                with cols[0]:
                                    if track["album"]["images"]:
                                        st.image(track["album"]["images"][0]["url"], width=60)
                                with cols[1]:
                                    st.write(f"**{i}. {track['name']}** ({release_year})")
                                    st.caption(f"Album: {track['album']['name']}")
                else:
                    st.error("Could not fetch top tracks.")
            else:
                st.error("Artist not found.")
        else:
            st.error("Failed to search for artist.")
