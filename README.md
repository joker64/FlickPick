# FlickPick Movie Recommender 🎬

FlickPick is a web application that recommends movies based on your mood and preferred genre. It uses OpenAI's GPT-3.5 for intelligent movie recommendations, TMDB for movie information and ratings, and YouTube for movie trailers.

## Features 🌟

- Mood-based movie recommendations
- Genre filtering
- Movie posters and ratings from TMDB
- Integrated YouTube trailers
- Dark/Light theme support
- Responsive design
- Local network accessibility

## Prerequisites 📋

Before you begin, ensure you have the following:

1. Python 3.7 or higher
2. API Keys for:
   - OpenAI API
   - TMDB API
   - YouTube Data API v3

## Installation 🚀

1. Clone the repository:
    git clone https://github.com/joker64/FlickPick.git
    cd FlickPick

2. Install required packages: pip install -r requirements.txt

3. Create a `.env` file in the project root with your API keys: 
    OPENAI_API_KEY=your_openai_api_key
    TMDB_API_KEY=your_tmdb_api_key
    YOUTUBE_API_KEY=your_youtube_api_key   


## Running the Application 🎯

### Windows:
1. Double-click `run_app.bat` or run it from Command Prompt as administrator
2. The script will:
   - Display your local IP address
   - Create necessary firewall rules
   - Start the Flask application

The application will be available at:
- Local access: `http://localhost:8000`
- Network access: `http://your_local_ip:8000`

## Usage 💡

1. Select your current mood from the dropdown
2. Choose your preferred movie genre
3. Click "Get Recommendations"
4. Browse through personalized movie recommendations
5. Click on any movie card to watch its trailer
6. Toggle between light and dark themes using the switch

## Project Structure 📁

── main.py # Flask application and API handlers
├── run_app.bat # Windows startup script
├── .env # API keys and configuration
├── static/
│ ├── style.css # Application styling
│ ├── script.js # Frontend JavaScript
│ └── favicon.ico # Website favicon
└── templates/
└── index.html # Main HTML template

## API Integration 🔌

- **OpenAI GPT-3.5**: Generates movie recommendations based on mood and genre
- **TMDB**: Provides movie posters, release years, and ratings
- **YouTube**: Fetches official movie trailers

## Security Notes 🔒

1. Keep your API keys secure and never commit them to version control
2. The application runs in debug mode by default - disable this in production
3. Consider adding authentication for public deployments
4. Review and update the firewall rules as needed

## Troubleshooting 🔧

1. If trailers don't play:
   - Check your YouTube API quota
   - Ensure JavaScript is enabled
   - Check browser console for errors

2. If recommendations fail:
   - Verify your API keys
   - Check your OpenAI API quota
   - Ensure proper network connectivity

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.