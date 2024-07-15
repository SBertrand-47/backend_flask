from flask import Flask, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

from models import db, User, Occupant, Room, House

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if not logged in


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY']) # I'll change this later
    return serializer.dumps(email, salt=current_app.config['SECRET_KEY'])


def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECRET_KEY'],
            max_age=expiration
        )
    except Exception:
        return False
    return email


def send_verification_email(user_email, token):
    verification_url = f"http://{os.environ.get('SERVER_NAME')}/verify_email/{token}"
    message = Mail(
        from_email='your_email@example.com',
        to_emails=user_email,
        subject='Email Verification',
        html_content=f'<p>Thank you for registering. Please click the link to verify your email address:</p><p><a href="{verification_url}">{verification_url}</a></p>'
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)



'''
This is simply the template of the dashboard
'''
@app.route('/')
@login_required
def home():
    return jsonify({"message": "Welcome to the Home Page", "user": current_user.username})



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "Email already registered"}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    token = generate_verification_token(email)
    send_verification_email(email, token)

    return jsonify({"message": "User registered successfully. Please check your email to verify your account."})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401


@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_verified:
        return jsonify({"message": "Please verify your email address to access this page."}), 403
    return jsonify({"message": "Welcome to your dashboard", "user": current_user.username})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})


@app.route('/edit_room', methods=['POST'])
@login_required
def edit_room():
    data = request.get_json()
    room_id = data['room_id']
    new_number = data['new_number']
    room = Room.query.get(room_id)
    if room:
        room.number = new_number
        db.session.commit()
        return jsonify({"message": "Room number updated"})
    return jsonify({"message": "Room not found"}), 404


@app.route('/adding_room', methods=['POST'])
@login_required
def adding_room():
    data = request.get_json()
    number = data['number']
    house_id = data['house_id']
    new_room = Room(number=number, house_id=house_id)
    db.session.add(new_room)
    db.session.commit()
    return jsonify({"message": "Room added successfully"})


@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data['email']
    user = User.query.filter_by(email=email).first()
    if user:
        # Implement password reset logic here
        return jsonify({"message": "Password reset email sent"})
    return jsonify({"message": "Email not found"}), 404


@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    try:
        email = confirm_verification_token(token)
    except:
        return jsonify({"message": "The confirmation link is invalid or has expired."}), 400

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        return jsonify({"message": "Account already verified."})
    else:
        user.is_verified = True
        db.session.commit()
        return jsonify({"message": "You have confirmed your account. Thanks!"})
