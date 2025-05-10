import os
from flask import jsonify, request, make_response
from app import app, db
from datetime import datetime
from models import PasswordResetToken, StoredjwtToken, UploadRecord, User
from toolz import is_valid_email, random_generator, send_email
from flask_httpauth import HTTPTokenAuth
from werkzeug.utils import secure_filename

auth = HTTPTokenAuth(scheme='Bearer')

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@auth.verify_token
def verify_token(token):
    return User.verify_auth_token(token)

@app.route('/signup', methods=['POST'])
def sign_up():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    
    # check names and check length of names
    if first_name is None or len(first_name) < 2:
        return jsonify({'error': 'Please enter a valid name!'}), 400
    
    # check if email is valid
    if not is_valid_email(email):
        return jsonify({'error': 'Please enter a valid email address'}), 400
    
    # check if email is unique
    exists = User.query.filter(User.email == email).first()
    if exists is not None:
        return jsonify({'error': 'Email already exists'}), 400
    
    #check password
    if password is None or len(password) < 6:
        return jsonify({'error': 'Password is invalid, please enter 6 or more characters.'})
    
    # create user account
    new_user = User(first_name=first_name, last_name=last_name,email=email, phone=phone)
    db.session.add(new_user)
    new_user.set_password(password)
    
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'Created': 'Account successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'User signup error: {e}'}), 400
    

# Login 

@app.route('/login')

def login_user():
    email = request.json.get('email')
    password = request.json.get('password')
    
    if email is None or password is None:
        return jsonify({'error': 'Please enter a valid email and password.'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': 'Please enter a valid email address!'}), 400
    
    # find user
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({'error': 'User with this email does not exist'}), 401
    
    # validate password
    if user.check_password(password):
        # delete previous token
        saved_token = StoredjwtToken.query.filter_by(user_id=user.id).first()
        if saved_token is not None:
            db.session.delete(saved_token)
            
        # password is correct, generate jwt token
        token = user.generate_auth_token()
        new_jwt_token = StoredjwtToken(user_id=user.id, jwt_token=token)
        db.session.add(new_jwt_token)
        db.session.commit()
        return jsonify({'success': True, 'token': token}), 200
    
    return jsonify({'error': 'Invalid email or password.'})

# logout

@app.route('/logout', methods=['GET'])
@auth.login_required  
def logout():
    user = auth.current_user()
    user_id = user.id
    active_token = StoredjwtToken.query.filter_by(user_id=user_id).first()
    db.session.delete(active_token)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User logout successfully'})

# updating users
@app.route('/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.filter(User.id == id).one_or_404()
    data = request.json
    user.email = data.get('email') or user.email
    user.password = data.get('password') or user.password
    user.first_name = data.get('first_name') or user.first_name
    user.last_name = data.get('last_name') or user.last_name
    
    if user is None:
        return jsonify({'error':'user with email does not exist'}), 404
    
    if user:
        db.session.commit()
        return jsonify({'done': True, 'message': f'{user} updated successfully'}), 200
    
    
#delete users
@app.route('/<int:did>', methods=['DELETE'])
def delete_user(did):
    user = User.query.filter(User.id == did).first()
    if user is None:
        return jsonify({'error': 'User does not exit'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'done': True, 'message': f'{user.email } Account deleted successfully!'}) 
    
    
    
    
@app.route('/my-domains')
@auth.login_required  
def my_domains():
    current_user = auth.current_user()
    user_domains = current_user.domains
    domains = []
    for domain in user_domains:
        domains.append({
            "domain_name": domain.domain_name,
            "price": domain.price,
            "expiry_date": domain.expiry_date
        })
    return jsonify({"domains": domains})

# get user profile
@app.route('/profile', methods=['GET'])
@auth.login_required  
def profile():
    current_user = auth.current_user()
    return jsonify(current_user.as_dict())


@app.route('/forget-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    
    # check if email exists
    
    if email is None:
        return jsonify({'error': 'Please enter email'}), 400
    
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({'error': 'User with this email does not exist'}), 400
    
    # create a password reset token
    
    token = random_generator(8)
    reset = PasswordResetToken(token=token, user_id=user.id, used=False)
    db.session.add(reset)
    db.session.commit()
    
    # send password reset token to email
    return jsonify({'success': True, 'message': 'Password reset email sent'}), 200


# reset password

@app.route('/reset-password', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    new_password = request.json.get('new_password')
    confirm_password = request.json.get('confirm_password')
    
    if new_password is None or confirm_password != new_password:
        return jsonify({'error': 'Password does not match'}), 400
    
    if token is None:
        return jsonify({'error': 'Please enter token'}), 400
    
    reset = PasswordResetToken.query.filter_by(token=token).first()
    if reset is None:
        return jsonify({'error': 'Invalid token'}), 400
    
    if reset.used:
        return jsonify({'error': 'Token has been used already'}), 400
    
    user = User.query.filter_by(id=reset.user_id).first()
    if user is None:
        return jsonify({'error':' User not found'}), 400
    
    user.set_password(new_password)
    reset.used = True
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password reset successfully'}), 200


# upload
@app.route('/upload', methods=['POST', 'PUT'])
@auth.login_required  
def upload_image():
    user = auth.current_user()
    user_id = user.id
    picture = request.files.get('image')
    
    if picture is None or picture.filename is None:
        return jsonify({'done': True, 'message': 'No file selected'}), 400
    
    # get the name of picture
    filename = secure_filename(picture.filename)
    upload_folder = 'static/uploads'
    
    # create folder if not exists
    os.makedirs(upload_folder, exist_ok=True)
    
    file_record = UploadRecord(user_id=user_id, filename=filename)
    db.session.add(file_record)
    db.session.commit()
    # save picture
    picture.save(os.path.join(upload_folder, filename))
    return jsonify({'success': True, 'message': 'File uploaded successfully!'}), 201

# make a route to list all the file that user upload and be able to delete it
# list of pictures
@app.route('/get-upload')
@auth.login_required  
def get_list_image():
    user = auth.current_user()
    images = UploadRecord.query.filter_by(user_id=user.id).all()
    
    # check if img exist
    if images is None:
        return jsonify({'error': 'Not found'})
    
    list_image = []
    for image in images:
        list_image.append ({
            "id": image.id,
            "filename": image.filename ,
            "uploaded_at": image.uploaded_at.strftime("%Y-%m-%d")
        })
    return jsonify(list_image), 200

# delete image picture
@app.route('/image/<int:id>', methods=['DELETE'])
@auth.login_required  
def delete_file(id):
    user = auth.current_user()
    
    # find image
    image = UploadRecord.query.filter(UploadRecord.id == id).first()
    
    if not image:
        return jsonify({'error': 'image not found'})
    
    try:
        # delete file from upload and static folder
        file_path = os.path.join('static/uploads', image.filename)
        if os.path.join(file_path):
            os.remove(file_path)
        # delete the record from the database
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'File deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500


# send email

@app.route('/send-email', methods=['POST'])
# @auth.login_required  
def send_test_email():
    email = request.json.get('email')
    text = request.json.get('text')
    
    if email is None:
        return jsonify({'error': 'Please enter email'}), 400
    
    try:
        otp = random_generator()
        opt_message = f'Use this code as your Pediforte OTP: {otp}'
        
        opt_message_html = f'<h1>{opt_message}</h1>'
        subject = 'Pediforte'
        send_email(subject=subject, receiver=email, text_body=opt_message, html_body=opt_message_html)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'success': True, 'message': 'Email sent successfully' }), 200
        