import streamlit as st
import pickle
import requests

## Load Data
movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movie_titles = movies_df['title'].values

PLACEHOLDER_IMG = "https://via.placeholder.com/500x750?text=No+Poster"

## Fetching Posters
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        url_main = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {
            "api_key": "TMDB_API_KEY",
            "language": "en-US"
        }
        resp_main = requests.get(url_main, params=params, timeout=5)
        if resp_main.status_code == 200:
            data_main = resp_main.json()
            poster_path = data_main.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except requests.exceptions.RequestException:
        pass

    try:
        url_images = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
        params = {"api_key": "TMDB_API_KEY"}
        resp_imgs = requests.get(url_images, params=params, timeout=5)
        if resp_imgs.status_code == 200:
            data_imgs = resp_imgs.json()
            posters_list = data_imgs.get("posters") or []
            if posters_list:
                # choose first poster in list
                first_path = posters_list[0].get("file_path")
                if first_path:
                    return f"https://image.tmdb.org/t/p/w500{first_path}"
    except requests.exceptions.RequestException:
        pass

    return PLACEHOLDER_IMG

##Recommend Movie Function: Top 5
def recommend(movie):
    idx = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[idx]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    rec_names = []
    rec_posters = []
    for i in movies_list:
        movie_id = movies_df.iloc[i[0]].movie_id
        rec_names.append(movies_df.iloc[i[0]].title)
        rec_posters.append(fetch_poster(movie_id))
    return rec_names, rec_posters

##Streamlit UI
st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox("Select a movie", movie_titles)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    st.subheader("Recommended Movies")
    cols = st.columns(5)

    for j, col in enumerate(cols):
        with col:
            st.text(names[j])
            st.image(posters[j])
else:
    st.write("👆 Select a movie and click Recommend")
