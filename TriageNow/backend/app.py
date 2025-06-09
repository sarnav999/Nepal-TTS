from gevent import monkey
monkey.patch_all()

from flask import Flask, request, jsonify, abort, url_for
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import requests
import os
import re
import traceback
import psutil
import json5 as json
from markdown import markdown

from models import db, bcrypt, User, Vitals, CareChatMessage, PatientProfile, PatientChatMessage

load_dotenv()



def clean_response(raw_text):
    # Remove <think> blocks
    clean_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL)
    # Remove markdown code blocks
    clean_text = re.sub(r"```json|```", "", clean_text)
    # Remove other markdown formatting
    clean_text = re.sub(r"\*\*(.*?)\*\*", r"\1", clean_text)
    clean_text = re.sub(r"\*(.*?)\*", r"\1", clean_text)
    # Remove excessive newlines
    clean_text = re.sub(r"\n{2,}", "\n", clean_text)
    return clean_text.strip()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'sslmode': 'require'}
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("Connected to DB:", app.config['SQLALCHEMY_DATABASE_URI'])

db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='rootadmin').first():
        root = User(name='Root Admin', username='rootadmin', role='admin')
        root.set_password('admin123')
        db.session.add(root)
        db.session.commit()
        print("✅ Root admin created with username='rootadmin' and password='admin123'")



CORS(app)

SONAR_API_KEY = os.getenv("SONAR_API_KEY")
print("Loaded SONAR_API_KEY:", SONAR_API_KEY)

@app.route('/triage', methods=['POST'])
def triage():
    data = request.get_json()
    symptoms = data.get('symptoms', '')
    medications = data.get('medications', [])

    prompt = (
        f"A patient reports the following symptoms: {symptoms}. "
        f"They have access to: {', '.join(medications)}. "
        f"Give a friendly, plain-English triage recommendation: "
        f"Should they stay home, go to urgent care, or visit the ER? "
        f"Summarize clearly in less than 5 sentences, then include sources as a list at the end."
    )

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {SONAR_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-reasoning",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        # Debugging info
        print("Status Code:", response.status_code)
        print("Raw Response Text:", response.text)

        resp_json = response.json()
        print("Parsed JSON:", resp_json)

        raw_answer = resp_json['choices'][0]['message']['content']
        print("Extracted Answer:", raw_answer)

        answer = clean_response(raw_answer)
        sources = resp_json.get('citations', [])
        return jsonify({"answer": answer, "citations": sources}), response.status_code

    except Exception as e:
        import traceback
        print("ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    print("✅ /register endpoint was hit!")
    data = request.get_json()
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    role = 'patient'

    if not all([name, username, password]):
        return jsonify({'error': 'Missing name, username, or password'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    user = User(name=name, username=username, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    print("Register endpoint hit")

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'role': user.role
        }
    }), 200

@app.route('/users', methods=['GET'])
def get_users():
    auth_username = request.args.get('admin')  # rootadmin verification
    admin_user = User.query.filter_by(username=auth_username).first()

    if not admin_user or admin_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    users = User.query.all()
    user_list = [
        {
            'id': u.id,
            'name': u.name,
            'username': u.username,
            'role': u.role
        } for u in users
    ]
    return jsonify({'users': user_list}), 200


@app.route('/update-role', methods=['POST'])
def update_user_role():
    data = request.get_json()
    admin_username = data.get('admin')
    target_username = data.get('username')
    new_role = data.get('role')

    admin_user = User.query.filter_by(username=admin_username).first()
    target_user = User.query.filter_by(username=target_username).first()

    if not admin_user or admin_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    # Only rootadmin can change admin roles
    if target_user.role == 'admin' and admin_user.username != 'rootadmin':
        return jsonify({'error': 'Only rootadmin can change other admin roles'}), 403

    target_user.role = new_role
    db.session.commit()
    return jsonify({'message': f"{target_username}'s role updated to {new_role}"}), 200

@app.route('/sonar-chat', methods=['POST'])
def sonar_chat():
    data     = request.get_json(force=True)
    username = data.get('username')
    messages = data.get('messages', [])

    # 1️⃣ Validate inputs
    if not username:
        return jsonify({'error': 'Missing username'}), 400
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    # lookup user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # 2️⃣ Fetch the stored profile JSON
    profile = PatientProfile.query.filter_by(user_id=user.id).first()
    profile_data = profile.data if profile else {}

    ''''# 3️⃣ Build the brief human summary + inline full‐JSON block
    demo       = profile_data.get('demographics', {})
    vitals_map = profile_data.get('vitals_biometrics', {})
    meds_data  = profile_data.get('medications', [])

    # format vitals
    vitals_str = ", ".join(
      f"{k}={v.get('value')}{v.get('unit','')}"
      for k, v in vitals_map.items()
      if isinstance(v, dict) and v.get('value') is not None
    ) or "None"

    # flatten meds whether list or dict
    if isinstance(meds_data, list):
      meds_list = meds_data
    elif isinstance(meds_data, dict):
      meds_list = []
      for key, val in meds_data.items():
        if isinstance(val, list):
          meds_list += val
        else:
          meds_list.append(key)
    else:
      meds_list = [str(meds_data)]
    meds_str = ", ".join(meds_list) or "None"'''

    # assemble full JSON block + human summary
    patient_context = (
      "Here is your FULL PROFILE (JSON):\n"
      "```json\n"
      f"{json.dumps(profile_data, indent=2)}\n"
      "```\n\n"
      f"- Name: {user.name}\n"
    )

    # 4️⃣ Flatten chat history
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    # 5️⃣ Build your final prompt
    full_prompt = f"""
You are SonarCare, a patient‐facing clinical assistant.  You have the patient’s full JSON profile above.
Use only trusted, up‐to‐date medical guidelines and case studies that physicians rely on.
Answer in clear, empathetic language (3–4 sentences) and always include a **Sources:** section at the end.

---
{patient_context}

**Chat so far:**  
{convo}

**Your response:**
"""

    # debug print
    print("📨 Prompt to SonarCare:\n", full_prompt)

    try:
        resp = requests.post(
          "https://api.perplexity.ai/chat/completions",
          headers={
            "Authorization": f"Bearer {SONAR_API_KEY}",
            "Content-Type":  "application/json"
          },
          json={
            "model":    "sonar-reasoning",
            "messages": [{"role": "user", "content": full_prompt}]
          }
        )
        resp.raise_for_status()

        raw = resp.json()
        # print entire raw so you can debug in your terminal
        print("📬 Raw SonarCare response:\n", json.dumps(raw, indent=2))

        answer   = clean_response(raw['choices'][0]['message']['content'])
        cites    = raw.get('citations', [])
        return jsonify({'answer': answer, 'citations': cites}), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500




@app.route('/update-vitals', methods=['POST'])
def update_vitals():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not user.vitals:
        user.vitals = Vitals(user_id=user.id)

    user.vitals.bp = data.get('bp')
    user.vitals.hr = data.get('hr')
    user.vitals.weight = data.get('weight')
    user.vitals.temp = data.get('temp')
    db.session.commit()

    return jsonify({'message': 'Vitals updated successfully'}), 200

@app.route('/vitals/<username>', methods=['GET'])
def get_vitals(username):
    user = User.query.filter_by(username=username).first()
    if not user or user.role != 'patient':
        return jsonify({'error': 'Vitals are only available for patients.'}), 403

    if not user.vitals:
        return jsonify({'message': 'No vitals recorded for this patient.'}), 200

    return jsonify({
        'bp': user.vitals.bp,
        'hr': user.vitals.hr,
        'weight': user.vitals.weight,
        'temp': user.vitals.temp,
        'recorded_at': user.vitals.recorded_at.isoformat()
    }), 200


@app.route('/bored-chat', methods=['POST'])
def bored_chat():
    data     = request.get_json(force=True)
    username = data.get('username')
    messages = data.get('messages', [])

    # 1️⃣ Validate inputs
    if not username:
        return jsonify({'error': 'Missing username'}), 400
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    # 2️⃣ Lookup user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # 3️⃣ Fetch profile JSON
    profile = PatientProfile.query.filter_by(user_id=user.id).first()
    profile_data = profile.data if profile else {}

    # 4️⃣ Assemble patient context with raw JSON
    patient_context = (
        "Here is your FULL PROFILE (JSON):\n"
        "```json\n"
        f"{json.dumps(profile_data, indent=2)}\n"
        "```\n\n"
        f"- Name: {user.name}\n"
    )

    # 5️⃣ Flatten chat history
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    # 6️⃣ Friendly final prompt for bored patients
    full_prompt = f"""
You are a friendly AI assistant for bored patients. When patients are bored or anxious, you teach them fun, useful, or health-related facts in simple terms.
Keep the conversation appropriate.

{patient_context}

**Chat so far:**  
{convo}

**Your response (keep it friendly and under 5 sentences, cite sources if needed):**
"""

    print("📨 Prompt to Sonar (bored mode):\n", full_prompt)

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('SONAR_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-reasoning",
                "messages": [{"role": "user", "content": full_prompt}]
            }
        )
        response.raise_for_status()
        raw = response.json()
        print("📬 Raw Bored Chat Response:", json.dumps(raw, indent=2))

        content = raw['choices'][0]['message']['content']
        clean = clean_response(content)
        sources = raw.get('citations', [])
        return jsonify({'answer': clean, 'citations': sources}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@app.route('/care-chat', methods=['POST'])
def save_care_chat_message():
    data = request.get_json()
    username = data.get('username')
    sender = data.get('sender')  # 'user', 'nurse', or 'bot'
    content = data.get('content')
    meta = data.get('meta', None)

    if not all([username, sender, content]):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    message = CareChatMessage(
        user_id=user.id,
        sender=sender,
        content=content,
        meta=json.dumps(meta) if meta else None
    )

    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Message saved'}), 201



@app.route('/care-chat/<username>', methods=['GET'])
def get_care_chat_messages(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    messages = CareChatMessage.query.filter_by(user_id=user.id).order_by(CareChatMessage.timestamp).all()
    result = [
        {
            'sender': msg.sender,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat()
        } for msg in messages
    ]
    return jsonify({'messages': result}), 200


@app.route('/patients', methods=['GET'])
def get_patients():
    patients = User.query.filter_by(role='patient').all()
    return jsonify([
        {'id': p.id, 'name': p.name, 'username': p.username}
        for p in patients
    ])


def parse_profile_text(input_text: str, username: str = None):
    if not input_text:
        raise ValueError("Missing input text")

    prompt = f"""
    You are a clinical AI assistant designed to extract structured patient data from free-text clinical summaries and updates. You must extract relevant information and validate it against condition-specific monitoring schemas.

    Use the following **master schema** derived from 2025 clinical guidelines (AHA, ADA, GINA, GOLD, etc.). For each use case, there are:
    - Core vital/biometric requirements (with LOINC references)
    - Mandatory patient-history elements
    - Recommended alert/trigger thresholds
    - Primary guideline source citations

    Do NOT fabricate data. If required fields are missing, respond as a friendly chat assistant and ASK THE USER (e.g., nurse) to provide the missing information.

    ---

    # 🧾 MASTER PROFILE REQUIREMENTS

    1. **Chronic Disease Management (HF, DM, Asthma, COPD)**
       - Core Vital/Biometric Inputs (sensor ➜ LOINC): 
         • Weight ➜ 29463-7 
         • HR/SBP/DBP ➜ 8867-4 / 8480-6 / 8462-4 
         • SpO₂ ➜ 59408-5 
         • Glucose ➜ 2339-0 
       - Required History: 
         • Age, sex 
         • NYHA class 
         • A1c & diabetes meds 
         • Asthma severity / GOLD stage 
       - Alert Thresholds: 
         • SpO₂ < 88% (GOLD 2023) 
         • Weight ↑ >2kg/3d (AHA 2022) 
         • A1c > 9% (ADA 2025)
       - Evidence: [1][2][3][4]

    2. **Post-Operative Recovery**
       - Core Vitals:
         • HR ➜ 8867-4 
         • BP ➜ 8480-6 
         • Temp ➜ 8310-5 
       - Required History:
         • Procedure type 
         • VTE risk 
         • Opioid regimen 
       - Alert:
         • Temp >38.5°C 
         • SBP <90 mmHg 
       - Evidence: [5]

    3. **Oncology Monitoring**
       - Inputs:
         • Temp ➜ 8310-5 
         • Weight ➜ 29463-7 
       - Required:
         • ANC, cancer stage, ICI use 
       - Alert:
         • Temp ≥38°C + ANC <500 
       - Evidence: [6]

    4. **Maternal-Fetal Monitoring**
       - Inputs:
         • BP ➜ 8480-6 
         • FHR ➜ 56085-1 
       - Required:
         • Gestational age, pre-eclampsia risk 
       - Alert:
         • BP ≥140/90, FHR <110/>160 
       - Evidence: [8]

    5. **Substance Use**
       - Inputs:
         • Transdermal EtOH, HR ➜ 8867-4 
       - Required:
         • AUDIT score, naltrexone use 
       - Alert:
         • TAC ≥0.02% 
       - Evidence: [21]

    # 📚 Sources
    1. AHA 2022 HF - doi:10.1161/CIR.0000000000001063
    2. ADA 2025 - https://diabetesjournals.org/care/article/48/Supplement_1/S6
    3. GINA 2024 - https://ginasthma.org
    4. GOLD 2023 - https://goldcopd.org
    5. ERAS 2025 - https://erassociety.org
    6. ASCO 2024 - https://connectwithcare.org
    8. ACOG/AHRQ Maternal RPM 2025
    21. SOBRsafe EtOH Validation - https://ir.sobrsafe.com

    ---

    ## TASK

    Analyze the following input (which may contain both the original summary and follow-up updates).
    If there is any follow up updates, you should act like a chatbot considering the response you gave earlier and new responses from the careteam and respond accordingly:

    \"""{input_text}\"""

    1. Extract valid clinical information and incorporate new updates into the existing structure.
    2. Preserve previously valid data if still applicable.
    3. Re-evaluate *missing_fields* based on the full current information.
    4. Return the updated JSON structured profile.

    Output a single raw JSON object with:
    - demographics
    - vitals_biometrics (with LOINC)
    - functional_scores
    - medications
    - devices
    - behavioral_factors
    - infectious_history
    - missing_fields (list of dictionaries with parameter, question, guideline_ref)
    - alerts (trigger violations)

    Use null for unknown values. Do not fabricate. Only ask about *required* missing values.
    """

    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {SONAR_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "sonar-reasoning",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    raw_output = response.json()['choices'][0]['message']['content']
    cleaned = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL).strip()
    cleaned = re.sub(r"^```json|```$", "", cleaned).strip()
    json_match = re.search(r'\{[\s\S]*\}', cleaned)

    if not json_match:
        raise ValueError("No valid JSON object found in cleaned output.")

    json_str = json_match.group()
    json_str = re.sub(r'//.*', '', json_str)
    json_str = re.sub(r'/\*[\s\S]*?\*/', '', json_str)

    parsed_json = json.loads(json_str)
    return parsed_json



@app.route('/parse-profile', methods=['POST'])
def parse_profile():
    data = request.get_json()
    input_text = data.get('input', '')
    username = data.get('username', None)

    try:
        parsed_json = parse_profile_text(input_text, username)
        return jsonify({'parsed': parsed_json}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@app.route('/save-profile', methods=['POST'])
def save_profile():
    data         = request.get_json()
    username     = data.get('username')
    profile_data = data.get('profile')
    input_text   = data.get('input')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    existing = PatientProfile.query.filter_by(user_id=user.id).first()
    if existing:
        existing.data                 = profile_data
        existing.original_input      = input_text
        existing.missing_fields_snapshot = profile_data.get('missing_fields', [])
        existing.alerts_snapshot        = profile_data.get('alerts', [])
    else:
        new_profile = PatientProfile(
            user_id                 = user.id,
            data                    = profile_data,
            original_input          = input_text,
            missing_fields_snapshot = profile_data.get('missing_fields', []),
            alerts_snapshot         = profile_data.get('alerts', [])
        )
        db.session.add(new_profile)

    db.session.commit()
    return jsonify({'message': 'Profile saved'}), 200

@app.route('/alerts/<username>', methods=['GET'])
def get_alerts(username):
    user    = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = PatientProfile.query.filter_by(user_id=user.id).first()
    alerts  = profile.alerts_snapshot if profile else []
    return jsonify({'alerts': alerts}), 200



@app.route('/profile/<username>', methods=['GET'])
def get_saved_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = PatientProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return jsonify({'message': 'No saved profile found'}), 200

    return jsonify({'profile': profile.data}), 200


from flask import url_for

@app.route('/reprocess-profile', methods=['POST', 'OPTIONS'])
@cross_origin()
def reprocess_profile_with_updates():
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 ** 2  # in MB
    cpu_before = process.cpu_percent(interval=None)
    data = request.get_json()
    username = data.get('username')
    updates = data.get('updates', {})

    # Fetch existing profile from DB
    user = User.query.filter_by(username=username).first()
    profile = PatientProfile.query.filter_by(user_id=user.id).first()

    updated_input = (
            f"{profile.original_input}\n\nUpdates:\n" +
            "\n".join(f"{k}: {v}" for k, v in updates.items())
    )

    try:
        parsed_json = parse_profile_text(updated_input, username)
        profile.data = parsed_json
        db.session.commit()
        mem_after = process.memory_info().rss / 1024 ** 2
        cpu_after = process.cpu_percent(interval=0.5)

        print(f"Memory used: {mem_after - mem_before:.2f} MB")
        print(f"CPU used: {cpu_after:.2f}%")
        return jsonify({'parsed': parsed_json}), 200
    except Exception as e:
        mem_after = process.memory_info().rss / 1024 ** 2
        cpu_after = process.cpu_percent(interval=0.5)

        print(f"Memory used: {mem_after - mem_before:.2f} MB")
        print(f"CPU used: {cpu_after:.2f}%")
        return jsonify({'error': str(e)}), 500


@app.route('/patient-chat', methods=['POST'])
def save_patient_chat_message():
    data = request.get_json()
    username = data.get('username')
    sender   = data.get('sender')   # 'user' or 'nurse'
    content  = data.get('content')

    if not all([username, sender, content]):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    msg = PatientChatMessage(
        user_id=user.id,
        sender=sender,
        content=content
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'message': 'Message saved'}), 201


@app.route('/patient-chat/<username>', methods=['GET'])
def get_patient_chat_messages(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error':'User not found'}), 404

    msgs = (PatientChatMessage.query
              .filter_by(user_id=user.id)
              .order_by(PatientChatMessage.timestamp)
              .all()
           )
    result = [
      {
        'sender':    m.sender,
        'content':   m.content,
        'timestamp': m.timestamp.isoformat()
      } for m in msgs
    ]
    return jsonify({'messages': result}), 200

@app.route('/patient-chat/<username>', methods=['DELETE'])
def delete_patient_chat(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error':'User not found'}), 404

    # delete all patient-chat messages for that user
    PatientChatMessage.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    return jsonify({'message':'Chat history cleared'}), 200


import json
from flask import request, jsonify

@app.route('/nurse-chat', methods=['POST'])
def nurse_chat():
    data      = request.get_json(force=True)
    username  = data.get('username')
    messages  = data.get('messages', [])

    # 1️⃣ Basic validation
    if not username:
        return jsonify({'error': 'Missing username'}), 400
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # 2️⃣ Grab the full AI‐parsed profile JSON you saved earlier
    profile = PatientProfile.query.filter_by(user_id=user.id).first()
    profile_data = profile.data if profile else {}

    # 3️⃣ Serialize the chat history
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    # 4️⃣ Build a single prompt that includes:
    #    • The patient’s entire JSON profile
    #    • The ongoing chat
    #    • Clear instructions to parse/validate/alert
    full_prompt = f"""
You are a **nurse triage assistant**.  You must use only trusted clinical guidelines, case-studies and the master schema to:
  1. Rigorously validate this patient’s JSON profile against the Master schema (AHA, ADA, GINA, GOLD…).
  2. Generate any missing follow-up questions (for required fields).
  3. Identify alerts (e.g. weight gain, hypoxemia, A1c thresholds).
  4. Answer the nurse’s actual question below *in context* of this patient.
  
  Master Schema:
  # 🧾 MASTER PROFILE REQUIREMENTS

1. **Chronic Disease Management (HF, DM, Asthma, COPD)**
   - Core Vital/Biometric Inputs (sensor ➜ LOINC): 
     • Weight ➜ 29463-7 
     • HR/SBP/DBP ➜ 8867-4 / 8480-6 / 8462-4 
     • SpO₂ ➜ 59408-5 
     • Glucose ➜ 2339-0 
   - Required History: 
     • Age, sex 
     • NYHA class 
     • A1c & diabetes meds 
     • Asthma severity / GOLD stage 
   - Alert Thresholds: 
     • SpO₂ < 88% (GOLD 2023) 
     • Weight ↑ >2kg/3d (AHA 2022) 
     • A1c > 9% (ADA 2025)
   - Evidence: [1][2][3][4]

2. **Post-Operative Recovery**
   - Core Vitals:
     • HR ➜ 8867-4 
     • BP ➜ 8480-6 
     • Temp ➜ 8310-5 
   - Required History:
     • Procedure type 
     • VTE risk 
     • Opioid regimen 
   - Alert:
     • Temp >38.5°C 
     • SBP <90 mmHg 
   - Evidence: [5]

3. **Oncology Monitoring**
   - Inputs:
     • Temp ➜ 8310-5 
     • Weight ➜ 29463-7 
   - Required:
     • ANC, cancer stage, ICI use 
   - Alert:
     • Temp ≥38°C + ANC <500 
   - Evidence: [6]

4. **Maternal-Fetal Monitoring**
   - Inputs:
     • BP ➜ 8480-6 
     • FHR ➜ 56085-1 
   - Required:
     • Gestational age, pre-eclampsia risk 
   - Alert:
     • BP ≥140/90, FHR <110/>160 
   - Evidence: [8]

5. **Substance Use**
   - Inputs:
     • Transdermal EtOH, HR ➜ 8867-4 
   - Required:
     • AUDIT score, naltrexone use 
   - Alert:
     • TAC ≥0.02% 
   - Evidence: [21]

# 📚 Sources
1. AHA 2022 HF - doi:10.1161/CIR.0000000000001063
2. ADA 2025 - https://diabetesjournals.org/care/article/48/Supplement_1/S6
3. GINA 2024 - https://ginasthma.org
4. GOLD 2023 - https://goldcopd.org
5. ERAS 2025 - https://erassociety.org
6. ASCO 2024 - https://connectwithcare.org
8. ACOG/AHRQ Maternal RPM 2025
21. SOBRsafe EtOH Validation - https://ir.sobrsafe.com

---

**PATIENT PROFILE (full JSON):**
```json
{json.dumps(profile_data, indent=2)}
CHAT SO FAR:
{convo}
When you reply:

Don’t echo the nurse’s question verbatim.

Do be concise and end with a “Sources:” list.

If there are missing required fields, include them as follow-up questions.
Nurse’s question →
"""
    try:
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {SONAR_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-reasoning",
                "messages": [{"role": "user", "content": full_prompt}]
            }
        )
        resp.raise_for_status()
        raw = resp.json()

        # dump entire raw for debug if you need:
        print("📬 Raw nurse-chat response:", json.dumps(raw, indent=2))

        raw_answer = raw['choices'][0]['message']['content']
        answer = clean_response(raw_answer)
        citations = raw.get('citations', [])

        return jsonify({'answer': answer, 'citations': citations}), 200

    except Exception as e:
        import traceback;
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return {"status": "Backend is running"}, 200

if __name__ == '__main__':
    print("Registered routes:")
    print(app.url_map)
    app.run(port=5000)