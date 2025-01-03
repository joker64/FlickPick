import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import requests
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client and Flask app
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
app = Flask(__name__)

# Configure for production
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = False

# TMDB and YouTube API configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

def get_movie_poster_and_rating(movie_title, year=None):
    """
    Search for a movie poster and rating using TMDB API
    """
    search_url = f"{TMDB_BASE_URL}/search/movie"
    headers = {
        "Authorization": f"Bearer {TMDB_API_KEY}",
        "accept": "application/json"
    }
    params = {
        'query': movie_title,
        'year': year
    }
    
    print(f"Searching for movie: {movie_title}")  # Debug print
    response = requests.get(search_url, headers=headers, params=params)
    print(f"Response status: {response.status_code}")  # Debug print
    
    if response.ok:
        data = response.json()
        print(f"Found {len(data.get('results', []))} results")  # Debug print
        if data['results']:
            movie = data['results'][0]
            poster_path = movie.get('poster_path')
            rating = movie.get('vote_average', 0)  # Get rating, default to 0 if not found
            return {
                'poster': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None,
                'rating': round(rating, 1)  # Round to 1 decimal place
            }
    return {'poster': None, 'rating': None}

def get_movie_trailer(movie_title, year=None):
    """
    Search for a movie trailer using YouTube API
    """
    search_query = f"{movie_title} {year if year else ''} official trailer"
    params = {
        'key': YOUTUBE_API_KEY,
        'q': search_query,
        'part': 'snippet',
        'type': 'video',
        'maxResults': 1
    }
    
    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params=params)
        if response.ok:
            data = response.json()
            if data.get('items'):
                return data['items'][0]['id']['videoId']
    except Exception as e:
        print(f"Error fetching trailer: {e}")
    return None

def get_movie_recommendations(mood, genre):
    """
    Get movie recommendations based on mood and genre using OpenAI API
    """
    prompt = f"""
    Recommend exactly 3 UNIQUE and DIFFERENT movies that match the following criteria:
    - Mood: {mood}
    - Genre: {genre}
    
    IMPORTANT: Each movie must be completely different from the others. Do not recommend sequels or movies from the same franchise.
    
    For each movie, provide the following in JSON format:
    {{
        "title": "Movie Title",
        "year": "Year",
        "description": "Brief description (1-2 sentences)",
        "reason": "Why it matches the mood and genre"
    }}
    
    Provide the response as a JSON array of exactly 3 UNIQUE movies.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a knowledgeable movie expert providing precise recommendations. Always respond with valid JSON. Never recommend the same movie twice or movies from the same franchise."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    try:
        movies = json.loads(response.choices[0].message.content)
        
        # Check for duplicates
        titles = [movie['title'].lower() for movie in movies]
        if len(titles) != len(set(titles)):
            # If duplicates found, make another API call
            return get_movie_recommendations(mood, genre)
            
        # Add poster URLs, ratings, and trailer IDs to each movie
        for movie in movies:
            movie_data = get_movie_poster_and_rating(movie['title'], movie.get('year'))
            movie['poster'] = movie_data['poster']
            movie['rating'] = movie_data['rating']
            movie['trailerId'] = get_movie_trailer(movie['title'], movie.get('year'))
        return movies
    except json.JSONDecodeError:
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_recommendations', methods=['POST'])
def recommendations():
    try:
        data = request.json
        mood = data.get('mood')
        genre = data.get('genre')
        
        if not mood or not genre:
            return jsonify({'error': 'Please provide both mood and genre'}), 400
            
        recommendations = get_movie_recommendations(mood, genre)
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Use environment variables for host and port
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
