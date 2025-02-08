import sqlite3
import os
from datetime import datetime

class MovieMatchDB:
    def __init__(self, db_name='movie_match.db'):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    profile_picture TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movie_preferences (
                    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    movie_title TEXT NOT NULL,
                    preference TEXT NOT NULL,
                    similarity_score REAL,
                    is_liked BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id_1 INTEGER,
                    user_id_2 INTEGER,
                    match_score REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id_1) REFERENCES users (user_id),
                    FOREIGN KEY (user_id_2) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()

    def create_user(self, name, age, gender, profile_picture=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, age, gender, profile_picture)
                VALUES (?, ?, ?, ?)
            ''', (name, age, gender, profile_picture))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id

    def get_user(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()

    def add_movie_preference(self, user_id, movie_title, preference, similarity_score=None, is_liked=False):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Check if movie preference already exists
            cursor.execute('''
                SELECT preference_id FROM movie_preferences 
                WHERE user_id = ? AND movie_title = ?
            ''', (user_id, movie_title))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing preference
                cursor.execute('''
                    UPDATE movie_preferences 
                    SET preference = ?, similarity_score = ?, is_liked = ?
                    WHERE user_id = ? AND movie_title = ?
                ''', (preference, similarity_score, is_liked, user_id, movie_title))
            else:
                # Insert new preference
                cursor.execute('''
                    INSERT INTO movie_preferences (user_id, movie_title, preference, similarity_score, is_liked)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, movie_title, preference, similarity_score, is_liked))
            
            conn.commit()

    def get_user_movie_preferences(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT movie_title, preference, similarity_score, is_liked 
                FROM movie_preferences 
                WHERE user_id = ?
                ORDER BY is_liked DESC, similarity_score DESC
            ''', (user_id,))
            return cursor.fetchall()

    def get_all_user_movies(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT movie_title, similarity_score, is_liked 
                FROM movie_preferences 
                WHERE user_id = ?
            ''', (user_id,))
            return cursor.fetchall()

    def get_all_users(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            return cursor.fetchall()

    def add_match(self, user_id_1, user_id_2, match_score):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Check if match already exists
            cursor.execute('''
                SELECT match_id FROM matches 
                WHERE (user_id_1 = ? AND user_id_2 = ?) OR (user_id_1 = ? AND user_id_2 = ?)
            ''', (user_id_1, user_id_2, user_id_2, user_id_1))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE matches 
                    SET match_score = ?
                    WHERE (user_id_1 = ? AND user_id_2 = ?) OR (user_id_1 = ? AND user_id_2 = ?)
                ''', (match_score, user_id_1, user_id_2, user_id_2, user_id_1))
            else:
                cursor.execute('''
                    INSERT INTO matches (user_id_1, user_id_2, match_score)
                    VALUES (?, ?, ?)
                ''', (user_id_1, user_id_2, match_score))
            
            conn.commit()

    def get_user_matches(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT u.*, m.match_score
                FROM users u
                JOIN matches m ON (u.user_id = m.user_id_2 AND m.user_id_1 = ?)
                    OR (u.user_id = m.user_id_1 AND m.user_id_2 = ?)
                ORDER BY m.match_score DESC
            ''', (user_id, user_id))
            return cursor.fetchall()

    def delete_user(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM matches WHERE user_id_1 = ? OR user_id_2 = ?', (user_id, user_id))
            cursor.execute('DELETE FROM movie_preferences WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit()

    def update_user(self, user_id, name=None, age=None, gender=None, profile_picture=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            update_fields = []
            values = []
            
            if name is not None:
                update_fields.append('name = ?')
                values.append(name)
            if age is not None:
                update_fields.append('age = ?')
                values.append(age)
            if gender is not None:
                update_fields.append('gender = ?')
                values.append(gender)
            if profile_picture is not None:
                update_fields.append('profile_picture = ?')
                values.append(profile_picture)
                
            if update_fields:
                values.append(user_id)
                query = f'''
                    UPDATE users 
                    SET {', '.join(update_fields)}
                    WHERE user_id = ?
                '''
                cursor.execute(query, values)
                conn.commit()

    def clear_movie_preferences(self, user_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM movie_preferences WHERE user_id = ?', (user_id,))
            conn.commit()