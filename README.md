# CineÉtincelle
A dating application based on movie preferences

CineÉtincelle is a proof-of-concept dating application that matches users based on their movie preferences. It uses cosine similarity to recommend users with similar tastes and suggests potential matches accordingly.

## Dataset Used
This project utilizes movie metadata from https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata?resource=download

## Technology Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite
- **Machine Learning**: scikit-learn (for cosine similarity)
- **Movie Data**: TMDB 5000 Movies Dataset

## Features
- **User Profiles**: Users can create a profile with their name, age, gender, and a profile picture.
- **Movie Swiping**: Users can swipe through a catalog of movies (hardcoded for simplicity, could be made dynamic) and like or dislike them.
- **Movie Recommendations**: Based on liked movies, the system recommends similar movies using cosine similarity.
- **User Matching**: Users with similar movie preferences are matched based on a calculated match score.
- **Admin Tool**: A basic admin tool is available for managing user profiles and preferences.

## How to Run
### Prerequisites
Ensure you have Python installed along with the necessary dependencies:flask ,pandas ,numpy ,scikit-learn

### Run the Backend:-app.py
The backend server will start on `http://127.0.0.1:5000/`.

### Run the Frontend:
Open `index.html` in a browser to interact with the application.

### If you want to manage user profiles, run:-admin_tool.py

This gives you options to:
- View all profiles
- View specific profiles
- Delete profiles

## 
- **This is a starting point but needs refinement for real-world use.The matching logic in JS needs far more sophistication and improvement.**
- **The movie selection for swiping is currently hardcoded and should be dynamically fetched.**
- **SQLite is used for ease of integration with Python but is not ideal.**
- **Profile pictures are stored in an `uploads` folder as SQLite cannot handle image storage.**

 ## output:
![1](https://github.com/user-attachments/assets/e2b3eb71-a28a-4f21-a2c0-12d4891aaf73)
![2](https://github.com/user-attachments/assets/62a1f716-bc38-4517-b9a7-59771550da3d)
![3](https://github.com/user-attachments/assets/3c80ea0f-f9f4-40c7-bed2-b85306f49c25)
![4](https://github.com/user-attachments/assets/54a56f7c-cf1a-4151-a335-f27efcb658a1)
![5](https://github.com/user-attachments/assets/22ed9fcd-19a1-4313-ba93-3990ee07da65)



 



