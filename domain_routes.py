from flask import jsonify, request
import requests
from app import app
from datetime import datetime
from app import db
from config import Config
from models import Domains
from user_routes import auth
import xml.etree.ElementTree as ET


@app.route('/add_domain', methods=['POST'])
@auth.login_required  
def add_domain():
    current_user = auth.current_user()
    data = request.json
    domain_name = data.get('domain_name')
    price =  data['price']
    expiry_date = data.get('expiry_date')
    registration_date = data.get('registration_date')
    status = data.get('status')
    # check if a value is input
    if domain_name is None or  price is None or registration_date is None or status is None:
        return jsonify({'done': False, 'message': 'All fields are required'}), 404
    
    ex_date = datetime.strptime(expiry_date, "%Y-%m-%d")
    
    new_domain = Domains(domain_name=domain_name, price=price, expiry_date=ex_date, status=status, user_id=current_user.id)
    db.session.add(new_domain)
    db.session.commit()
    return jsonify({'done': True , 'message': 'Domain name registered successfully.'}), 200

# get list of domains
@app.route('/')
@auth.login_required  
def list_domains():
    domains = Domains.query.all()
    amount_of_domains = Domains.query.count()
    all_domains = []
    for item in domains:
        domain_data = {
            "id": item.id,
            "domain_name": item.domain_name,
            "reg_date": item.registration_date,
            # "expiry_date": item.expiry_date,
            "price": item.price,
            "status": item.status
            
        }
        all_domains.append(domain_data)
    return jsonify({'Total': amount_of_domains, 'domains': all_domains})

# if you want to get domain info with id
@app.route('/<int:id>')
@auth.login_required  
def get_domain(id):
    domain = Domains.query.filter(Domains.id == id).first()
    
    if domain is None:
        return jsonify({'error': 'Not found'}), 404
    
    domain_data = {
        "id": domain.id,
        "domain_name": domain.domain_name,
        "reg_date": domain.registration_date,
        "price": domain.price,
        "status": domain.status
        
    }
    return jsonify(domain_data)

@app.route('/<domain_name>', methods=['PUT'])
@auth.login_required  
def update_domain(domain_name):
    domain = Domains.query.filter(Domains.domain_name == domain_name).one_or_404()
    data = request.json
    domain.price = data.get('price') or domain.price
    domain.status = data.get('status') or domain.status
    
    new_date = data.get('ex_date') 
    if new_date is not None:
        domain.expiry_date = datetime.strftime(new_date, "%Y-%m-%d")
        
    db.session.commit()
    return jsonify({'done' : True, 'message': f'{domain_name} updated successfully'})

@app.route('/<did>', methods=['DELETE'])
@auth.login_required  
def delete_domain(did):
    domain = Domains.query.filter(Domains.id == did).first()
    if domain is None:
        return jsonify({'error': 'Domain name does not exist'}), 404
    db.session.delete(domain)
    db.session.commit()
    return jsonify({'done': True, 'message': f'{domain.domain_name} deleted successfully!'})



# check actual domain
@app.route('/check_domain', methods=['POST'])
def checking_domain():
    domain_name = request.json.get('domain_name')
    try:
        price = check_domain(domain_name)
        if price is None:
            return jsonify({'error': 'Domain name is not available'}), 400
        else:
            return jsonify({'done':True, 'message': 'Domain name is available.', 'price': price}), 200
    except Exception as e:
        return jsonify({'error': str(e)})
    
def check_domain(domain:str):
    check_link = ('https://www.namesilo.com/api/checkRegisterAvailability?''version=1&type=xml&key={}&domains={}'.format(Config.NAMESILO_KEY, domain))
    
    response = requests.request("GET", check_link, headers={}, data={})
    root = ET.fromstring(response.content)
    res_domains = root.findall('reply/available/domain')
    
    if not res_domains:
        print(f'{domain} Not available')
        return None
    if res_domains[0].text == domain:
        price = res_domains[0].get('price')
        print(f'{domain}- Available ${price}')
        return price