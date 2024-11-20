from app import create_app, db, bcrypt  # Import your Flask app, SQLAlchemy instance, and Bcrypt instance
from app.model import User  # Import the User model
from app.routes import generate_uid  # Import the generate_uid function
from datetime import datetime

def seed_users():
    """Populate the users table with sample data."""
    # Clear the existing data in the users table
    User.query.delete()
    db.session.commit()  # Commit the deletion

    print("Existing data cleared from the users table.")

    # Sample data
    users = [
        {
            "name": "Manu",
            "email": "manu@gmail.com",
            "phone": "0700111222",
            "password": "password",
            "is_admin": True
        },
        {
            "name": "Philip",
            "email": "philip@gmail.com",
            "phone": "0711222333",
            "password": "password",
            "is_admin": False
        }
    ]

    # Insert users into the database
    for user_data in users:
        # Generate a unique ID for the user
        user_uid = generate_uid()

        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(user_data["password"]).decode('utf-8')
        
        # Create a User object
        user = User(
            uid=user_uid,  # Set the generated UID
            name=user_data["name"],
            email=user_data["email"],
            phone=user_data["phone"],
            password_hash=hashed_password,
            is_admin=user_data["is_admin"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add the user to the session
        db.session.add(user)
    
    # Commit the changes to the database
    db.session.commit()
    print("Users seeded successfully!")

if __name__ == "__main__":
    # Create the app context
    app = create_app()
    with app.app_context():
        db.create_all()  # Ensure the tables are created
        seed_users()
