import unittest
from triage_logic import assess_triage
import csv
import sys
from functools import wraps

# Guideline references used:
# - Emergency Severity Index (ESI) v4: https://www.ahrq.gov/patient-safety/settings/emergency/esi.html
# - Manchester Triage System: https://www.manchestertriagegroup.co.uk/
# - WHO ETAT: https://www.who.int/publications/i/item/9789241510219
# - Local protocol: [Insert hospital/local protocol if used]

class CSVTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_rows = []

    def addSuccess(self, test):
        super().addSuccess(test)
        if hasattr(test, 'csv_info'):
            self.csv_rows.append([test._testMethodName, test.csv_info['input'], test.csv_info['expected'], test.csv_info['actual'], 'PASS', test.csv_info['reason']])

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if hasattr(test, 'csv_info'):
            self.csv_rows.append([test._testMethodName, test.csv_info['input'], test.csv_info['expected'], test.csv_info['actual'], 'FAIL', test.csv_info['reason']])

    def addError(self, test, err):
        super().addError(test, err)
        if hasattr(test, 'csv_info'):
            self.csv_rows.append([test._testMethodName, test.csv_info['input'], test.csv_info['expected'], test.csv_info['actual'], 'ERROR', test.csv_info['reason']])

    def write_csv(self, filename='triage_test_report.csv'):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Test Name', 'Input', 'Expected Tag', 'Actual Tag', 'Result', 'Reason'])
            writer.writerows(self.csv_rows)

class CSVTestRunner(unittest.TextTestRunner):
    resultclass = CSVTestResult
    def run(self, test):
        result = super().run(test)
        result.write_csv()
        print(f"\nTest results exported to triage_test_report.csv\n")
        return result

def log_csv(expected_tag):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # The test must set 'patient' and 'result' variables
            result = func(self, *args, **kwargs)
            # If patient/result are set as attributes, use them
            patient = getattr(self, 'patient', None)
            triage_result = getattr(self, 'result', None)
            if patient is not None and triage_result is not None:
                actual = triage_result["tag"]
                reason = triage_result["reason"]
                self.set_csv_info(patient, expected_tag, actual, reason)
            return result
        return wrapper
    return decorator

class TestTriageLogic(unittest.TestCase):
    def set_csv_info(self, patient, expected, actual, reason):
        self.csv_info = {
            'input': str(patient),
            'expected': expected,
            'actual': actual,
            'reason': reason
        }

    # --- Ambulance ---
    # ESI v4: Immediate triage for ambulance arrivals with critical presentation
    @log_csv("RED")
    def test_ambulance_arrival(self):
        self.patient = {"ambulance_arrival": True}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
        self.assertIn("ambulance", self.result["reason"].lower())

    # --- Vitals: O2 Saturation ---
    # ESI v4: O2 sat <90% is RED; 90-93% is YELLOW; >=94% is GREEN
    @log_csv("RED")
    def test_critical_o2_red(self):
        self.patient = {"o2_saturation": 85, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("YELLOW")
    def test_o2_yellow(self):
        self.patient = {"o2_saturation": 92, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("GREEN")
    def test_o2_normal(self):
        self.patient = {"o2_saturation": 97, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")

    # --- Vitals: GCS ---
    # Manchester Triage: GCS <10 is RED; 10-13 is YELLOW; >=14 is GREEN
    @log_csv("RED")
    def test_gcs_red(self):
        self.patient = {"gcs_score": 8, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("YELLOW")
    def test_gcs_yellow(self):
        self.patient = {"gcs_score": 12, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("GREEN")
    def test_gcs_normal(self):
        self.patient = {"gcs_score": 15, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")

    # --- Vitals: Temperature ---
    # WHO ETAT: Temp <35°C or >40°C is RED; 35-36°C or 38-40°C is YELLOW; 36-37.9°C is GREEN
    @log_csv("RED")
    def test_temp_red_high(self):
        self.patient = {"temperature": 41, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("RED")
    def test_temp_red_low(self):
        self.patient = {"temperature": 34, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("YELLOW")
    def test_temp_yellow_high(self):
        self.patient = {"temperature": 39, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("YELLOW")
    def test_temp_yellow_low(self):
        self.patient = {"temperature": 35.5, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("GREEN")
    def test_temp_normal(self):
        self.patient = {"temperature": 37, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")

    # --- Vitals: Blood Pressure ---
    # ESI v4: SBP <80 or >220 is RED; 80-89 or 161-220 is YELLOW; 90-160 is GREEN
    @log_csv("RED")
    def test_bp_red_high(self):
        self.patient = {"systolic_bp": 230, "diastolic_bp": 100, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("RED")
    def test_bp_red_low(self):
        self.patient = {"systolic_bp": 70, "diastolic_bp": 50, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("YELLOW")
    def test_bp_yellow_high(self):
        self.patient = {"systolic_bp": 180, "diastolic_bp": 110, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("YELLOW")
    def test_bp_yellow_low(self):
        self.patient = {"systolic_bp": 85, "diastolic_bp": 60, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("GREEN")
    def test_bp_normal(self):
        self.patient = {"systolic_bp": 120, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")

    # --- Vitals: Heart Rate ---
    # ESI v4: HR <40 or >150 is RED; 40-49 or 101-150 is YELLOW; 50-100 is GREEN
    @log_csv("RED")
    def test_hr_red_high(self):
        self.patient = {"heart_rate": 160, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("RED")
    def test_hr_red_low(self):
        self.patient = {"heart_rate": 35, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("YELLOW")
    def test_hr_yellow_high(self):
        self.patient = {"heart_rate": 120, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("YELLOW")
    def test_hr_yellow_low(self):
        self.patient = {"heart_rate": 45, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("GREEN")
    def test_hr_normal(self):
        self.patient = {"heart_rate": 75, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")

    # --- RED Symptoms ---
    @log_csv("RED")
    def test_red_symptoms(self):
        red_ids = [
            "shortness_of_breath_severe", "vomiting_blood", "hypertension_with_symptoms",
            "chest_pain", "severe_headache", "major_trauma", "abdominal_pain_severe"
        ]
        for sid in red_ids:
            with self.subTest(symptom=sid):
                self.patient = {"symptoms": [sid]}
                self.result = assess_triage(self.patient)
                self.assertEqual(self.result["tag"], "RED")
                self.assertIn(sid, self.result["reason"])

    # --- YELLOW Symptoms ---
    @log_csv("YELLOW")
    def test_yellow_symptoms(self):
        yellow_ids = [
            "shortness_of_breath_mild", "hypertension_without_symptoms", "vomiting_nausea",
            "headache_moderate", "bloody_diarrhea", "unexplained_tachycardia"
        ]
        for sid in yellow_ids:
            with self.subTest(symptom=sid):
                self.patient = {"symptoms": [sid]}
                self.result = assess_triage(self.patient)
                self.assertEqual(self.result["tag"], "YELLOW")
                self.assertIn(sid, self.result["reason"])

    # --- GREEN Symptoms ---
    @log_csv("GREEN")
    def test_green_symptoms(self):
        green_ids = [
            "eye_problems", "psychiatric_issues", "joint_pain", "gynecological",
            "pediatric_routine", "general_symptoms", "constipation", "medication_request",
            "dressing_change", "mild_diarrhea"
        ]
        for sid in green_ids:
            with self.subTest(symptom=sid):
                self.patient = {"symptoms": [sid]}
                self.result = assess_triage(self.patient)
                self.assertEqual(self.result["tag"], "GREEN")
                self.assertIn(sid, self.result["reason"])

    # --- Combinations ---
    @log_csv("RED")
    def test_red_vital_and_green_symptom(self):
        self.patient = {"o2_saturation": 85, "symptoms": ["constipation"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("YELLOW")
    def test_yellow_vital_and_yellow_symptom(self):
        self.patient = {"o2_saturation": 92, "symptoms": ["headache_moderate"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("GREEN")
    def test_green_symptom_and_normal_vitals(self):
        self.patient = {"o2_saturation": 97, "symptoms": ["constipation"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")

    # --- Default ---
    @log_csv("GREEN")
    def test_default_green(self):
        self.patient = {"symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.assertIn("No urgent symptoms", self.result["reason"])

    # --- Edge Cases for Vitals ---
    @log_csv("RED")
    def test_o2_edge_cases(self):
        # RED upper edge
        self.patient = {"o2_saturation": 89, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
        # YELLOW lower edge
        self.patient = {"o2_saturation": 90, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        # YELLOW upper edge
        self.patient = {"o2_saturation": 93, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        # GREEN lower edge
        self.patient = {"o2_saturation": 94, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")

    @log_csv("RED")
    def test_gcs_edge_cases(self):
        self.patient = {"gcs_score": 9, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
        self.patient = {"gcs_score": 10, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"gcs_score": 13, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"gcs_score": 14, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")

    @log_csv("RED")
    def test_temp_edge_cases(self):
        self.patient = {"temperature": 34.9, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
        self.patient = {"temperature": 35, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"temperature": 35.9, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"temperature": 36, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"temperature": 37.9, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"temperature": 38, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"temperature": 40, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"temperature": 40.1, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")

    @log_csv("RED")
    def test_bp_edge_cases(self):
        # SBP
        self.patient = {"systolic_bp": 79, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
        self.patient = {"systolic_bp": 80, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"systolic_bp": 89, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"systolic_bp": 90, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"systolic_bp": 159, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"systolic_bp": 160, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"systolic_bp": 161, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"systolic_bp": 220, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"systolic_bp": 221, "diastolic_bp": 80, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
        # DBP
        self.patient = {"systolic_bp": 120, "diastolic_bp": 99, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"systolic_bp": 120, "diastolic_bp": 100, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"systolic_bp": 120, "diastolic_bp": 101, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"systolic_bp": 120, "diastolic_bp": 119, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"systolic_bp": 120, "diastolic_bp": 120, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"systolic_bp": 120, "diastolic_bp": 121, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")

    @log_csv("RED")
    def test_hr_edge_cases(self):
        self.patient = {"heart_rate": 39, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
        self.patient = {"heart_rate": 40, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"heart_rate": 49, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"heart_rate": 50, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"heart_rate": 99, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"heart_rate": 100, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
        self.patient = {"heart_rate": 101, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"heart_rate": 149, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"heart_rate": 150, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        self.patient = {"heart_rate": 151, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")

    # --- Multiple Symptoms ---
    @log_csv("YELLOW")
    def test_multiple_yellow_symptoms(self):
        self.patient = {"symptoms": ["headache_moderate", "vomiting_nausea"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
    @log_csv("GREEN")
    def test_multiple_green_symptoms(self):
        self.patient = {"symptoms": ["constipation", "eye_problems"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "GREEN")
    @log_csv("RED")
    def test_red_and_yellow_symptom(self):
        self.patient = {"symptoms": ["chest_pain", "headache_moderate"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("YELLOW")
    def test_yellow_and_green_symptom(self):
        self.patient = {"symptoms": ["headache_moderate", "constipation"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")

    # --- Multiple Abnormal Vitals ---
    @log_csv("RED")
    def test_multiple_abnormal_vitals(self):
        # RED + YELLOW vital: should be RED
        self.patient = {"o2_saturation": 85, "heart_rate": 120, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
        # YELLOW + YELLOW vital: should be YELLOW
        self.patient = {"o2_saturation": 92, "heart_rate": 120, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")
        # RED + RED vital: should be RED
        self.patient = {"o2_saturation": 85, "heart_rate": 35, "symptoms": []}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")

    # --- Vitals + Symptoms ---
    @log_csv("RED")
    def test_red_vital_and_yellow_symptom(self):
        self.patient = {"o2_saturation": 85, "symptoms": ["headache_moderate"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("RED")
    def test_yellow_vital_and_red_symptom(self):
        self.patient = {"o2_saturation": 92, "symptoms": ["chest_pain"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "RED")
    @log_csv("YELLOW")
    def test_yellow_vital_and_green_symptom(self):
        self.patient = {"o2_saturation": 92, "symptoms": ["constipation"]}
        self.result = assess_triage(self.patient)
        self.assertEqual(self.result["tag"], "YELLOW")

if __name__ == "__main__":
    unittest.main(testRunner=CSVTestRunner(), verbosity=2) 