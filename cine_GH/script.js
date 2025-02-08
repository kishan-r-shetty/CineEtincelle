let currentUser = null;
let currentIndex = 0;
let likedMovies = [];
let recommendedMovies = new Map(); // Store recommended movies and their scores

const movies = [
    {
        title: "Spectre",
        image: "https://www.bondsuits.com/wp-content/uploads/2015/03/Spectre-Teaser-Poster-1024x767.jpg"
    },
    {
        title: "The Dark Knight",
        image: "https://upload.wikimedia.org/wikipedia/en/1/1c/The_Dark_Knight_%282008_film%29.jpg"
    },
    {
        title: "Iron Man 3",
        image: "https://static.wikia.nocookie.net/marvelcinematicuniverse/images/5/55/Iron_Man_3_IMAX_poster.jpg"
    },
    {
        title: "Pulp Fiction",
        image: "https://upload.wikimedia.org/wikipedia/en/3/3b/Pulp_Fiction_%281994%29_poster.jpg"
    },
    {
        title: "Interstellar",
        image: "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg"
    },
    {
        title: "Ratatouille",
        image: "https://upload.wikimedia.org/wikipedia/en/5/50/RatatouillePoster.jpg"
    },
    {
        title: "Inside Out",
        image: "https://upload.wikimedia.org/wikipedia/en/0/0a/Inside_Out_%282015_film%29_poster.jpg"
    },
    {
        title: "The Twilight Saga: Eclipse",
        image: "https://posters-uk.s3.eu-west-2.amazonaws.com/PRILON/10116516.jpg"
    },
    {
        title: "Deadpool",
        image: "https://upload.wikimedia.org/wikipedia/en/2/23/Deadpool_%282016_poster%29.png"
    },
    {
        title: "The Godfather",
        image: "https://upload.wikimedia.org/wikipedia/en/a/af/The_Godfather%2C_The_Game.jpg"
    }
];

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const splashScreen = document.getElementById('splash-screen');
        const mainApp = document.getElementById('main-app');
        
        splashScreen.style.opacity = '0';
        splashScreen.style.transition = 'opacity 0.5s ease';
        
        setTimeout(() => {
            splashScreen.style.display = 'none';
            mainApp.style.display = 'block';
            document.getElementById('profile-section').style.display = 'block';
        }, 500);
    }, 3000);
});

document.getElementById('profile-picture').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        const preview = document.getElementById('picture-preview');
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        
        reader.readAsDataURL(file);
    }
});

document.getElementById('profile-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('http://127.0.0.1:5000/api/create_profile', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            currentUser = {
                id: data.user_id,
                name: formData.get('name'),
                age: formData.get('age'),
                gender: formData.get('gender'),
                profilePicture: URL.createObjectURL(formData.get('profile_picture'))
            };
            
            document.getElementById('profile-section').style.display = 'none';
            document.getElementById('main-container').style.display = 'flex';
            
            updateLikedMoviesList();
            updateCurrentMovie();
        } else {
            showMessage('Error creating profile', 'red');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('Error creating profile', 'red');
    }
});

function updateLikedMoviesList() {
    const likedMoviesList = document.getElementById('liked-movies-list');
    likedMoviesList.innerHTML = likedMovies.length ? 
        likedMovies.map(movie => `
            <div class="liked-movie-item">
                <div class="recommendation-title">${movie}</div>
            </div>
        `).join('') : 
        '<p>No movies liked yet</p>';
}

async function sendLikesToBackend() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                liked_movies: likedMovies,
                user_id: currentUser.id
            })
        });
        
        const data = await response.json();
        
        // Store recommended movies
        recommendedMovies.clear();
        data.recommendations.forEach(rec => {
            recommendedMovies.set(rec.title, rec.score);
        });
        
        document.getElementById('matches-section').style.display = 'none';
        document.getElementById('recommendations-section').style.display = 'none';
        
        if (data.other_users) {
            displayMatches(data.other_users);
            setTimeout(() => {
                displayRecommendations(data.recommendations);
            }, 500);
        } else {
            displayRecommendations(data.recommendations);
        }
    } catch (error) {
        console.error('Error:', error);
        const recommendationsSection = document.getElementById('recommendations-section');
        recommendationsSection.style.display = 'block';
        recommendationsSection.innerHTML = '<div class="section-title">Recommendations</div><p>Error getting recommendations. Please try again.</p>';
    }
}

function displayRecommendations(recommendations) {
    const recommendationsSection = document.getElementById('recommendations-section');
    const recommendationsList = document.getElementById('recommendations-list');
    
    recommendationsList.innerHTML = recommendations.map(rec => `
        <div class="recommendation-item">
            <div class="recommendation-title">${rec.title}</div>
            <div class="match-score">Match Score: ${(rec.score * 100).toFixed(1)}%</div>
            <div class="based-on">Based on your like: ${rec.based_on}</div>
        </div>
    `).join('');

    recommendationsSection.style.display = 'block';
}

function displayMatches(otherUsers) {
    const matchesList = document.getElementById('matches-list');
    const matchesSection = document.getElementById('matches-section');
    
    const filteredUsers = otherUsers.filter(user => {
        if (currentUser.gender === 'male' && user.gender === 'female') return true;
        if (currentUser.gender === 'female' && user.gender === 'male') return true;
        return false;
    });
    
    if (filteredUsers.length === 0) {
        matchesList.innerHTML = `
            <div class="match-item">
                <p>No matches found for your preferences!</p>
            </div>`;
    } else {
        matchesList.innerHTML = filteredUsers.map(user => {
            const commonMovies = user.movies.map(movie => movie.title);
            
            return `
                <div class="match-item">
                    <img src="http://127.0.0.1:5000/uploads/${user.profile_picture}" 
                         alt="${user.name}'s profile" 
                         class="match-profile-pic">
                    <div class="match-info">
                        <div class="match-name">${user.name} (${user.age})</div>
                        <div class="match-percentage">Match Score: ${(user.match_score * 100).toFixed(1)}%</div>
                        <div class="common-movies">
                            Common Movies: ${commonMovies.join(', ') || 'None yet'}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    matchesSection.style.display = 'block';
}

function updateCurrentMovie() {
    const card = document.getElementById('card');
    
    if (currentIndex < movies.length) {
        const movie = movies[currentIndex];
        card.innerHTML = `
            <img class="card-image" src="${movie.image}" alt="${movie.title}">
            <div class="movie-title">${movie.title}</div>
        `;
    } else {
        card.innerHTML = '<div class="movie-title">Getting recommendations...</div>';
        sendLikesToBackend();
    }
}

function showMessage(text, color) {
    const message = document.getElementById('message');
    message.textContent = text;
    message.className = `message ${color}`;
    message.style.opacity = 1;
    
    setTimeout(() => {
        message.style.opacity = 0;
    }, 2000);
}

function handleSwipe(direction) {
    const message = document.getElementById('message');
    const card = document.getElementById('card');
    
    let translateX = 0;
    let translateY = 0;
    let feedback = '';
    let feedbackColor = '';
    
    if (direction === 'right') {
        translateX = window.innerWidth + 200;
        feedback = '👍 Liked!';
        feedbackColor = 'green';
        if (currentIndex < movies.length) {
            likedMovies.push(movies[currentIndex].title);
            updateLikedMoviesList();
        }
    } else if (direction === 'left') {
        translateX = -window.innerWidth - 200;
        feedback = '👎 Nope!';
        feedbackColor = 'red';
    } else {
        translateY = -window.innerHeight - 200;
        feedback = '⏭️ Skipped';
        feedbackColor = 'orange';
    }
    
    message.textContent = feedback;
    message.className = `message ${feedbackColor}`;
    message.style.opacity = 1;
    
    card.style.transform = `translate(${translateX}px, ${translateY}px)`;
    
    setTimeout(() => {
        message.style.opacity = 0;
        card.style.transition = 'none';
        card.style.transform = 'translate(0, 0)';
        currentIndex++;
        setTimeout(() => {
            card.style.transition = 'transform 0.5s ease';
            updateCurrentMovie();
        }, 50);
    }, 1000);
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') handleSwipe('right');
    else if (e.key === 'ArrowLeft') handleSwipe('left');
    else if (e.key === 'ArrowUp') handleSwipe('up');
});