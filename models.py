import os
import jwt
from app import db
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class Domains(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    domain_name = db.Column(db.String(50))
    price = db.Column(db.Integer)
    registration_date = db.Column(db.DateTime, default=datetime.now)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(10))
    user = relationship("User", back_populates="domains")
    
    def __repr__(self):
        return f"<Domain {self.domain_name}>"
    
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email =  db.Column(db.String(200), unique=True)
    phone =  db.Column(db.String(20))
    password_hash =  db.Column(db.String(200))
    create = db.Column(db.DateTime, default=datetime.now)
    domains = relationship("Domains", back_populates="user")
    
    # works with getting the user profile
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self):
        expiration_time = datetime.now() + timedelta(days=10)
        payload = {
            'id' : self.id,
            'exp' : expiration_time,
            # 'role' : self.role
        }
        token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')
        return token
        
    @staticmethod
    def verify_auth_token(token):
            if not token:
                return None
            try:
                active_token = StoredjwtToken.query.filter_by(jwt_token=token).first()
                if active_token:
                    payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
                    user = User.query.get(payload['id'])
                    return user
            except jwt.ExpiredSignatureError:
                print("Token has expired ")
                return None
            except jwt.DecodeError:
                print("Token is invalid")
                return None
            
            
class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
class StoredjwtToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jwt_token = db.Column(db.String(255), unique=True, nullable=True)
    user_id = db.Column(db.Integer, nullable=True)
    
    

# upload a picture
class UploadRecord(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String)
    uploaded_at = db.Column(db.DateTime, default=datetime.now)