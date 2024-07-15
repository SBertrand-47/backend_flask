import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'MrMagicians645278@')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:Umwana11@localhost/HouseManagement')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', 'your_sendgrid_api_key')
    SERVER_NAME = os.getenv('SERVER_NAME', 'localhost:5000')  # Replace with your actual server name or domain
