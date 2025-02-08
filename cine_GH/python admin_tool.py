from database import MovieMatchDB
import os

class AdminTool:
    def __init__(self):
        self.db = MovieMatchDB()
        print(f"Using database at: {os.path.abspath(self.db.db_name)}")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu(self):
        self.clear_screen()
        print("=== CineÉtincelle Database Admin Tool ===")
        print("1. View All Profiles")
        print("2. View Specific Profile")
        print("3. Delete Profile")
        print("4. Exit")
        print("=====================================")

    def display_movie_preferences(self, preferences):
        if not preferences:
            return
        
        print("\nLiked Movies:")
        for pref in preferences:
            movie_title, preference, score, is_liked = pref
            if is_liked:
                print(f"- {movie_title}")
        
        print("\nRecommended Movies:")
        for pref in preferences:
            movie_title, preference, score, is_liked = pref
            if not is_liked and score is not None:
                print(f"- {movie_title} (Score: {score:.2f})")

    def view_all_profiles(self):
        users = self.db.get_all_users()
        if not users:
            print("\nNo users found in database.")
            return

        print("\nAll Profiles:")
        print("----------------------------------------")
        for user in users:
            print(f"ID: {user[0]}")
            print(f"Name: {user[1]}")
            print(f"Age: {user[2]}")
            print(f"Gender: {user[3]}")
            print(f"Profile Picture: {user[4]}")
            print(f"Created At: {user[5]}")
            
            preferences = self.db.get_user_movie_preferences(user[0])
            self.display_movie_preferences(preferences)
            print("----------------------------------------")

    def view_specific_profile(self):
        user_id = input("\nEnter User ID: ")
        try:
            user_id = int(user_id)
            user = self.db.get_user(user_id)
            if user:
                print("\nProfile Details:")
                print("----------------------------------------")
                print(f"ID: {user[0]}")
                print(f"Name: {user[1]}")
                print(f"Age: {user[2]}")
                print(f"Gender: {user[3]}")
                print(f"Profile Picture: {user[4]}")
                print(f"Created At: {user[5]}")
                
                preferences = self.db.get_user_movie_preferences(user[0])
                self.display_movie_preferences(preferences)
                print("----------------------------------------")
            else:
                print("\nUser not found.")
        except ValueError:
            print("\nInvalid user ID.")

    def delete_profile(self):
        user_id = input("\nEnter User ID to delete: ")
        try:
            user_id = int(user_id)
            user = self.db.get_user(user_id)
            if user:
                confirm = input(f"Are you sure you want to delete {user[1]}'s profile? (y/n): ")
                if confirm.lower() == 'y':
                    if user[4]:  # profile_picture field
                        try:
                            file_path = os.path.join('uploads', user[4])
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except Exception as e:
                            print(f"Warning: Could not delete profile picture: {e}")
                    
                    self.db.delete_user(user_id)
                    print("\nProfile deleted successfully.")
                else:
                    print("\nDeletion cancelled.")
            else:
                print("\nUser not found.")
        except ValueError:
            print("\nInvalid user ID.")

    def run(self):
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                self.view_all_profiles()
            elif choice == '2':
                self.view_specific_profile()
            elif choice == '3':
                self.delete_profile()
            elif choice == '4':
                print("\nExiting admin tool...")
                break
            else:
                print("\nInvalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    admin_tool = AdminTool()
    admin_tool.run()