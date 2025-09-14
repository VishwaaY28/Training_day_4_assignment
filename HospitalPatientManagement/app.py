from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity)
from datetime import datetime
from enum import Enum
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# --- Models ---

class UserRole(Enum):
    doctor = 'doctor'
    admin = 'admin'
    staff = 'staff'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    head_doctor = db.Column(db.String(100), nullable=True)
    created_on = db.Column(db.Date, default=datetime.utcnow)

    patients = db.relationship('Patient', backref='department', lazy=True)

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    disease = db.Column(db.String(100), nullable=False)
    admitted_on = db.Column(db.Date, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

# --- Helper functions ---

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_username = get_jwt_identity()
        user = User.query.filter_by(username=current_username).first()
        if not user or user.role != UserRole.admin:
            return jsonify({"msg": "Admin privilege required"}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# --- Routes ---

@app.route('/register', methods=['POST'])
@admin_required
def register():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if not username or not password or not role:
        return jsonify({"msg": "username, password and role are required"}), 400

    if role not in UserRole._value2member_map_:
        return jsonify({"msg": "Invalid role"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 409
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, role=UserRole(role))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User   registered successfully", "user_id": new_user.id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Use username as identity instead of user.id
    access_token = create_access_token(identity=user.username)
    return jsonify({"token": access_token}), 200

# --- Department APIs ---

@app.route('/departments', methods=['POST'])
@admin_required
def add_department():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    name = data.get('name')
    head_doctor = data.get('head_doctor')
    if not name or not isinstance(name, str):
        return jsonify({"msg": "Department name is required and must be a string"}), 400
    if head_doctor is not None and not isinstance(head_doctor, str):
        return jsonify({"msg": "head_doctor must be a string if provided"}), 400

    if not name:
        return jsonify({"msg": "Department name is required"}), 400

    if Department.query.filter_by(name=name).first():
        return jsonify({"msg": "Department already exists"}), 409

    new_department = Department(name=name, head_doctor=head_doctor)
    db.session.add(new_department)
    db.session.commit()

    return jsonify({"message": "Department added successfully", "department_id": new_department.id}), 201

@app.route('/departments', methods=['GET'])
@jwt_required()
def list_departments():
    departments = Department.query.all()
    result = []
    for d in departments:
        result.append({
            "id": d.id,
            "name": d.name,
            "head_doctor": d.head_doctor,
            "created_on": d.created_on.isoformat()
        })
    return jsonify(result), 200

# --- Patient APIs ---

@app.route('/patients', methods=['POST'])
@jwt_required()
def add_patient():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    name = data.get('name')
    age = data.get('age')
    disease = data.get('disease')
    admitted_on = data.get('admitted_on')
    department_id = data.get('department_id')

    if not all([name, age, disease, admitted_on, department_id]):
        return jsonify({"msg": "All patient fields are required"}), 400

    # Validate department exists
    department = Department.query.get(department_id)
    if not department:
        return jsonify({"msg": "Department not found"}), 404

    try:
        admitted_date = datetime.strptime(admitted_on, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"msg": "Invalid date format for admitted_on, use YYYY-MM-DD"}), 400

    new_patient = Patient(
        name=name,
        age=age,
        disease=disease,
        admitted_on=admitted_date,
        department_id=department_id
    )
    db.session.add(new_patient)
    db.session.commit()

    return jsonify({"message": "Patient registered successfully", "patient_id": new_patient.id}), 201

@app.route('/patients', methods=['GET'])
@jwt_required()
def list_patients():
    patients = Patient.query.all()
    result = []
    for p in patients:
        result.append({
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "disease": p.disease,
            "admitted_on": p.admitted_on.isoformat(),
            "department": p.department.name if p.department else None
        })
    return jsonify(result), 200

@app.route('/patients/disease/<string:disease>', methods=['GET'])
@jwt_required()
def filter_patients_by_disease(disease):
    patients = Patient.query.filter(Patient.disease.ilike(f'%{disease}%')).all()
    result = []
    for p in patients:
        result.append({
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "disease": p.disease,
            "admitted_on": p.admitted_on.isoformat(),
            "department": p.department.name if p.department else None
        })
    return jsonify(result), 200

@app.route('/patients/search', methods=['GET'])
@jwt_required()
def search_patients_by_name():
    name_query = request.args.get('name')
    if not name_query:
        return jsonify({"msg": "Query parameter 'name' is required"}), 400

    patients = Patient.query.filter(Patient.name.ilike(f'%{name_query}%')).all()
    result = []
    for p in patients:
        result.append({
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "disease": p.disease,
            "admitted_on": p.admitted_on.isoformat(),
            "department": p.department.name if p.department else None
        })
    return jsonify(result), 200

@app.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    name = data.get('name')
    age = data.get('age')
    disease = data.get('disease')
    admitted_on = data.get('admitted_on')
    department_id = data.get('department_id')

    if name:
        patient.name = name
    if age:
        patient.age = age
    if disease:
        patient.disease = disease
    if admitted_on:
        try:
            patient.admitted_on = datetime.strptime(admitted_on, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"msg": "Invalid date format for admitted_on, use YYYY-MM-DD"}), 400
    if department_id:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({"msg": "Department not found"}), 404
        patient.department_id = department_id

    db.session.commit()
    return jsonify({"message": "Patient updated successfully"}), 200

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": "Patient deleted successfully"}), 200

# --- Initialize DB and create admin user for testing ---

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password=generate_password_hash('1234'),
                role=UserRole.admin
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
