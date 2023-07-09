from flask import session, abort
from functools import wraps

# Define a constant for the login required message
LOGIN_REQUIRED_MESSAGE = "Login is required"

# Create a class to encapsulate the OAuth 2.0 functions and attributes
class OAuth:
    def __init__(self):
        # Initialize the state and google_id as None
        self.state = None
        self.google_id = None
    
    def set_state(self, state):
        # Set the state attribute and the session state
        self.state = state
        session["state"] = state
    
    def get_state(self):
        # Get the state attribute
        return self.state
    
    def set_google_id(self, google_id):
        # Set the google_id attribute and the session google_id
        self.google_id = google_id
        session["google_id"] = google_id
    
    def get_google_id(self):
        # Get the google_id attribute
        return self.google_id
    
    def set_name(self, name):
        # Set the name attribute and the session name
        self.name = name
        session["name"] = name
    
    def get_name(self):
        # Get the name attribute
        return self.name

    def login_is_required(self, function):
        # Define a decorator function to check if the user is authorized or not
        @wraps(function)
        def wrapper(*args, **kwargs):
            if "google_id" not in session:  #authorization required
                return abort(401, LOGIN_REQUIRED_MESSAGE)
            else:
                return function(*args, **kwargs)

        return wrapper
    
    # Add any other methods for OAuth 2.0 as needed

