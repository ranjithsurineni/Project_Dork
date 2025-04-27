from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from model import DorkQueryGenerator
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from flask_migrate import Migrate
from flask import session

 # Import the chatbot pipeline
from chatbot_pipeline import ChatbotPipeline, ChatHistory




app = Flask(__name__)



app.secret_key = 'your_secret_key'  # Replace with a secure key

# PostgreSQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dork_user:securepassword@localhost:1234/project_dork'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'

migrate = Migrate(app, db)


# ------------------------ User Model ------------------------ #
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# ------------------------ Query History Model ------------------------ #
class QueryHistory(db.Model):
    __tablename__ = 'query_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query_text = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    deleted = db.Column(db.Boolean, default=False)  # New column to track soft deletion

    # Relationship to the User model
    user = db.relationship('User', backref=db.backref('queries', lazy=True))

# ------------------------ Login Manager ------------------------ #
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------------ logs ------------------------ #
class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------------ Routes ------------------------ #
# -------------------------- Home Page ------------------------ #


# Main Page
@app.route('/')
def main_page():
    return render_template('main.html')



# Documentation Page
@app.route('/documentation', methods=['GET'])
def documentation():
    return render_template('documentation.html')



# Contact Page
@app.route('/contact', methods=['GET'])
def contact():
    logged_in = current_user.is_authenticated  # Check if the user is logged in
    return render_template('contact.html', logged_in=logged_in)



# About Us Page
@app.route('/aboutus', methods=['GET'])
def aboutus():
    return render_template('aboutus.html')


# Sign Up Route --------------------------------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        # Debugging: Print the values to the console
        print(f"Username: {username}, Email: {email}, Password: {password}, Confirm Password: {confirm_password}")

        # Validate inputs
        if not username or not email or not password or not confirm_password:
            flash("All fields are required!", "error")
            return render_template('signup.html', username=username, email=email)

        # Validate passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template('signup.html', username=username, email=email)

        # Check if the email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered.", "error")
            return render_template('signup.html', username=username, email=email)

        # Hash the password before saving
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Save the user to the database
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for('signin'))

    return render_template('signup.html')

# ----------------------- Sign In Route --------------------------------------------


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    next_page = request.args.get('dashboard.html')  # Get the "next" parameter from the query string
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Authenticate the user
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)

            # Clear chat history for the session
            session['chat_history'] = []

            # Log the sign-in action
            log = Log(user_id=user.id, action="User signed in")
            db.session.add(log)
            db.session.commit()

            flash("Logged in successfully!", "success")
            # Redirect to the next page if it exists, otherwise redirect to the index page
            return redirect(next_page) if next_page else redirect(url_for('index'))

        flash("Invalid email or password.", "error")
        return render_template('signin.html', email=email, next=next_page)

    return render_template('signin.html', next=next_page)
#------------------------dashboard------------------------#

# Dashboard Page
@app.route('/dashboard')
@login_required
def dashboard():
    query_history = QueryHistory.query.filter_by(user_id=current_user.id, deleted=False).order_by(QueryHistory.created_at.desc()).all()
    return render_template("dashboard.html", 
                           query_history=query_history,
                           username=current_user.username,
                           email=current_user.email,
                           created_at=current_user.created_at.strftime("%Y-%m-%d %H:%M:%S")
                            
                           )


#-------------------------logs----------------------------

@app.route('/some_action', methods=['POST'])
@login_required
def some_action():
    # Perform the action
    log = Log(user_id=current_user.id, action="Performed some action")
    db.session.add(log)
    db.session.commit()

    flash("Action performed successfully!", "success")
    return redirect(url_for('index'))


# Index Page
@app.route('/index', methods=['GET'])
@login_required
def index():
    query_history = QueryHistory.query.filter_by(user_id=current_user.id).order_by(QueryHistory.created_at.desc()).all()
    return render_template('index.html', query_history=query_history)


# Initialize the DorkQueryGenerator
dork_generator = DorkQueryGenerator()



# Generate Dork Route
@app.route("/generate_dork", methods=["POST"])
@login_required
def generate_dork():
    user_input = request.form.get("user_input")

    if not user_input:
        error_message = "Query text cannot be empty!"
        return render_template("index.html", error=error_message)

    try:
        # Use the DorkQueryGenerator to generate the dork query
        generated_query = dork_generator.generate_dork_query(user_input)

        # Render the index.html template with the generated query
        return render_template("index.html", dork_query=generated_query)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        return render_template("index.html", error=error_message)



# Log Out Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main_page'))



# Redirect to Sign-In Page
@app.route('/try')
def try_once():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('signin', next='index'))



#-----------------------------------------

# Save Query Route
@app.route('/save_query', methods=['POST'])
@login_required
def save_query():
    data = request.get_json()  # Parse JSON data from the request
    query = data.get('query')  # Get the query text

    if not query:
        return jsonify({"error": "Query cannot be empty!"}), 400

    try:
        # Save the query to the database
        new_query = QueryHistory(user_id=current_user.id, query_text=query)
        db.session.add(new_query)
        db.session.commit()

        # Return the saved query as a JSON response
        return jsonify({
            "success": True,
            "query_id": new_query.id,
            "query_text": new_query.query_text,
            "created_at": new_query.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


#----------------------------------------

# chatbot route

@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot_response():
    """
    API endpoint to handle chatbot queries.
    Expects a JSON payload: {"query": "user question"}
    Returns a JSON response: {"query": "user question", "response": "chatbot answer"}
    """
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' field in request"}), 400

    query = data["query"]

    # Create an instance of ChatbotPipeline for the current user
    chatbot = ChatbotPipeline(user_id=current_user.id)

    # Call the chat method on the instance
    response = chatbot.chat(query)
    

    # Save the query and response to the chat_history table
    try:
        chat_entry = ChatHistory(user_id=current_user.id, query=query, response=response["response"])
        db.session.add(chat_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save chat history: {str(e)}"}), 500

    return jsonify(response)
#-------------------------------------

# Delete Query Route (Soft Delete)
@app.route('/delete_query', methods=['POST'])
@login_required
def delete_query():
    data = request.get_json()
    query_id = data.get('query_id')

    if not query_id:
        return jsonify({"success": False, "error": "Query ID is required."}), 400

    try:
        # Mark the query as deleted
        query = QueryHistory.query.filter_by(id=query_id, user_id=current_user.id).first()
        if query:
            query.deleted = True
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Query not found."}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


#-----------------------------------------



@app.route('/login/<int:user_id>')
def login(user_id):
    session['user_id'] = user_id

    # Clear chat history for the user
    chatbot = ChatbotPipeline(user_id)
    chatbot.clear_chat_history()

    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', user_id=1))  # Redirect to login if not logged in

    chatbot = ChatbotPipeline(user_id)
    return "Chatbot ready to interact!"


#-----------------------------------------

# Clear Chat History Route

@app.route('/clear_chat_history', methods=['POST'])
@login_required
def clear_chat_history():
    """
    Clears the chat history for the current session.
    """
    session['chat_history'] = []
    return jsonify({"success": True, "message": "Chat history cleared for the session."})


#-----------------------------------------

# Fetch Chat History Route

@app.route('/get_chat_history', methods=['GET'])
@login_required
def get_chat_history():
    """
    Fetches the chat history for the logged-in user.
    """
    try:
        chat_history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.created_at.asc()).all()
        history = [{"query": chat.query, "response": chat.response, "created_at": chat.created_at.strftime("%Y-%m-%d %H:%M:%S")} for chat in chat_history]
        return jsonify({"success": True, "chat_history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ------------------------ Run the Flask App ------------------------ #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)