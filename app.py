from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required
from models import db, User
from auth.routes import auth_bp
from ai_assistant import ai_bp  # Dilshan - AI Care Assistant (HP-9, HP-10)

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

# Register AI Care Assistant Blueprint
app.register_blueprint(ai_bp)

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



    from werkzeug.security import generate_password_hash
from models import db, User

with app.app_context():
    db.create_all()
    
    # 1. Doctor Account
    if not User.query.filter_by(email='doctor@clinic.com').first():
        doc = User(
            username='Dr. Udayakantha',
            email='doctor@clinic.com',
            password=generate_password_hash('1234'),
            role='Doctor'
        )
        db.session.add(doc)
        
    # 2. Staff Account
    if not User.query.filter_by(email='staff@clinic.com').first():
        staff = User(
            username='Clinic Staff',
            email='staff@clinic.com',
            password=generate_password_hash('1234'),
            role='Staff'
        )
        db.session.add(staff)

    # 3. Pet Owner Account
    if not User.query.filter_by(email='owner@clinic.com').first():
        owner = User(
            username='Kamal Perera',
            email='owner@clinic.com',
            password=generate_password_hash('1234'),
            role='Pet Owner'
        )
        db.session.add(owner)
        
    db.session.commit()