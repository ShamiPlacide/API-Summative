import os
import requests
import urllib.parse
from flask import Flask, request, redirect, session, render_template_string
import secrets
from collections import Counter

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

# Spotify API credentials
SPOTIFY_CLIENT_ID = '64e7c8f8ad2c4064a75382ad1beae61e'
SPOTIFY_CLIENT_SECRET = 'ac81d33d4e884fab89cded23a53911f0'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8080/callback'

# Spotify API endpoints
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1'

# Required scopes for accessing user data
SCOPES = 'user-top-read user-read-recently-played'

def get_spotify_auth_url():
    """Generate Spotify authorization URL"""
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': SCOPES,
        'show_dialog': True  # Force user to approve app again
    }
    return f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"

def get_access_token(auth_code):
    """Exchange authorization code for access token"""
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=data)
    return response.json()

def make_spotify_request(endpoint, token):
    """Make authenticated request to Spotify API"""
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{SPOTIFY_API_BASE_URL}{endpoint}", headers=headers)
    return response.json()

def extract_genres_from_artists(artists_data):
    """Extract and count genres from artists data"""
    all_genres = []
    for artist in artists_data.get('items', []):
        all_genres.extend(artist.get('genres', []))

    # Count genre frequency and get top 10
    genre_counts = Counter(all_genres)
    return genre_counts.most_common(10)

# HTML Templates
LANDING_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Spotify Wrapped</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: #1a1d3a;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
        }

        .container {
            width: 80%;
            max-width: 1200px;
            height: 80vh;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 25px;
            backdrop-filter: blur(15px);
            box-shadow: 0 12px 40px rgba(31, 38, 135, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.15);
            display: flex;
            align-items: center;
        }

        .left-section {
            width: 50%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding-right: 2rem;
        }

        .right-section {
            width: 50%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            padding-left: 2rem;
        }

        .spotify-logo {
            width: 100px;
            height: 100px;
            margin-bottom: 2rem;
            filter: drop-shadow(0 4px 8px rgba(29, 185, 84, 0.3));
        }

        h1 {
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(45deg, #1DB954, #1ed760, #00d461);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 4px 8px rgba(29, 185, 84, 0.3);
        }

        p {
            font-size: 1.3rem;
            margin-bottom: 3rem;
            opacity: 0.9;
            line-height: 1.6;
        }

        .login-btn {
            background: linear-gradient(45deg, #1DB954, #1ed760);
            color: white;
            border: none;
            padding: 18px 40px;
            font-size: 1.2rem;
            border-radius: 50px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: bold;
            box-shadow: 0 6px 20px rgba(29, 185, 84, 0.3);
        }

        .login-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(29, 185, 84, 0.4);
        }

        .album-container {
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .album-cover {
            width: 200px;
            height: 200px;
            border-radius: 15px;
            position: absolute;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease;
            background-size: cover;
            background-position: center;
            border: 2px solid rgba(255, 255, 255, 0.1);
        }

        .album-cover:hover {
            transform: scale(1.05);
        }

        .album-left {
            transform: translateX(-80px) rotate(-15deg);
            z-index: 1;
            background-image: url('https://i.scdn.co/image/ab67616d0000b273e319baafd16e84f0408af2a0');
            background-size: cover;
            background-position: center;
            width: 170px;
            height: 170px;
        }

        .album-center {
            transform: translateX(0);
            z-index: 3;
            background-image: url('https://i.scdn.co/image/ab67616d0000b273f907de96b9a4fbc04accc0d5');
            background-size: cover;
            background-position: center;
            width: 220px;
            height: 220px;
        }

        .album-right {
            transform: translateX(80px) rotate(15deg);
            z-index: 2;
            background-image: url('https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36');
            background-size: cover;
            background-position: center;
            width: 170px;
            height: 170px;
        }

        .album-text {
            text-align: center;
            padding: 1rem;
        }

        @media (max-width: 768px) {
            .container {
                width: 95%;
                height: 90vh;
                flex-direction: column;
                padding: 2rem;
            }

            .left-section, .right-section {
                width: 100%;
                height: 50%;
                padding: 1rem;
            }

            h1 {
                font-size: 2.5rem;
            }

            .album-cover {
                width: 120px;
                height: 120px;
            }

            .album-left {
                transform: translateX(-40px) rotate(-15deg);
            }

            .album-right {
                transform: translateX(40px) rotate(15deg);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="left-section">
            <svg class="spotify-logo" viewBox="0 0 24 24" fill="#1DB954">
                <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.84-.179-.84-.66 0-.479.179-.66.539-.78 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.243 1.021zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z"/>
            </svg>
            <h1>Wrapify</h1>
            <p>Discover your top songs, artists, and genres from the last 30 days</p>
            <a href="{{ auth_url }}" class="login-btn">Login with Spotify</a>
        </div>

        <div class="right-section">
            <div class="album-container">
                <div class="album-cover album-left"></div>
                <div class="album-cover album-center"></div>
                <div class="album-cover album-right"></div>
            </div>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Spotify Wrapped</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: #191414;
            color: white;
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 3rem;
        }

        .header h1 {
            font-size: 3rem;
            background: linear-gradient(45deg, #1DB954, #1ed760);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }

        .header p {
            color: #b3b3b3;
            font-size: 1.1rem;
        }

        .section {
            margin-bottom: 3rem;
            background: #303030;
            border-radius: 15px;
            padding: 2rem;
        }

        .section h2 {
            color: #1DB954;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
            text-align: center;
        }


        .genres-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .genre-tag {
            background: #1DB954;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: bold;
        }

        .logout-btn {
            background: #e22134;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 2rem;
            transition: background 0.3s ease;
        }

        .logout-btn:hover {
            background: #c41e3a;
        }

        .error {
            background: #e22134;
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }

        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }

            .header h1 {
                font-size: 2rem;
            }
        }

        /* Ranked list styles for Top Songs & Top Artists */
        .ranked-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem 2rem;
        }

        .ranked-item {
            display: flex;
            align-items: center;
            background: #3f3f3f;
            padding: 1rem;
            border-radius: 10px;
            gap: 1rem;
            transition: transform 0.2s ease;
        }

        .ranked-item:hover {
            transform: translateY(-2px);
            background: #404040;
        }

        .rank-number {
            font-size: 2.2rem;
            font-weight: 900;
            color: #1DB954;
            width: 40px;
            text-align: center;
        }

        .rank-image {
            width: 60px;
            height: 60px;
            border-radius: 8px;
            object-fit: cover;
        }

        .rank-info {
            flex: 1;
        }

        .rank-name {
            font-weight: bold;
            font-size: 1rem;
            color: white;
        }

        .rank-sub {
            font-size: 0.85rem;
            color: #b3b3b3;
        }

        @media (max-width: 768px) {
            .ranked-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Spotify Wrapped</h1>
            <p>This your music taste from the last 30 days</p>
        </div>

        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}

        {% if top_tracks %}
        <div class="section">
            <h2>Your Top 10 Songs</h2>
            <div class="ranked-list">
                {% for track in top_tracks %}
                <div class="ranked-item">
                    <div class="rank-number">{{ loop.index }}</div>
                    <img src="{{ track.album.images[0].url if track.album.images else '/static/default-track.png' }}"
                         alt="{{ track.name }}" class="rank-image">
                    <div class="rank-info">
                        <div class="rank-name">{{ track.name }}</div>
                        <div class="rank-sub">{{ track.artists[0].name }}</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% if top_artists %}
        <div class="section">
            <h2>Your Top 10 Artists</h2>
            <div class="ranked-list">
                {% for artist in top_artists %}
                <div class="ranked-item">
                    <div class="rank-number">{{ loop.index }}</div>
                    <img src="{{ artist.images[0].url if artist.images else '/static/default-artist.png' }}"
                         alt="{{ artist.name }}" class="rank-image">
                    <div class="rank-info">
                        <div class="rank-name">{{ artist.name }}</div>
                        <div class="rank-sub">{{ "{:,}".format(artist.followers.total) }} followers</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% if top_genres %}
        <div class="section">
            <h2>Your Top Genres</h2>
            <div class="genres-list">
                {% for genre, count in top_genres %}
                <span class="genre-tag">{{ loop.index }}. {{ genre.title() }} ({{ count }})</span>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <div style="text-align: center;">
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Landing page with Spotify login"""
    if 'access_token' in session:
        return redirect('/dashboard')

    auth_url = get_spotify_auth_url()
    return render_template_string(LANDING_PAGE, auth_url=auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify OAuth callback"""
    auth_code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return f"Authorization failed: {error}"

    if not auth_code:
        return "No authorization code received"

    # Exchange code for access token
    token_data = get_access_token(auth_code)

    if 'access_token' in token_data:
        session['access_token'] = token_data['access_token']
        return redirect('/dashboard')
    else:
        return f"Failed to get access token: {token_data}"

@app.route('/dashboard')
def dashboard():
    """Main dashboard showing user's Spotify data"""
    if 'access_token' not in session:
        return redirect('/')

    access_token = session['access_token']

    try:
        # Fetch user's top tracks (last 30 days)
        top_tracks_data = make_spotify_request('/me/top/tracks?time_range=short_term&limit=10', access_token)

        # Fetch user's top artists (last 30 days)
        top_artists_data = make_spotify_request('/me/top/artists?time_range=short_term&limit=10', access_token)

        # Extract genres from top artists
        top_genres = extract_genres_from_artists(top_artists_data)

        return render_template_string(
            DASHBOARD_PAGE,
            top_tracks=top_tracks_data.get('items', []),
            top_artists=top_artists_data.get('items', []),
            top_genres=top_genres,
            error=None
        )

    except Exception as e:
        return render_template_string(
            DASHBOARD_PAGE,
            top_tracks=None,
            top_artists=None,
            top_genres=None,
            error=str(e)
        )

@app.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    # Check if credentials are set
    if SPOTIFY_CLIENT_ID == 'your_client_id_here' or SPOTIFY_CLIENT_SECRET == 'your_client_secret_here':
        print("\n" + "="*60)
        print("⚠️  SETUP REQUIRED!")
        print("="*60)
        print("Please update the following in the code:")
        print(f"SPOTIFY_CLIENT_ID = '{SPOTIFY_CLIENT_ID}'")
        print(f"SPOTIFY_CLIENT_SECRET = '{SPOTIFY_CLIENT_SECRET}'")
        print("\nSteps to get your credentials:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Create a new app")
        print("3. Add redirect URI: http://localhost:5000/callback")
        print("4. Copy your Client ID and Client Secret")
        print("5. Replace the values in this file")
        print("="*60)

    # For local development
    if os.environ.get('ENVIRONMENT') == 'production':
      # Docker/Production settings
      port = int(os.environ.get('PORT', 80))
      host = '0.0.0.0'
      REDIRECT_URI = "http://your-production-domain.com/callback"
    else:
      # Local development settings
      port = 8080
      host = '127.0.0.1'  # or 'localhost'
      REDIRECT_URI = "http://127.0.0.1:8080/callback"

    app.run(host=host, port=port, debug=True)
