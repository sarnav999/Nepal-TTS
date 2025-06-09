<<<<<<< HEAD
TriageNow

TriageNow is an AI-powered medical triage web app. It allows users to input symptoms and see whether they should stay home, go to urgent care, or go to the ER — with a clear explanation and trusted sources.

This app is composed of:
- A **Flask backend** (`/backend`) that queries the Perplexity Sonar API
-  A **React frontend** (`/triagenow`) built with Tailwind and Create React App

---



Prerequisites
- Python 3.8+
- Node.js and npm
- API key for [Perplexity Sonar](https://www.perplexity.ai)

---
Create a folder for the app and cd into the folder:
```bash
cd folder
git clone https://github.com/PatelShivam26684/TriageNow.git
```

cd into TriageNow:
```bash
cd TriageNow
```



Backend Setup (`/backend`)

1. Open a terminal and navigate to the `backend` folder:

```bash
cd backend
```
2. (Optional but recommended) Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows
```
3. Install required packages:

```bash
pip install -r requirements.txt
```
4. Create a .env file in the backend folder and add your Sonar API key:

SONAR_API_KEY=your_api_key_here


5. Start the Flask server:
```bash
python app.py
```
The backend will run at: http://127.0.0.1:5000

---

Frontend Setup (`/triagenow`)

1. In a separate terminal tab, cd into TriageNow and run:
```bash
cd TriageNow
cd TriageNow
npm install
npm start
```

This will start the frontend at: http://localhost:3000

Make sure the backend is running at the same time.
