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
from kivy.uix.image import Image
import random
import string
import mysql.connector
from datetime import datetime
from status import StatusScreen  # Import the StatusScreen
from reportHistory import ReportHistory

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

# Submitting the report data
class DataHandler:
    def __init__(self, app):
        self.app = app

    def submit_data(self, screen_name):
        screen_report = self.app.root.get_screen(screen_name)

        reportInitial = random.randint(10, 999)
        reportID = str(reportInitial)
        title = screen_report.ids.title.text
        incident_type = screen_report.ids.choice1.text
        image_path = screen_report.ids.imagepath.text
        details = screen_report.ids.details.text
        urgency = screen_report.ids.urgency.text
        status = "Pending"
        date_created = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO report (reportID, title, checklist, image_path, details, urgency, status, dateCreated, ProfileID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (reportID, title, incident_type, image_path, details, urgency, status, date_created,self.app.current_user['user_id'])
        )
        db.commit()

        # Clear the text fields
        screen_report.ids.title.text = ""
        screen_report.ids.choice1.text = ""
        screen_report.ids.imagepath.text = ""
        screen_report.ids.details.text = ""
        screen_report.ids.urgency.text = ""
    
    def submit_sos(self):
        
        reportInitial = random.randint(10, 999)
        reportID = str(reportInitial)
        title = "SOS"
        incident_type = "NONE"
        image_path = "NONE"
        details = "NONE"
        urgency = "HIGH"
        status = "Pending"
        date_created = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute(
            "INSERT INTO report (reportID, title, checklist, image_path, details, urgency, status, dateCreated, ProfileID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (reportID, title, incident_type, image_path, details, urgency, status, date_created,self.app.current_user['user_id'])
        )
        db.commit()
    
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
        self.data_handler = DataHandler(self)

        self.screen_manager = MDScreenManager()
        # Login Screens
        self.screen_manager.add_widget(Builder.load_file("Screens\\LoginScreen\\login.kv"))
        homescreen_enforcer = Builder.load_file("Screens\\Enforcer_Screens\\homescreen_enforcer.kv") # Load the screen from KV file and assign a name
        self.screen_manager.add_widget(homescreen_enforcer)
        
        self.screen_manager.add_widget(Builder.load_file("Screens\\LoginScreen\\signup.kv"))
        self.screen_manager.add_widget(Builder.load_file("Screens\\LoginScreen\\main.kv"))
        homescreen_enforcer.name = 'homescreen_enforcer' # Assign a name to the screen
        

        # For Users
        self.screen_manager.add_widget(Builder.load_file("Screens\\User_Screens\\homescreen.kv"))
        self.screen_manager.add_widget(Builder.load_file("Screens\\User_Screens\\screenreport.kv"))
        
        # For Enforcers
        self.screen_manager.add_widget(Builder.load_file("Screens\\Enforcer_Screens\\enforcer_screen_report.kv"))
        self.screen_manager.add_widget(Builder.load_file("Screens\\Enforcer_Screens\\enforcer_report_history.kv"))


        # For Admins
        self.screen_manager.add_widget(Builder.load_file("Screens\\Admin_Screens\\homescreen_admin.kv"))

        return self.screen_manager
    
    
    # Used to transition screen coming from other py file(status update of enforcer)
    def add_enforcer_status_screen(self):
        if not hasattr(self, 'status_screen'):
            self.status_screen = StatusScreen(name='status_screen')
            self.screen_manager.add_widget(self.status_screen)
        self.screen_manager.current = 'status_screen'
    
    # Used to transition screen coming from other py file(view past reports of logged in users)
    def add_user_report_history_screen(self):
        if not hasattr(self, 'report_history'):
            self.report_history = ReportHistory(name='report_history')
            self.screen_manager.add_widget(self.report_history)
        # Pass the user_id to the ReportHistory instance
        self.report_history.user_id = self.current_user['user_id']
        self.screen_manager.current = 'report_history'
    
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
        
        accountType = "Pending"
        try:
            # Insert the new user's data into the database
            cursor.execute(
                "INSERT INTO UserProfiles (ProfileID, UserName, Email, Birthdate, UserPassword, CreditScore, AccountType) "
                "VALUES (%s, %s, %s, %s, %s, 100, %s)",
                (user_id, name, email, formatted_birthdate, password, accountType)
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
                self.update_username_label()
                self.screen_manager.current = 'homescreen'
                toast(f"Login successful! Welcome, {self.current_user['name']}.")

                # call credit score function
                self.display_credit_score_image(self.current_user['user_id'])
            else:
                toast("User not found or incorrect password!")
        except mysql.connector.Error as err:
            print("Error: ", err)
            toast("An error occurred during login.")
        finally:
            cursor.close()
            conn.close()
    
    # dynamically change the username
    def update_username_label(self):
        # Assuming 'homescreen' is the name of your screen with the username label
        homescreen = self.screen_manager.get_screen('homescreen')
        # Update the label's text with the current user's name
        # Ensure you have an id for your MDLabel like id: username_label
        homescreen.ids.currentUser.text = self.current_user['name']
        
    # Reporting functions
    def show_incident_type_dropdown(self, caller):
        incident_types = ["Medical Emergency", "Natural Disaster", "Security Threat", "Others"]
        self.dropdown_handler.show_custom_dropdown(caller, incident_types)

    def show_urgency_dropdown(self, caller):
        urgency_levels = ["Low", "Medium", "High"]
        self.dropdown_handler.show_custom_dropdown(caller, urgency_levels)

    # submit function 
    def change_screen_and_submit(self, new_screen_name):
        # Call the submit_data method before changing the screen
        self.data_handler.submit_data('screenreport')  # Pass the screen name from which data will be submitted
        # Change the screen after submitting the data
        self.screen_manager.current = new_screen_name
    
    #submit sos
    def submitSos(self):
        self.data_handler.submit_sos()
        
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

    def get_credit_score_color(self, score):
        if score >= 81:
            return (0, 128/255, 55/255, 1)  # Green for excellent scores
        elif score >= 61:
            return (126/255, 217/255, 87/255, 1)  # Darker green for good scores
        elif score >= 41:
            return (237/255, 183/255, 0, 1)  # Yellow for fair scores
        elif score >= 21:
            return (255/255, 118/255, 67/255, 1)  # Orange for poor scores
        else:
            return (231/255, 0, 51/255, 1)  # Red for very poor scores

    # Displaying Credit score
    def display_credit_score_image(self, user_id):
        # Fetch the user's credit score from the database
        print(f"Hello {user_id}!")
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT CreditScore FROM UserProfiles WHERE ProfileID = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                credit_score = result[0]
            else:
                print(f"No credit score found for user_id: {user_id}")
                return
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return
        finally:
            cursor.close()
            conn.close()

        # Determine the appropriate image path based on the credit score
        if 81 <= credit_score:
            selected_image_path = 'Screens\\Assets\\Excellent.png'
        elif 61 <= credit_score <= 80:
            selected_image_path = 'Screens\\Assets\\Good.png'
        elif 41 <= credit_score <= 60:
            selected_image_path = 'Screens\\Assets\\Fair.png'
        elif 21 <= credit_score <= 40:
            selected_image_path = 'Screens\\Assets\\Poor.png'
        elif 1 <= credit_score <= 20:
            selected_image_path = 'Screens\\Assets\\VeryPoor.png'
        else:
            selected_image_path = 'Screens\\Assets\\Fair.png'  # Provide a default image for unexpected cases

        # Add the image to the BoxLayout with id 'image_container'
        homescreen = self.screen_manager.get_screen('homescreen')
        image_container = homescreen.ids.image_container
        credit_score_label = homescreen.ids.credit_score_label  # Get the label object
        # Determine the color based on the credit score
        credit_score_color = self.get_credit_score_color(credit_score)
        credit_score_label.color = credit_score_color

        image_container.clear_widgets()
        image_container.add_widget(Image(source=selected_image_path))
        credit_score_label.text = f"Trustiness: {credit_score}"  # Update the label's text

if __name__ == "__main__":
    LabelBase.register(name="MPoppins", fn_regular="Screens\\Assets\\Poppins\\Poppins-Medium.ttf")
    LabelBase.register(name="BPoppins", fn_regular="Screens\\Assets\\Poppins\\Poppins-SemiBold.ttf")

    MyApp().run()
