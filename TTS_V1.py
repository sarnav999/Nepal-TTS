import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class TriageSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Trishuli Hospital Triage System")
        self.root.geometry("1520x680")
        self.root.resizable(True, True)
        
        # Create main container
        container = ttk.Frame(root)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas with scrollbar
        self.canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Bind mousewheel to scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Create window in canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas to expand with window
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind canvas resize to window resize
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Set up the main frame
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titles
        title_label = ttk.Label(main_frame, text="Trishuli Hospital Triage System", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Patient info frame
        patient_frame = ttk.LabelFrame(main_frame, text="Patient Information", padding="10")
        patient_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        ttk.Label(patient_frame, text="Patient ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.patient_id = ttk.Entry(patient_frame, width=20)
        self.patient_id.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(patient_frame, text="Name:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.patient_name = ttk.Entry(patient_frame, width=30)
        self.patient_name.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(patient_frame, text="Age:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.patient_age = ttk.Entry(patient_frame, width=10)
        self.patient_age.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(patient_frame, text="Gender:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.patient_gender = ttk.Combobox(patient_frame, values=["Male", "Female", "Other"], width=10)
        self.patient_gender.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Ambulance arrival
        ttk.Label(patient_frame, text="Ambulance Arrival:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.ambulance_var = tk.BooleanVar()
        ttk.Checkbutton(patient_frame, variable=self.ambulance_var).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Vitals frame
        vitals_frame = ttk.LabelFrame(main_frame, text="Vital Signs", padding="10")
        vitals_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10), pady=(0, 20))
        
        ttk.Label(vitals_frame, text="O₂ Saturation (%):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.o2_saturation = ttk.Entry(vitals_frame, width=10)
        self.o2_saturation.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(vitals_frame, text="GCS Score (3-15):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.gcs_score = ttk.Combobox(vitals_frame, values=list(range(3, 16)), width=10)
        self.gcs_score.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(vitals_frame, text="Blood Glucose (mmol/L):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.blood_glucose = ttk.Entry(vitals_frame, width=10)
        self.blood_glucose.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(vitals_frame, text="Pain Score (0-10):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.pain_score = ttk.Combobox(vitals_frame, values=list(range(11)), width=10)
        self.pain_score.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(vitals_frame, text="Temperature (°C):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.temperature = ttk.Entry(vitals_frame, width=10)
        self.temperature.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(vitals_frame, text="Blood Pressure:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        bp_frame = ttk.Frame(vitals_frame)
        bp_frame.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        
        self.systolic_bp = ttk.Entry(bp_frame, width=5)
        self.systolic_bp.pack(side=tk.LEFT)
        ttk.Label(bp_frame, text="/").pack(side=tk.LEFT)
        self.diastolic_bp = ttk.Entry(bp_frame, width=5)
        self.diastolic_bp.pack(side=tk.LEFT)
        
        ttk.Label(vitals_frame, text="Heart Rate (bpm):").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.heart_rate = ttk.Entry(vitals_frame, width=10)
        self.heart_rate.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        
        # Symptoms frame
        symptoms_frame = ttk.LabelFrame(main_frame, text="Symptoms & Conditions", padding="10")
        symptoms_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 0), pady=(0, 20))
        
        # Red tag symptoms with possible diagnoses
        self.red_symptoms = {
            "shortness_of_breath_severe": {
                "name": "Shortness of breath / Moderate respiratory distress",
                "diagnoses": ["Acute Pulmonary Edema", "Severe Asthma", "Pulmonary Embolism"]
            },
            "vomiting_blood": {
                "name": "Vomiting blood",
                "diagnoses": ["Upper GI Bleeding", "Gastric Ulcer", "Esophageal Varices"]
            },
            "hypertension_with_symptoms": {
                "name": "Hypertension with symptoms",
                "diagnoses": ["Hypertensive Emergency", "End Organ Damage", "Malignant Hypertension"]
            },
            "chest_pain": {
                "name": "Chest Pain",
                "diagnoses": ["Acute Coronary Syndrome", "Myocardial Infarction", "Aortic Dissection"]
            },
            "severe_headache": {
                "name": "Severe/sudden headache",
                "diagnoses": ["Subarachnoid Hemorrhage", "Meningitis", "Cerebral Aneurysm"]
            },
            "major_trauma": {
                "name": "Major Trauma - blunt, no obvious injury",
                "diagnoses": ["Internal Bleeding", "Organ Injury", "Neurological Trauma"]
            },
            "abdominal_pain_severe": {
                "name": "Abdominal pain (severe - 8-10/10)",
                "diagnoses": ["Acute Appendicitis", "Perforated Viscus", "Acute Pancreatitis"]
            }
        }
        
        # Yellow tag symptoms with possible diagnoses
        self.yellow_symptoms = {
            "shortness_of_breath_mild": {
                "name": "Shortness of breath / Mild respiratory distress",
                "diagnoses": ["COPD Exacerbation", "Bronchitis", "Anxiety-induced Dyspnea"]
            },
            "hypertension_without_symptoms": {
                "name": "Hypertension without symptoms",
                "diagnoses": ["Essential Hypertension", "White Coat Hypertension"]
            },
            "vomiting_nausea": {
                "name": "Vomiting / nausea (mild dehydration)",
                "diagnoses": ["Gastroenteritis", "Food Poisoning", "Viral Infection"]
            },
            "headache_moderate": {
                "name": "Headache (moderate pain 4-7/10)",
                "diagnoses": ["Migraine", "Tension Headache", "Sinusitis"]
            },
            "bloody_diarrhea": {
                "name": "Uncontrolled Diarrhea (bloody)",
                "diagnoses": ["Inflammatory Bowel Disease", "Infectious Colitis", "Diverticulitis"]
            },
            "unexplained_tachycardia": {
                "name": "Unexplained tachycardia (HR >100)",
                "diagnoses": ["Anxiety", "Dehydration", "Thyrotoxicosis"]
            }
        }
        
        # Green tag symptoms with possible diagnoses
        self.green_symptoms = {
            "eye_problems": {
                "name": "Eye problems (redness/irritation)",
                "diagnoses": ["Conjunctivitis", "Dry Eyes", "Minor Eye Trauma"]
            },
            "psychiatric_issues": {
                "name": "Mental health concerns",
                "diagnoses": ["Anxiety", "Depression", "Stress"]
            },
            "joint_pain": {
                "name": "Joint/bone pain (chronic)",
                "diagnoses": ["Osteoarthritis", "Minor Sprain", "Chronic Joint Pain"]
            },
            "gynecological": {
                "name": "Gynecological issues",
                "diagnoses": ["Menstrual Issues", "Minor Vaginal Discharge", "Pregnancy Check"]
            },
            "pediatric_routine": {
                "name": "Routine pediatric issues",
                "diagnoses": ["Growth Check", "Vaccination", "Minor Pediatric Ailments"]
            },
            "general_symptoms": {
                "name": "General medical issues",
                "diagnoses": ["Minor Infections", "Chronic Disease Follow-up", "Medication Review"]
            },
            "constipation": {
                "name": "Constipation",
                "diagnoses": ["Functional Constipation", "Diet-related", "Medication Side Effect"]
            },
            "medication_request": {
                "name": "Medication request",
                "diagnoses": ["Medication Refill", "Prescription Review"]
            },
            "dressing_change": {
                "name": "Dressing change",
                "diagnoses": ["Wound Care", "Post-operative Care"]
            },
            "mild_diarrhea": {
                "name": "Mild diarrhea (no blood)",
                "diagnoses": ["Viral Gastroenteritis", "Dietary Indiscretion", "IBS"]
            }
        }
        
        # Create variables for checkboxes
        self.symptom_vars = {}
        
        # Create checkboxes for all symptoms
        row = 0
        for symptom_id, symptom_data in self.red_symptoms.items():
            self.symptom_vars[symptom_id] = tk.BooleanVar()
            ttk.Checkbutton(symptoms_frame, text=symptom_data["name"], 
                          variable=self.symptom_vars[symptom_id]).grid(
                row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1
        
        for symptom_id, symptom_data in self.yellow_symptoms.items():
            self.symptom_vars[symptom_id] = tk.BooleanVar()
            ttk.Checkbutton(symptoms_frame, text=symptom_data["name"], 
                          variable=self.symptom_vars[symptom_id]).grid(
                row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1
        
        for symptom_id, symptom_data in self.green_symptoms.items():
            self.symptom_vars[symptom_id] = tk.BooleanVar()
            ttk.Checkbutton(symptoms_frame, text=symptom_data["name"], 
                          variable=self.symptom_vars[symptom_id]).grid(
                row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=0)
        buttons_frame.columnconfigure(2, weight=0)
        buttons_frame.columnconfigure(3, weight=1)
        
        ttk.Button(buttons_frame, text="Assess Triage", command=self.assess_triage, width=15).grid(
            row=0, column=1, padx=10, pady=10)
        ttk.Button(buttons_frame, text="Clear Form", command=self.clear_form, width=15).grid(
            row=0, column=2, padx=10, pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Triage Results", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Create a sub-frame for better organization of results
        results_content = ttk.Frame(results_frame)
        results_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Triage tag with background color
        self.tag_frame = ttk.Frame(results_content)
        self.tag_frame.pack(fill=tk.X, pady=(5, 10))
        self.tag_label = ttk.Label(self.tag_frame, text="", font=("Arial", 16, "bold"))
        self.tag_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Time to assessment
        self.time_label = ttk.Label(results_content, text="", font=("Arial", 12))
        self.time_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Reason for triage level
        self.reason_label = ttk.Label(results_content, text="", font=("Arial", 12), wraplength=800)
        self.reason_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Possible diagnoses (with a header)
        ttk.Separator(results_content).pack(fill=tk.X, padx=10, pady=10)
        self.diagnosis_header = ttk.Label(results_content, text="Possible Diagnoses to Consider:", 
                                        font=("Arial", 12, "bold"))
        self.diagnosis_header.pack(fill=tk.X, padx=10, pady=(5, 0))
        self.diagnosis_label = ttk.Label(results_content, text="", font=("Arial", 12), 
                                       wraplength=800, justify=tk.LEFT)
        self.diagnosis_label.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    def assess_triage(self):
        try:
            # Initialize variables
            triage_tag = "GREEN"
            triage_time = "60 minutes"
            triage_reason = "No urgent symptoms or abnormal vital signs detected"
            possible_diagnoses = []

            # Check ambulance first (immediate RED)
            if self.ambulance_var.get():
                self.display_result("RED", "15 minutes", 
                                  "Patient arrived by ambulance",
                                  ["Trauma", "Acute Medical Emergency", "Critical Condition"])
                return

            # Check vital signs that warrant immediate RED tag
            vitals_check = self.check_vital_signs()
            if vitals_check["is_red"]:
                self.display_result("RED", "15 minutes", 
                                  vitals_check["reason"],
                                  vitals_check["diagnoses"])
                return

            # Check RED symptoms
            for symptom_id, symptom_data in self.red_symptoms.items():
                if self.symptom_vars[symptom_id].get():
                    self.display_result("RED", "15 minutes",
                                      f"Presence of RED TAG symptom: {symptom_data['name']}",
                                      symptom_data["diagnoses"])
                    return

            # Check YELLOW conditions (continue checking all)
            yellow_found = False
            yellow_reason = ""
            yellow_diagnoses = []

            # Check vital signs for yellow
            vitals_yellow = self.check_vital_signs_yellow()
            if vitals_yellow["is_yellow"]:
                yellow_found = True
                yellow_reason = vitals_yellow["reason"]
                yellow_diagnoses.extend(vitals_yellow["diagnoses"])

            # Check YELLOW symptoms
            for symptom_id, symptom_data in self.yellow_symptoms.items():
                if self.symptom_vars[symptom_id].get():
                    yellow_found = True
                    if yellow_reason:
                        yellow_reason += "; "
                    yellow_reason += symptom_data["name"]
                    yellow_diagnoses.extend(symptom_data["diagnoses"])

            if yellow_found:
                self.display_result("YELLOW", "30 minutes", 
                                  f"YELLOW TAG conditions: {yellow_reason}",
                                  yellow_diagnoses)
                return

            # Check GREEN symptoms
            green_diagnoses = []
            green_reason = []
            for symptom_id, symptom_data in self.green_symptoms.items():
                if self.symptom_vars[symptom_id].get():
                    green_reason.append(symptom_data["name"])
                    green_diagnoses.extend(symptom_data["diagnoses"])

            if green_reason:
                self.display_result("GREEN", "60 minutes",
                                  f"GREEN TAG conditions: {', '.join(green_reason)}",
                                  green_diagnoses)
                return

            # Default case
            self.display_result("GREEN", "60 minutes",
                              "No urgent symptoms or abnormal vital signs detected",
                              ["Routine Check-up", "Minor Ailment"])

        except Exception as e:
            self.display_result("ERROR", "N/A", 
                              f"Assessment failed: {str(e)}",
                              ["System Error - Please reassess manually"])
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def check_vital_signs(self):
        """Check vital signs for RED tag conditions"""
        result = {"is_red": False, "reason": "", "diagnoses": []}
        
        try:
            # O₂ saturation
            o2_sat = float(self.o2_saturation.get() or 0)
            if o2_sat < 90 and o2_sat > 0:
                result["is_red"] = True
                result["reason"] = f"Critical O₂ saturation: {o2_sat}%"
                result["diagnoses"] = ["Respiratory Failure", "Severe Pneumonia", "Pulmonary Embolism"]
                return result

            # GCS score
            if self.gcs_score.get():
                gcs = int(self.gcs_score.get())
                if gcs < 10:
                    result["is_red"] = True
                    result["reason"] = f"Critical GCS Score: {gcs}"
                    result["diagnoses"] = ["Altered Mental Status", "Intracranial Event", "Metabolic Encephalopathy"]
                    return result

            # Temperature
            temp = float(self.temperature.get() or 0)
            if temp > 40 and temp > 0:
                result["is_red"] = True
                result["reason"] = f"Critical High Temperature: {temp}°C"
                result["diagnoses"] = ["Severe Sepsis", "Malignant Hyperthermia", "Heat Stroke"]
                return result
            elif temp < 35 and temp > 0:
                result["is_red"] = True
                result["reason"] = f"Critical Low Temperature: {temp}°C"
                result["diagnoses"] = ["Severe Hypothermia", "Septic Shock", "Environmental Exposure"]
                return result

            # Blood pressure
            if self.systolic_bp.get() and self.diastolic_bp.get():
                sbp = float(self.systolic_bp.get())
                dbp = float(self.diastolic_bp.get())
                if sbp > 220 or dbp > 120:
                    result["is_red"] = True
                    result["reason"] = f"Critical High Blood Pressure: {sbp}/{dbp}"
                    result["diagnoses"] = ["Hypertensive Emergency", "Malignant Hypertension", "End Organ Damage"]
                    return result
                elif sbp < 80:
                    result["is_red"] = True
                    result["reason"] = f"Critical Low Blood Pressure: {sbp}/{dbp}"
                    result["diagnoses"] = ["Hypotensive Shock", "Sepsis", "Severe Dehydration"]
                    return result

            # Heart rate
            hr = float(self.heart_rate.get() or 0)
            if hr < 40 and hr > 0:
                result["is_red"] = True
                result["reason"] = f"Critical Low Heart Rate: {hr} bpm"
                result["diagnoses"] = ["Severe Bradycardia", "Heart Block", "Sick Sinus Syndrome"]
                return result
            elif hr > 150 and hr > 0:
                result["is_red"] = True
                result["reason"] = f"Critical High Heart Rate: {hr} bpm"
                result["diagnoses"] = ["Severe Tachycardia", "Atrial Fibrillation", "Ventricular Tachycardia"]
                return result

        except ValueError:
            pass

        return result

    def check_vital_signs_yellow(self):
        """Check vital signs for YELLOW tag conditions"""
        result = {"is_yellow": False, "reason": "", "diagnoses": []}
        
        try:
            # O₂ saturation
            o2_sat = float(self.o2_saturation.get() or 0)
            if (90 <= o2_sat < 94) and o2_sat > 0:
                result["is_yellow"] = True
                result["reason"] = f"Concerning O₂ saturation: {o2_sat}%"
                result["diagnoses"] = ["COPD Exacerbation", "Asthma", "Pneumonia"]
                return result

            # GCS score
            if self.gcs_score.get():
                gcs = int(self.gcs_score.get())
                if 10 <= gcs <= 13:
                    result["is_yellow"] = True
                    result["reason"] = f"Concerning GCS Score: {gcs}"
                    result["diagnoses"] = ["Concussion", "Medication Effect", "Metabolic Disorder"]
                    return result

            # Temperature
            temp = float(self.temperature.get() or 0)
            if (35 <= temp < 36) and temp > 0:
                result["is_yellow"] = True
                result["reason"] = f"Concerning Low Temperature: {temp}°C"
                result["diagnoses"] = ["Mild Hypothermia", "Poor Circulation", "Environmental Exposure"]
                return result
            elif (38 <= temp <= 40) and temp > 0:
                result["is_yellow"] = True
                result["reason"] = f"Concerning High Temperature: {temp}°C"
                result["diagnoses"] = ["Infection", "Inflammatory Condition", "Early Sepsis"]
                return result

            # Blood pressure
            if self.systolic_bp.get() and self.diastolic_bp.get():
                sbp = float(self.systolic_bp.get())
                dbp = float(self.diastolic_bp.get())
                if 80 <= sbp < 90:
                    result["is_yellow"] = True
                    result["reason"] = f"Concerning Low Blood Pressure: {sbp}/{dbp}"
                    result["diagnoses"] = ["Early Shock", "Dehydration", "Medication Effect"]
                    return result
                elif (160 < sbp <= 220) or (100 < dbp <= 120):
                    result["is_yellow"] = True
                    result["reason"] = f"Concerning High Blood Pressure: {sbp}/{dbp}"
                    result["diagnoses"] = ["Hypertension", "Anxiety", "Pain"]
                    return result

            # Heart rate
            hr = float(self.heart_rate.get() or 0)
            if (40 <= hr < 50) and hr > 0:
                result["is_yellow"] = True
                result["reason"] = f"Concerning Low Heart Rate: {hr} bpm"
                result["diagnoses"] = ["Bradycardia", "Beta Blocker Effect", "Athletic Heart"]
                return result
            elif (100 < hr <= 150) and hr > 0:
                result["is_yellow"] = True
                result["reason"] = f"Concerning High Heart Rate: {hr} bpm"
                result["diagnoses"] = ["Tachycardia", "Anxiety", "Fever"]
                return result

        except ValueError:
            pass

        return result

    def determine_opd(self):
        """Determine appropriate OPD based on patient characteristics and symptoms"""
        try:
            age = int(self.patient_age.get() or 0)
            gender = self.patient_gender.get()
            
            # Check pediatric cases first
            if age < 18 and age > 0:
                return "Pediatrics"
            
            # Check symptoms against each department
            for symptom_id, symptom_data in self.green_symptoms.items():
                if self.symptom_vars[symptom_id].get():
                    symptom_name = symptom_data["name"].lower()
                    
                    # Check OB/GYN cases
                    if gender == "Female" and (
                        symptom_id == "gynecological" or
                        "gynecological" in symptom_name or
                        "pregnancy" in symptom_name or
                        "menstrual" in symptom_name or
                        "vaginal" in symptom_name
                    ):
                        return "OB/GYN"
                    
                    # Check ophthalmology cases
                    if symptom_id == "eye_problems" or "eye" in symptom_name or "vision" in symptom_name:
                        return "Ophthalmology"
                    
                    # Check orthopedic cases
                    if symptom_id == "joint_pain" or any(word in symptom_name for word in ["joint", "bone", "fracture", "sprain"]):
                        return "Orthopedics"
                    
                    # Check psychiatric cases
                    if symptom_id == "psychiatric_issues" or any(word in symptom_name for word in ["mental", "psychiatric", "anxiety", "depression"]):
                        return "Psychiatry"
            
            # Default to internal medicine
            return "Internal Medicine"
            
        except ValueError:
            return "Internal Medicine"  # Default if age is not properly set

    def display_result(self, tag, time, reason, diagnoses):
        # Set colors
        color = "#ff6666" if tag == "RED" else \
                "#ffdd66" if tag == "YELLOW" else \
                "#99cc99" if tag == "GREEN" else \
                "#cccccc"  # Error state

        # Update tag label with background color
        self.tag_frame.configure(style='Results.TFrame')
        style = ttk.Style()
        style.configure('Results.TFrame', background=color)
        self.tag_label.configure(text=f"{tag} TAG", background=color)
        
        # Update other labels
        self.time_label.configure(text=f"Physician assessment within: {time}")
        
        # For GREEN tag, add OPD recommendation
        if tag == "GREEN":
            recommended_opd = self.determine_opd()
            self.reason_label.configure(text=f"Reason: {reason}\nRecommended OPD: {recommended_opd}")
        else:
            self.reason_label.configure(text=f"Reason: {reason}")
        
        # Update diagnosis section
        if diagnoses:
            self.diagnosis_header.pack(fill=tk.X, padx=10, pady=(5, 0))
            self.diagnosis_label.configure(text=", ".join(diagnoses))
            self.diagnosis_label.pack(fill=tk.X, padx=10, pady=(5, 10))
        else:
            self.diagnosis_header.pack_forget()
            self.diagnosis_label.pack_forget()

        # Force UI to refresh immediately
        self.root.update_idletasks()

    def clear_form(self):
        # Clear patient info
        self.patient_id.delete(0, tk.END)
        self.patient_name.delete(0, tk.END)
        self.patient_age.delete(0, tk.END)
        self.patient_gender.set("")
        self.ambulance_var.set(False)
        
        # Clear vitals
        self.o2_saturation.delete(0, tk.END)
        self.gcs_score.set("")
        self.blood_glucose.delete(0, tk.END)
        self.pain_score.set("")
        self.temperature.delete(0, tk.END)
        self.systolic_bp.delete(0, tk.END)
        self.diastolic_bp.delete(0, tk.END)
        self.heart_rate.delete(0, tk.END)
        
        # Clear symptoms
        for var in self.symptom_vars.values():
            var.set(False)
        
        # Clear results including diagnosis section
        self.tag_label.configure(text="", background=self.root["background"])
        self.time_label.configure(text="")
        self.reason_label.configure(text="")
        self.diagnosis_header.pack_forget()
        self.diagnosis_label.configure(text="")
        self.diagnosis_label.pack_forget()

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update the width of the canvas window to fit the frame
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
        # Get current position of scrollbar
        current_scroll = self.canvas.yview()
        
        # Update scroll region to encompass the new size
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Maintain scroll position
        self.canvas.yview_moveto(current_scroll[0])

# Main function to run the application
def main():
    root = tk.Tk()
    app = TriageSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()