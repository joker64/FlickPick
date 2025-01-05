import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client and Flask app
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
app = Flask(__name__)
CORS(app)

# Configure for production
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'efd7e5f66498ffa0c0a8b73e2bca278adef1ed84de36cd340f6d8e773f55eb61')
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = False

# API configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

def get_movie_poster_and_rating(movie_title, year=None):
    """
    Search for a movie poster and rating using TMDB API
    """
    try:
        search_url = f"{TMDB_BASE_URL}/search/movie"
        headers = {
            "Authorization": f"Bearer {TMDB_API_KEY}",
            "accept": "application/json"
        }
        params = {
            'query': movie_title,
            'year': year
        }

        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        if data.get('results'):
            movie = data['results'][0]
            poster_path = movie.get('poster_path')
            rating = movie.get('vote_average', 0)

            return {
                'poster': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None,
                'rating': round(rating, 1)
            }

        return {'poster': None, 'rating': None}

    except Exception as e:
        print(f"Error fetching movie data for {movie_title}: {str(e)}")
        return {'poster': None, 'rating': None}

def get_movie_trailer(movie_title, year=None):
    """
    Search for a movie trailer using YouTube API
    """
    try:
        search_query = f"{movie_title} {year if year else ''} official trailer"
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'key': YOUTUBE_API_KEY,
            'q': search_query,
            'part': 'snippet',
            'type': 'video',
            'maxResults': 1
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if data.get('items'):
            video_id = data['items'][0]['id']['videoId']
            return video_id

        print(f"No trailer found for: {movie_title}")
        return None

    except Exception as e:
        print(f"Error fetching trailer for {movie_title}: {str(e)}")
        return None

def get_movie_recommendations(mood, genre, language='all'):
    """
    Get movie recommendations based on mood, genre, and language using OpenAI API
    """
    try:
        language_prompt = ""
        description_language = "English"

        if language == 'en':
            language_prompt = "Only recommend English language movies."
        elif language == 'ar':
            language_prompt = "Only recommend Egyptian movies."
            description_language = "Egyptian"

        prompt = f"""
        Recommend exactly 3 UNIQUE and DIFFERENT movies that match the following criteria:
        - Mood: {mood}
        - Genre: {genre}
        {language_prompt}

        IMPORTANT:
        - Each movie must be completely different from the others. Do not recommend sequels or movies from the same franchise.
        - Provide the description and reason in {description_language} language.

        For each movie, provide the following in JSON format:
        {{
            "title": "Movie Title",
            "year": "Year",
            "description": "Brief description (1-2 sentences) in {description_language}",
            "reason": "Why it matches the mood and genre (in {description_language})"
        }}

        Provide the response as a JSON array of exactly 3 UNIQUE movies.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"""You are a knowledgeable movie expert providing precise recommendations.
                    Always respond with valid JSON."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        movies = json.loads(response.choices[0].message.content)

        # Check for duplicates
        titles = [movie['title'].lower() for movie in movies]
        if len(titles) != len(set(titles)):
            return get_movie_recommendations(mood, genre, language)

        # Add poster and rating only (no trailer)
        for movie in movies:
            movie_data = get_movie_poster_and_rating(movie['title'], movie.get('year'))
            movie['poster'] = movie_data['poster']
            movie['rating'] = movie_data['rating']

        return movies

    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
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
        language = data.get('language', 'all')

        if not mood or not genre:
            return jsonify({'error': 'Please provide both mood and genre'}), 400

        recommendations = get_movie_recommendations(mood, genre, language)
        return jsonify({'recommendations': recommendations})

    except Exception as e:
        print(f"Error in recommendations route: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add new endpoint for fetching trailers
@app.route('/get_trailer', methods=['POST'])
def get_trailer():
    try:
        data = request.json
        movie_title = data.get('title')
        movie_year = data.get('year')

        if not movie_title:
            return jsonify({'error': 'Movie title is required'}), 400

        trailer_id = get_movie_trailer(movie_title, movie_year)
        return jsonify({'trailerId': trailer_id})

    except Exception as e:
        print(f"Error fetching trailer: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
