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
    
    if (!mood || !genre) {
        showError('Please select both a mood and a genre');
        return;
    }

    // Show loading and hide other sections
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('recommendations').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');

    try {
        const response = await fetch('/get_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mood, genre })
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
        document.getElementById('loading').classList.add('hidden');
    }
}

let player;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('youtubePlayer', {
        width: '100%',
        height: '100%',
        videoId: '',
        playerVars: {
            'autoplay': 1,
            'playsinline': 1,
            'rel': 0
        }
    });
}

function showTrailer(trailerId) {
    if (!trailerId) {
        showError('Trailer not available for this movie');
        return;
    }

    const modal = document.getElementById('trailerModal');
    modal.classList.add('show');

    if (player && player.loadVideoById) {
        player.loadVideoById(trailerId);
    }
}

function closeTrailer() {
    const modal = document.getElementById('trailerModal');
    modal.classList.remove('show');
    if (player && player.stopVideo) {
        player.stopVideo();
    }
}

// Event Listeners
document.querySelector('.close-button').addEventListener('click', closeTrailer);

document.getElementById('trailerModal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('trailerModal')) {
        closeTrailer();
    }
});

function showRecommendations(movies) {
    const content = document.getElementById('recommendations-content');
    content.innerHTML = movies.map(movie => `
        <div class="movie-card" onclick="showTrailer('${movie.trailerId || ''}')" role="button" tabindex="0">
            ${movie.poster 
                ? `<img src="${movie.poster}" alt="${movie.title}" class="movie-poster">`
                : `<div class="no-poster"><i class="fas fa-film fa-3x"></i></div>`
            }
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
                ${movie.trailerId 
                    ? `<div class="trailer-hint">
                         <i class="fas fa-play-circle"></i> Click to watch trailer
                       </div>`
                    : ''
                }
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

// Add keyboard support for closing modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeTrailer();
    }
}); 