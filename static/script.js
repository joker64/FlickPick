const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');

function switchTheme(e) {
    if (e.target.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    }    
}

toggleSwitch.addEventListener('change', switchTheme);

// Check for saved theme preference
const currentTheme = localStorage.getItem('theme');
if (currentTheme) {
    document.documentElement.setAttribute('data-theme', currentTheme);
    if (currentTheme === 'dark') {
        toggleSwitch.checked = true;
    }
}

async function getRecommendations() {
    const mood = document.getElementById('mood').value;
    const genre = document.getElementById('genre').value;
    const language = document.getElementById('language').value;
    
    if (!mood || !genre) {
        showError('Please select both a mood and a genre');
        return;
    }

    // Show loading and hide other sections
    const loadingElement = document.getElementById('loading');
    const recommendationsElement = document.getElementById('recommendations');
    const errorElement = document.getElementById('error');

    loadingElement.classList.remove('hidden');
    recommendationsElement.classList.add('hidden');
    errorElement.classList.add('hidden');

    try {
        const response = await fetch('/get_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mood, genre, language })
        });

        const data = await response.json();

        if (response.ok) {
            showRecommendations(data.recommendations);
        } else {
            showError(data.error || 'Failed to get recommendations');
        }
    } catch (error) {
        showError('An error occurred while fetching recommendations');
    } finally {
        loadingElement.classList.add('hidden');
    }
}

function showTrailer(trailerId) {
    if (!trailerId) {
        showError('Trailer not available for this movie');
        return;
    }

    const modal = document.getElementById('trailerModal');
    const iframe = document.getElementById('trailerFrame');
    
    // Set the iframe source with the embedded YouTube URL
    iframe.src = `https://www.youtube.com/embed/${trailerId}?autoplay=1&rel=0`;
    
    // Show the modal
    modal.classList.add('show');
}

function closeTrailer() {
    const modal = document.getElementById('trailerModal');
    const iframe = document.getElementById('trailerFrame');
    
    // Stop the video by clearing the iframe source
    iframe.src = '';
    
    // Hide the modal
    modal.classList.remove('show');
}

// Add event listeners for closing the trailer
document.querySelector('.close-button').addEventListener('click', closeTrailer);

document.getElementById('trailerModal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('trailerModal')) {
        closeTrailer();
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeTrailer();
    }
});

function showRecommendations(movies) {
    const content = document.getElementById('recommendations-content');
    content.innerHTML = movies.map(movie => `
        <div class="movie-card" onclick="handleMovieClick('${movie.title}', '${movie.year}')" role="button" tabindex="0">
            ${movie.poster 
                ? `<img src="${movie.poster}" alt="${movie.title}" class="movie-poster">`
                : `<div class="no-poster"><i class="fas fa-film fa-3x"></i></div>`
            }
            <div class="watch-trailer-text">Watch Trailer</div>
            <div class="movie-info">
                <div class="movie-title">${movie.title}</div>
                <div class="movie-year-rating">
                    <span class="year">${movie.year}</span>
                    ${movie.rating 
                        ? `<div class="rating">
                            <i class="fas fa-star"></i>
                            <span>${movie.rating}</span>
                          </div>`
                        : ''
                    }
                </div>
                <div class="movie-description">${movie.description}</div>
                <div class="movie-reason">${movie.reason}</div>
                <div class="trailer-hint">
                    <i class="fas fa-play-circle"></i> Click to watch trailer
                </div>
            </div>
        </div>
    `).join('');
    document.getElementById('recommendations').classList.remove('hidden');
}

function showError(message) {
    const error = document.getElementById('error');
    error.textContent = message;
    error.classList.remove('hidden');
}

// Add function to handle movie card clicks
async function handleMovieClick(title, year) {
    try {
        const response = await fetch('/get_trailer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, year })
        });

        const data = await response.json();

        if (response.ok && data.trailerId) {
            showTrailer(data.trailerId);
        } else {
            showError('Trailer not available for this movie');
        }
    } catch (error) {
        showError('Error loading trailer');
        console.error('Error:', error);
    }
} 