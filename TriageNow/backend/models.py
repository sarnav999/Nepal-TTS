from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

VALID_ROLES = ['patient', 'care_team', 'admin']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    # Core profile data
    age = db.Column(db.Integer)
    sex = db.Column(db.String(10))
    race_ethnicity = db.Column(db.String(100))
    functional_status = db.Column(db.String(100))  # NYHA, ECOG, etc.
    comorbidity_index = db.Column(db.Integer)
    clinical_tags = db.Column(db.Text)  # JSON string of tags like ["COPD", "HF"]
    medications = db.Column(db.Text)
    med_change_date = db.Column(db.DateTime)
    device_info = db.Column(db.Text)
    clinical_summary = db.Column(db.Text)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')


class Vitals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

    bp = db.Column(db.String(20))   # Optional fallback
    hr = db.Column(db.Integer)
    weight = db.Column(db.Float)
    temp = db.Column(db.Float)
    spo2 = db.Column(db.Float)
    glucose = db.Column(db.Float)
    rr = db.Column(db.Float)
    bmi = db.Column(db.Float)
    ahi = db.Column(db.Float)
    eda = db.Column(db.Float)
    hrv = db.Column(db.Float)
    step_count = db.Column(db.Integer)
    sleep_duration = db.Column(db.Float)
    gait_speed = db.Column(db.Float)
    tremor_amplitude = db.Column(db.Float)
    peak_exp_flow = db.Column(db.Float)
    transdermal_alcohol = db.Column(db.Float)
    fetal_hr = db.Column(db.Float)
    contraction_freq = db.Column(db.Float)
    med_adherence = db.Column(db.Float)
    skin_temp = db.Column(db.Float)
    bradykinesia_score = db.Column(db.Float)
    limb_rom_symmetry = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('vitals', uselist=False))


class ClinicalNarrative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    source_text = db.Column(db.Text, nullable=False)  # Raw input
    parsed_json = db.Column(db.Text)  # JSON representation
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='narratives')


class CareChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    meta = db.Column(db.Text, nullable=True)  # NEW

    user = db.relationship('User', backref='care_messages')



class PatientProfile(db.Model):
    id                      = db.Column(db.Integer, primary_key=True)
    user_id                 = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    data                    = db.Column(db.JSON)
    original_input          = db.Column(db.Text)
    missing_fields_snapshot = db.Column(db.JSON)
    alerts_snapshot         = db.Column(db.JSON)            # ← NEW
    updated_at              = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PatientChatMessage(db.Model):
    __tablename__ = 'patient_chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = db.Column(db.String(50), nullable=False)     # e.g. 'user' or 'nurse'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='patient_messages')