from typing import Dict, List

def assess_triage(patient: Dict) -> Dict:
    """
    Assess triage based on patient data.
    patient: dict with keys: o2_saturation, gcs_score, temperature, systolic_bp, diastolic_bp, heart_rate, symptoms (list of symptom ids)
    Returns: dict with keys: tag, time, reason, diagnoses
    """
    # Define symptom groups and diagnoses (copied from TTS_V1.py)
    red_symptoms = {
        "shortness_of_breath_severe": ["Acute Pulmonary Edema", "Severe Asthma", "Pulmonary Embolism"],
        "vomiting_blood": ["Upper GI Bleeding", "Gastric Ulcer", "Esophageal Varices"],
        "hypertension_with_symptoms": ["Hypertensive Emergency", "End Organ Damage", "Malignant Hypertension"],
        "chest_pain": ["Acute Coronary Syndrome", "Myocardial Infarction", "Aortic Dissection"],
        "severe_headache": ["Subarachnoid Hemorrhage", "Meningitis", "Cerebral Aneurysm"],
        "major_trauma": ["Internal Bleeding", "Organ Injury", "Neurological Trauma"],
        "abdominal_pain_severe": ["Acute Appendicitis", "Perforated Viscus", "Acute Pancreatitis"]
    }
    yellow_symptoms = {
        "shortness_of_breath_mild": ["COPD Exacerbation", "Bronchitis", "Anxiety-induced Dyspnea"],
        "hypertension_without_symptoms": ["Essential Hypertension", "White Coat Hypertension"],
        "vomiting_nausea": ["Gastroenteritis", "Food Poisoning", "Viral Infection"],
        "headache_moderate": ["Migraine", "Tension Headache", "Sinusitis"],
        "bloody_diarrhea": ["Inflammatory Bowel Disease", "Infectious Colitis", "Diverticulitis"],
        "unexplained_tachycardia": ["Anxiety", "Dehydration", "Thyrotoxicosis"]
    }
    green_symptoms = {
        "eye_problems": ["Conjunctivitis", "Dry Eyes", "Minor Eye Trauma"],
        "psychiatric_issues": ["Anxiety", "Depression", "Stress"],
        "joint_pain": ["Osteoarthritis", "Minor Sprain", "Chronic Joint Pain"],
        "gynecological": ["Menstrual Issues", "Minor Vaginal Discharge", "Pregnancy Check"],
        "pediatric_routine": ["Growth Check", "Vaccination", "Minor Pediatric Ailments"],
        "general_symptoms": ["Minor Infections", "Chronic Disease Follow-up", "Medication Review"],
        "constipation": ["Functional Constipation", "Diet-related", "Medication Side Effect"],
        "medication_request": ["Medication Refill", "Prescription Review"],
        "dressing_change": ["Wound Care", "Post-operative Care"],
        "mild_diarrhea": ["Viral Gastroenteritis", "Dietary Indiscretion", "IBS"]
    }
    # Ambulance arrival
    if patient.get("ambulance_arrival"):
        return {
            "tag": "RED",
            "time": "15 minutes",
            "reason": "Patient arrived by ambulance",
            "diagnoses": ["Trauma", "Acute Medical Emergency", "Critical Condition"]
        }
    # RED vital signs
    try:
        o2 = float(patient.get("o2_saturation", 0))
        if o2 < 90 and o2 > 0:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Critical O₂ saturation: {o2}%", "diagnoses": ["Respiratory Failure", "Severe Pneumonia", "Pulmonary Embolism"]}
        gcs = int(patient.get("gcs_score", 15))
        if gcs < 10:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Critical GCS Score: {gcs}", "diagnoses": ["Altered Mental Status", "Intracranial Event", "Metabolic Encephalopathy"]}
        temp = float(patient.get("temperature", 0))
        if temp > 40 and temp > 0:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Critical High Temperature: {temp}°C", "diagnoses": ["Severe Sepsis", "Malignant Hyperthermia", "Heat Stroke"]}
        if temp < 35 and temp > 0:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Critical Low Temperature: {temp}°C", "diagnoses": ["Severe Hypothermia", "Septic Shock", "Environmental Exposure"]}
        sbp = float(patient.get("systolic_bp", 0))
        dbp = float(patient.get("diastolic_bp", 0))
        if sbp > 220 or dbp > 120:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Critical High Blood Pressure: {sbp}/{dbp}", "diagnoses": ["Hypertensive Emergency", "Malignant Hypertension", "End Organ Damage"]}
        if sbp < 80 and sbp > 0:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Critical Low Blood Pressure: {sbp}/{dbp}", "diagnoses": ["Hypotensive Shock", "Sepsis", "Severe Dehydration"]}
        hr = float(patient.get("heart_rate", 0))
        if hr < 40 and hr > 0:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Critical Low Heart Rate: {hr} bpm", "diagnoses": ["Severe Bradycardia", "Heart Block", "Sick Sinus Syndrome"]}
        if hr > 150 and hr > 0:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Critical High Heart Rate: {hr} bpm", "diagnoses": ["Severe Tachycardia", "Atrial Fibrillation", "Ventricular Tachycardia"]}
    except Exception:
        pass
    # RED symptoms
    for s in patient.get("symptoms", []):
        if s in red_symptoms:
            return {"tag": "RED", "time": "15 minutes", "reason": f"Presence of RED TAG symptom: {s}", "diagnoses": red_symptoms[s]}
    # YELLOW vital signs
    try:
        o2 = float(patient.get("o2_saturation", 0))
        if 90 <= o2 < 94 and o2 > 0:
            return {"tag": "YELLOW", "time": "30 minutes", "reason": f"Concerning O₂ saturation: {o2}%", "diagnoses": ["COPD Exacerbation", "Asthma", "Pneumonia"]}
        gcs = int(patient.get("gcs_score", 15))
        if 10 <= gcs <= 13:
            return {"tag": "YELLOW", "time": "30 minutes", "reason": f"Concerning GCS Score: {gcs}", "diagnoses": ["Concussion", "Medication Effect", "Metabolic Disorder"]}
        temp = float(patient.get("temperature", 0))
        if 35 <= temp < 36 and temp > 0:
            return {"tag": "YELLOW", "time": "30 minutes", "reason": f"Concerning Low Temperature: {temp}°C", "diagnoses": ["Mild Hypothermia", "Poor Circulation", "Environmental Exposure"]}
        if 38 <= temp <= 40 and temp > 0:
            return {"tag": "YELLOW", "time": "30 minutes", "reason": f"Concerning High Temperature: {temp}°C", "diagnoses": ["Infection", "Inflammatory Condition", "Early Sepsis"]}
        sbp = float(patient.get("systolic_bp", 0))
        dbp = float(patient.get("diastolic_bp", 0))
        if 80 <= sbp < 90:
            return {"tag": "YELLOW", "time": "30 minutes", "reason": f"Concerning Low Blood Pressure: {sbp}/{dbp}", "diagnoses": ["Early Shock", "Dehydration", "Medication Effect"]}
        if (160 < sbp <= 220) or (100 < dbp <= 120):
            return {"tag": "YELLOW", "time": "30 minutes", "reason": f"Concerning High Blood Pressure: {sbp}/{dbp}", "diagnoses": ["Hypertension", "Anxiety", "Pain"]}
        hr = float(patient.get("heart_rate", 0))
        if 40 <= hr < 50 and hr > 0:
            return {"tag": "YELLOW", "time": "30 minutes", "reason": f"Concerning Low Heart Rate: {hr} bpm", "diagnoses": ["Bradycardia", "Beta Blocker Effect", "Athletic Heart"]}
        if 100 < hr <= 150 and hr > 0:
            return {"tag": "YELLOW", "time": "30 minutes", "reason": f"Concerning High Heart Rate: {hr} bpm", "diagnoses": ["Tachycardia", "Anxiety", "Fever"]}
    except Exception:
        pass
    # YELLOW symptoms
    yellow_found = []
    for s in patient.get("symptoms", []):
        if s in yellow_symptoms:
            yellow_found.append(s)
    if yellow_found:
        diagnoses = []
        for s in yellow_found:
            diagnoses.extend(yellow_symptoms[s])
        return {"tag": "YELLOW", "time": "30 minutes", "reason": f"YELLOW TAG conditions: {', '.join(yellow_found)}", "diagnoses": diagnoses}
    # GREEN symptoms
    green_found = []
    for s in patient.get("symptoms", []):
        if s in green_symptoms:
            green_found.append(s)
    if green_found:
        diagnoses = []
        for s in green_found:
            diagnoses.extend(green_symptoms[s])
        return {"tag": "GREEN", "time": "60 minutes", "reason": f"GREEN TAG conditions: {', '.join(green_found)}", "diagnoses": diagnoses}
    # Default
    return {"tag": "GREEN", "time": "60 minutes", "reason": "No urgent symptoms or abnormal vital signs detected", "diagnoses": ["Routine Check-up", "Minor Ailment"]} 