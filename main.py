import mysql.connector
import random
from kivy.core.text import LabelBase
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.metrics import dp
from kivymd.toast import toast
import random
import string
import mysql.connector
from datetime import datetime
from status import StatusScreen  # Import the StatusScreen

host = "sql12.freesqldatabase.com"
user = "sql12662532"
password = "viDRIhzYSq"
database = "sql12662532"

db = mysql.connector.connect(
    host = "sql12.freesqldatabase.com",
    user = "sql12662532",
    password = "viDRIhzYSq",
    database = "sql12662532",
    )

cursor = db.cursor()
Window.size = (360, 600)

class DropDownHandler:
    def show_custom_dropdown(self, caller, items):
        menu_items = self.create_menu_items(items, caller)
        self.dropdown_menu = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        self.dropdown_menu.open()

    def create_menu_items(self, options, caller):
        return [{"viewclass": "OneLineListItem",
                 "text": option,
                 "on_release": lambda x=option: self.menu_callback(x, caller)} for option in options]

    def menu_callback(self, text_item, caller):
        caller.text = text_item
        self.dropdown_menu.dismiss()
        caller.focus = False

class SuccessDialog:
    def __init__(self, app, transition_function):
        self.app = app
        self.transition_function = transition_function

    def show_success_dialog(self, transition_screen):
        self.transition_screen = transition_screen
        self.dialog = MDDialog(
            text="Successfully Submitted!",
            radius=[20, 20, 20, 20],
            size_hint=(0.7, None),
            height=dp(200)
        )
        self.dialog.ids.text.text_color = (0, 0, 0, 1)
        self.dialog.ids.text.font_name = "BPoppins"
        self.dialog.ids.text.font_size = "20sp"
        self.dialog.ids.text.halign = "center"
        self.dialog.ids.text.valign = "center"
        self.dialog.open()
        Clock.schedule_once(self.dismiss_dialog, 2)

    def dismiss_dialog(self, dt):
        self.dialog.dismiss()
        # Schedule the transition to the home screen to happen after a short delay
        Clock.schedule_once(self.transition_function, 0.5)

    # def transition_to_home(self, dt):
        # self.root.current = self.transition_screen

class MyApp(MDApp):
    dropdown_handler = DropDownHandler()

    def build(self):
        self.success_dialog_user = SuccessDialog(self, self.transition_to_user_home)
        self.success_dialog_enforcer = SuccessDialog(self, self.transition_to_enforcer_home)

        self.screen_manager = MDScreenManager()
        
        homescreen_enforcer = Builder.load_file("Screens\\Enforcer_Screens\\homescreen_enforcer.kv") # Load the screen from KV file and assign a name
        self.screen_manager.add_widget(homescreen_enforcer)
        status_screen = StatusScreen(name='status')  #Create an instance of StatusScreen
        self.status_screen = status_screen
        self.screen_manager.add_widget(status_screen)
        homescreen_enforcer.name = 'homescreen_enforcer' # Assign a name to the screen

        # For Users
        self.screen_manager.add_widget(Builder.load_file("Screens\\User_Screens\\homescreen.kv"))
        self.screen_manager.add_widget(Builder.load_file("Screens\\User_Screens\\screenreport.kv"))
        self.screen_manager.add_widget(Builder.load_file("Screens\\User_Screens\\report_history.kv"))
        
        # For Enforcers
        self.screen_manager.add_widget(Builder.load_file("Screens\\Enforcer_Screens\\enforcer_screen_report.kv"))
        self.screen_manager.add_widget(Builder.load_file("Screens\\Enforcer_Screens\\enforcer_report_history.kv"))

        # Login Screens
        self.screen_manager.add_widget(Builder.load_file("Screens\\LoginScreen\\main.kv"))
        self.screen_manager.add_widget(Builder.load_file("Screens\\LoginScreen\\login.kv"))
        self.screen_manager.add_widget(Builder.load_file("Screens\\LoginScreen\\signup.kv"))

        # For Admins
        self.screen_manager.add_widget(Builder.load_file("Screens\\Admin_Screens\\homescreen_admin.kv"))

        return self.screen_manager

    def generate_user_id(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(10))

    def get_db_connection(self):
        return mysql.connector.connect(
            host="sql12.freesqldatabase.com",
            user="sql12662532",
            password="viDRIhzYSq",
            database="sql12662532"
        )

    def convert_date_format(self, date_string):
        try:
            date_object = datetime.strptime(date_string, '%m/%d/%Y')
            return date_object.strftime('%Y-%m-%d')
        except ValueError as e:
            print(f"Error converting date: {e}")
            return None

    def on_signup(self, name, email, password, birthdate):
        # Check if any of the fields are empty
        if not name.strip():
            toast("Please enter your name.")
            return
        if not email.strip():
            toast("Please enter your email.")
            return
        if not password:
            toast("Please enter your password.")
            return
        if not birthdate.strip():
            toast("Please enter your birthday.")
            return

        # Validate the birthday format
        try:
            # Using strptime to check if the birthday is in the correct format
            datetime.strptime(birthdate, '%m/%d/%Y')
        except ValueError:
            # If strptime raises a ValueError, it means the format is incorrect
            toast("Invalid birthday format. Please use MM/DD/YYYY.")
            return

        # If all validations pass, proceed with creating a user ID and formatting the birthdate
        user_id = self.generate_user_id()
        formatted_birthdate = datetime.strptime(birthdate, '%m/%d/%Y').date()

        # Database connection and cursor setup
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert the new user's data into the database
            cursor.execute(
                "INSERT INTO UserProfiles (ProfileID, UserName, Email, Birthdate, UserPassword, CreditScore) "
                "VALUES (%s, %s, %s, %s, %s, 100)",
                (user_id, name, email, formatted_birthdate, password)
            )
            conn.commit()
            # Inform the user of successful signup and navigate to the login screen
            toast("Signup successful! Please log in.")
            self.screen_manager.current = 'login'
        except mysql.connector.Error as err:
            print("Database error: ", err)
            toast("An error occurred during signup.")
        finally:
            cursor.close()
            conn.close()

    def on_login(self, email, password):
        conn = self.get_db_connection()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("SELECT * FROM UserProfiles WHERE Email = %s AND UserPassword = %s", (email, password))
            user = cursor.fetchone()
            if user:
                # Store user information
                self.current_user = {
                    "user_id": user[0],  # Assuming ProfileID is the first column
                    "name": user[1],     # Adjust indices based on your table structure
                    "email": user[2],
                    # ... Include other relevant details ...
                }
                self.screen_manager.current = 'homescreen'
                toast(f"Login successful! Welcome, {self.current_user['name']}.")
            else:
                toast("User not found or incorrect password!")
        except mysql.connector.Error as err:
            print("Error: ", err)
            toast("An error occurred during login.")
        finally:
            cursor.close()
            conn.close()
    
    # Reporting functions
    def show_incident_type_dropdown(self, caller):
        incident_types = ["Medical Emergency", "Natural Disaster", "Security Threat", "Others"]
        self.dropdown_handler.show_custom_dropdown(caller, incident_types)

    def show_urgency_dropdown(self, caller):
        urgency_levels = ["Low", "Medium", "High"]
        self.dropdown_handler.show_custom_dropdown(caller, urgency_levels)

    def submit_data(self):
        # Assuming 'screenreport' is the name of the screen where your 'title' widget resides
        screen_report = self.root.get_screen('screenreport')

       
        reportInitial = random.randint(10, 999)
        reportID = str(reportInitial)
        title = screen_report.ids.title.text
        incident_type = screen_report.ids.choice1.text
        image_path = screen_report.ids.imagepath.text
        details = screen_report.ids.details.text
        urgency = screen_report.ids.urgency.text
        status = "pending"
        date_created = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO report (reportID, title, checklist, image_path, details, urgency, status, dateCreated, ProfileID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (reportID, title, incident_type, image_path, details, urgency, status, date_created,self.current_user['user_id'])
        )
        db.commit()

        # Clear the text fields
        screen_report.ids.title.text = ""
        screen_report.ids.choice1.text = ""
        screen_report.ids.imagepath.text = ""
        screen_report.ids.details.text = ""
        screen_report.ids.urgency.text = ""

    def show_user_success_dialog(self, transition_screen):
        # Method to trigger the success dialog for user
        self.success_dialog_user.show_success_dialog(transition_screen)

    def show_enforcer_success_dialog(self, transition_screen):
        # Method to trigger the success dialog for enforcer
        self.success_dialog_enforcer.show_success_dialog(transition_screen)

    # For User
    def transition_to_user_home(self, dt):
        self.root.current = 'homescreen'

    # For Enforcer
    def transition_to_enforcer_home(self, dt):
        self.root.current = 'homescreen_enforcer'
        
    # Status update extended function
    def falseReport(self):
        if self.status_screen:
            self.status_screen.falseReport()

    def menu_callback(self):
        if self.status_screen:
            self.status_screen.menu_callback()

if __name__ == "__main__":
    LabelBase.register(name="MPoppins", fn_regular="Screens\\Assets\\Poppins\\Poppins-Medium.ttf")
    LabelBase.register(name="BPoppins", fn_regular="Screens\\Assets\\Poppins\\Poppins-SemiBold.ttf")

    MyApp().run()
