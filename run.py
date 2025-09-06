from api import create_app
from api.models import db, User
import bcrypt

app = create_app()

@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create a test user if none exists
    if not User.query.first():
        password_hash = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            name='Test User',
            email='test@example.com',
            password_hash=password_hash,
            role='manager'
        )
        db.session.add(user)
        db.session.commit()
        print("Created test user: test@example.com / password")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)