from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import time
from database import MovieMatchDB

app = Flask(__name__)
CORS(app)

db = MovieMatchDB()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_movie_data():
    movies = pd.read_csv(r"C:\Users\kisha\OneDrive\Desktop\machine learing project\movies\tmdb_5000_movies.csv")
    credits = pd.read_csv(r"C:\Users\kisha\OneDrive\Desktop\machine learing project\movies\tmdb_5000_credits.csv")
    movies = movies.merge(credits, on='title')
    return process_movie_data(movies)

def process_movie_data(movies):
    movies = movies.copy()
    movies = movies[['id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
    
    def safe_eval(column):
        return column.apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    
    movies['genres'] = safe_eval(movies['genres'])
    movies['keywords'] = safe_eval(movies['keywords'])
    movies['cast'] = safe_eval(movies['cast'])
    movies['crew'] = safe_eval(movies['crew'])
    
    movies['genres'] = movies['genres'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    movies['keywords'] = movies['keywords'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    movies['cast'] = movies['cast'].apply(lambda x: [i['name'] for i in x[:3]] if isinstance(x, list) else [])
    movies['crew'] = movies['crew'].apply(lambda x: [i['name'] for i in x if i.get('job') == 'Director'])
    
    for feature in ['genres', 'keywords', 'cast', 'crew']:
        movies[feature] = movies[feature].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
    
    movies['overview'] = movies['overview'].fillna('')
    movies['overview'] = movies['overview'].apply(lambda x: x.split())
    movies['tags'] = movies.apply(lambda x: ' '.join(x['overview'] + x['genres'] + x['keywords'] + x['cast'] + x['crew']), axis=1)
    
    return movies[['id', 'title', 'tags']]

print("Loading movie data...")
final_movies = load_movie_data()
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(final_movies['tags']).toarray()
similarity = cosine_similarity(vectors)
print("Movie data loaded and processed!")

@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies_list = final_movies['title'].tolist()
    return jsonify({
        'movies': movies_list
    })

@app.route('/api/create_profile', methods=['POST'])
def create_profile():
    try:
        data = request.form
        name = data.get('name')
        age = int(data.get('age'))
        gender = data.get('gender')
        
        profile_pic = request.files.get('profile_picture')
        profile_pic_path = None
        
        if profile_pic:
            filename = f"{name}_{int(time.time())}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            profile_pic.save(filepath)
            profile_pic_path = filename

        user_id = db.create_user(name, age, gender, profile_pic_path)
        
        return jsonify({
            'status': 'success',
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    liked_movies = data.get('liked_movies', [])
    user_id = data.get('user_id')
    
    # Clear existing preferences for the user
    if user_id:
        db.clear_movie_preferences(user_id)
        
        # Store liked movies with score 1.0
        for movie in liked_movies:
            db.add_movie_preference(user_id, movie, 'like', similarity_score=1.0, is_liked=True)
    
    all_recommendations = []
    for movie_title in liked_movies:
        if movie_title in final_movies['title'].values:
            index = final_movies[final_movies['title'] == movie_title].index[0]
            distances = list(enumerate(similarity[index]))
            distances = sorted(distances, reverse=True, key=lambda x: x[1])
            
            for i in distances[1:6]:
                movie = final_movies.iloc[i[0]].title
                score = float(i[1])
                all_recommendations.append({
                    'title': movie,
                    'score': score,
                    'based_on': movie_title
                })
    
    # Process and store unique recommendations with highest scores
    if user_id:
        unique_recommendations = {}
        for rec in all_recommendations:
            if rec['title'] not in unique_recommendations:
                unique_recommendations[rec['title']] = rec
            elif rec['score'] > unique_recommendations[rec['title']]['score']:
                unique_recommendations[rec['title']] = rec
        
        # Store recommendations in database
        for rec in unique_recommendations.values():
            db.add_movie_preference(
                user_id, 
                rec['title'], 
                'recommendation',
                similarity_score=rec['score'],
                is_liked=False
            )
    
    other_users = []
    if user_id:
        all_users = db.get_all_users()
        for user in all_users:
            if user[0] != user_id:
                user_movies = db.get_all_user_movies(user[0])
                if user_movies:
                    match_score = calculate_match_score(user_id, user[0])
                    
                    if match_score > 0:
                        db.add_match(user_id, user[0], match_score)
                        other_users.append({
                            'name': user[1],
                            'age': user[2],
                            'gender': user[3],
                            'profile_picture': user[4],
                            'match_score': match_score,
                            'movies': [
                                {
                                    'title': movie[0],
                                    'score': movie[1],
                                    'is_liked': bool(movie[2])
                                }
                                for movie in user_movies
                            ]
                        })
    
    # Sort recommendations by score
    sorted_recommendations = sorted(
        all_recommendations,
        key=lambda x: x['score'],
        reverse=True
    )
    
    # Remove duplicates while maintaining order
    seen = set()
    unique_sorted_recommendations = []
    for rec in sorted_recommendations:
        if rec['title'] not in seen:
            unique_sorted_recommendations.append(rec)
            seen.add(rec['title'])
    
    # Sort users by match score
    other_users.sort(key=lambda x: x['match_score'], reverse=True)
    
    return jsonify({
        'recommendations': unique_sorted_recommendations[:10],
        'other_users': other_users
    })

def calculate_match_score(user_id_1, user_id_2):
    user1_movies = db.get_all_user_movies(user_id_1)
    user2_movies = db.get_all_user_movies(user_id_2)
    
    if not user1_movies or not user2_movies:
        return 0
    
    # Convert to dictionaries for easier lookup
    user1_dict = {movie[0]: (movie[1], movie[2]) for movie in user1_movies}
    user2_dict = {movie[0]: (movie[1], movie[2]) for movie in user2_movies}
    
    # Find common movies
    common_movies = set(user1_dict.keys()) & set(user2_dict.keys())
    
    if not common_movies:
        return 0
    
    total_score = 0
    for movie in common_movies:
        score1, is_liked1 = user1_dict[movie]
        score2, is_liked2 = user2_dict[movie]
        
        # If both users liked the movie, use max score
        if is_liked1 and is_liked2:
            movie_score = 1.0
        # If one user liked and other has it as recommendation
        elif is_liked1 or is_liked2:
            movie_score = max(score1, score2)
        # If both are recommendations
        else:
            movie_score = (score1 + score2) / 2
            
        total_score += movie_score
    
    # Normalize the score
    match_score = total_score / len(common_movies)
    return match_score

@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)