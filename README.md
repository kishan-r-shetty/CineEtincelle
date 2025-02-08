# CineEtincelle
A dating application based on movie preferences
CineÉtincelle is a proof-of-concept dating application that matches users based on their movie preferences. It uses cosine similarity to recommend users with similar tastes and suggests potential matches accordingly.
-----
Dataset Used:

This project utilizes movie metadata from the TMDB dataset: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata?resource=download
-----
Features:

User Profiles: Users can create a profile with their name, age, gender, and a profile picture.
Movie Swiping: Users can swipe through a catalog of movies (hardcoded for simplicity ,could be made dynamic) and like or dislike them.
Movie Recommendations: Based on liked movies, the system recommends similar movies using cosine similarity.
User Matching: Users with similar movie preferences are matched based on a calculated match score.
Admin Tool: A basic admin tool is available for managing user profiles and preferences.
-----

How to Run:

->Prerequisites:
Ensure you have Python installed along with the necessary dependencies:flask, pandas, numpy, scikit-learn

->Run the Backend:-app.py
The backend server will start on http://127.0.0.1:5000/.

->Run the Frontend:
Open index.html in a browser to interact with the application.

->If you want to manage user profiles, run:-python admin_tool.py

This gives you options to:
View all profiles
View specific profiles
Delete profiles
-----
**
-This is a starting point but needs refinement for real-world use. the matching logic in JS need far more sophistication and improvement.
-The movie selection for swiping is currently hardcoded and should be dynamically fetched.
-SQLite is used for ease of integration with Python but is not ideal
-Profile pictures are stored in an uploads folder as SQLite cannot handle image storage.
