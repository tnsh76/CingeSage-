from flask import Flask,request,render_template, request
import pickle 
import requests
import pandas as pd
from patsy import dmatrices

similarity = pickle.load(open('model\similarity.pkl','rb'))
movies = pickle.load(open('model\movies_list.pkl','rb'))

def fetch_poster(movie_name):
    """Fetches movie poster URL based on movie name."""
    # Search for movie by name in themoviedb API (replace with your API key)
    url = f"https://api.themoviedb.org/3/search/movie?api_key=18a47bf707e3040f183cf02e7090693e&query={movie_name}"
    response = requests.get(url)
    data = response.json()
    
    # Check if any results found
    if not data['results']:
        return None  # No movie found
    
    # Check if poster path is available
    poster_path = data['results'][0]['poster_path']
    if not poster_path:
        return None  # No poster path available
    
    # Assuming the first result is the desired movie
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
  """Recommends movies based on a given movie name."""
  index = movies[movies['Name'] == movie].index[0]  # Accessing index of movie name

  distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
  recommended_movies_name = []
  recommended_movies_poster = []
  for i in distances[1:9]:
    recommended_movie_name = movies.iloc[i[0]]['Name']
    recommended_movies_poster.append(fetch_poster(recommended_movie_name))
    recommended_movies_name.append(recommended_movie_name)

  return recommended_movies_name, recommended_movies_poster

def genre_recommend(genres):
    """Recommends movies based on given genres."""
    # Assuming movies DataFrame has a 'Genre' column
    indices = []
    for genre in genres:
        indices.extend(movies[movies['Genre'] == genre].index.tolist())

    distances = []
    for index in indices:
        distances.extend([(i, similarity[index][i]) for i in range(len(similarity))])

    distances = sorted(distances, reverse=True, key=lambda x: x[1])

    recommended_movies_name = []
    recommended_movies_poster = []
    for i in distances[1:9]:
        recommended_movie_name = movies.iloc[i[0]]['Name']
        recommended_movies_poster.append(fetch_poster(recommended_movie_name))
        recommended_movies_name.append(recommended_movie_name)

    return recommended_movies_name, recommended_movies_poster
app = Flask(__name__)

@app.route("/")
def login():
    return render_template('login.html')

@app.route('/movie_based.html',methods=['GET','POST'])
def movie_based():
    movie_list = movies['Name'].values
    status = False
    if request.method == 'POST':
        try:
            if request.form:
                movies_name = request.form['movies']
                recommended_movies_name, recommended_movies_poster = recommend(movies_name)
                status = True

                return render_template('movie_based.html',movies_name = recommended_movies_name, poster = recommended_movies_poster, movie_list = movie_list, status = status)

        except Exception as e:
            error = {'error':e}
            return render_template('movie_based.html',error = error, movie_list = movie_list,status = status)
    else:
        return render_template('movie_based.html',movie_list = movie_list, status = status)


@app.route('/genre_based.html', methods=['GET','POST'])
def genre_based():
    genre_list = list(movies['Genre'].unique())
    status = False
    if request.method == 'POST':
        try:
            if request.form:
                genres = request.form.getlist('genres')
                if len(genres) < 0 or len(genres) > 3:
                    raise ValueError("Please select 1 to 3 genres.")
                recommended_movies_name, recommended_movies_poster = genre_recommend(genres)
                status = True

                return render_template('genre_based.html', 
                                       genre=recommended_movies_name, 
                                       poster=recommended_movies_poster, 
                                       genre_list=genre_list, 
                                       status=status)
        except Exception as e:
            error = {'error':e}
            return render_template('genre_based.html', 
                                   error=error, 
                                   genre_list=genre_list, 
                                   status=status)
    else:
        return render_template('genre_based.html', 
                               genre_list=genre_list, 
                               status=status)


@app.route('/about_us.html')
def about_us():
     return render_template("about_us.html")

@app.route('/home_page.html')
def home():
     return render_template("home_page.html")

if __name__ == '__main__':
    app.run(debug=True)

    