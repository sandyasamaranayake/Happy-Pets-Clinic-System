from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required
from models import db, User
from auth.routes import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'happy_pets_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///happypets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Authentication Blueprint
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)