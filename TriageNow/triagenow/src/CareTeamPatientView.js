import React, { useEffect, useState } from 'react';
import ChatWithCareTeam from './ChatWithCareTeam';
import NurseAIChat      from './NurseAIChat';
import ProfileTable     from './ProfileTable';
import { BACKEND_URL } from './config';

export default function CareTeamPatientView({ patient }) {
  const [vitals, setVitals]               = useState(null);
  const [messages, setMessages]           = useState([]);
  const [summary, setSummary]             = useState('');
  const [parsedProfile, setParsedProfile] = useState(null);
  const [missingFields, setMissingFields] = useState([]);
  const [alerts, setAlerts]               = useState([]);
  const [loading, setLoading]             = useState(false);
  const [showVitalsForm, setShowVitalsForm] = useState(false);
  const [manualVitals, setManualVitals] = useState({
    heartRate: '',
    systolicBP: '',
    diastolicBP: '',
    respiratoryRate: '',
    temperature: '',
    oxygenSaturation: ''
  });
  const [vitalsLoading, setVitalsLoading] = useState(false);

  /** 1️⃣ Refresh structured profile + alerts + missing_fields **/
  useEffect(() => {
    if (!patient) return;
    async function refreshProfile() {
      try {
        const res  = await fetch(`${BACKEND_URL}/profile/${patient.username}`);
        const json = await res.json();
        if (json.profile) {
          const p = json.profile;
          setParsedProfile(p);
          setMissingFields(p.missing_fields || []);
          setAlerts(
            (p.alerts || []).map(a => {
              const refs = Array.isArray(a.guideline_ref)
                ? a.guideline_ref.join(', ')
                : a.guideline_ref || '';
              return `${a.parameter}: ${a.value}` + (refs ? ` (Refs: ${refs})` : '');
            })
          );
        }
      } catch (err) {
        console.error('Error loading profile:', err);
      }
    }
    refreshProfile();
  }, [patient.username]);

  /** 2️⃣ Load vitals (optional) **/
  useEffect(() => {
    if (!patient) return;
    async function loadVitals() {
      try {
        const res  = await fetch(`${BACKEND_URL}/vitals/${patient.username}`);
        const json = await res.json();
        setVitals(json);
      } catch (err) {
        console.error('Error loading vitals:', err);
      }
    }
    loadVitals();
  }, [patient.username]);

  /** 3️⃣ Load persistent patient↔care chat **/
  useEffect(() => {
    if (!patient) return;
    async function loadChat() {
      try {
        const res  = await fetch(`${BACKEND_URL}/patient-chat/${patient.username}`);
        const json = await res.json();
        setMessages(
          (json.messages || []).map(m => ({
            role:      m.sender,
            content:   m.content,
            timestamp: m.timestamp
          }))
        );
      } catch (err) {
        console.error('Error loading chat:', err);
      }
    }
    loadChat();
  }, [patient.username]);

  /** 4️⃣ Parse & save + auto‐follow-up questions **/
  const handleParseAndSave = async () => {
    setLoading(true);
    try {
      // parse
      const res1 = await fetch(`${BACKEND_URL}/parse-profile`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ input: summary, username: patient.username })
      });
      const data = await res1.json();
      if (!data.parsed) {
        alert('⚠️ AI returned no structured data.');
        setLoading(false);
        return;
      }

      // update UI state
      setParsedProfile(data.parsed);
      setMissingFields(data.parsed.missing_fields || []);
      setAlerts(
        (data.parsed.alerts || []).map(a => {
          const refs = Array.isArray(a.guideline_ref)
            ? a.guideline_ref.join(', ')
            : a.guideline_ref || '';
          return `${a.parameter}: ${a.value}` + (refs ? ` (Refs: ${refs})` : '');
        })
      );

      // auto‐send follow-ups
      for (let f of data.parsed.missing_fields || []) {
        await fetch(`${BACKEND_URL}/care-chat`, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: patient.username,
            sender:   'nurse',
            content:  f.question,
            meta:     { system_generated: true }
          })
        });
      }

      // save
      const res2 = await fetch(`${BACKEND_URL}/save-profile`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: patient.username,
          profile:  data.parsed,
          input:    summary
        })
      });
      if (res2.ok) {
        alert('✅ Patient profile updated successfully!');
      } else {
        alert('❌ Failed to save profile.');
      }
    } catch (err) {
      console.error('Parse error:', err);
      alert('❌ Error parsing profile. See console.');
    } finally {
      setLoading(false);
    }
  };

  /** 5️⃣ Send a new care-team → patient message **/
  const handleSend = async ({ role, content }) => {
    try {
      await fetch(`${BACKEND_URL}/patient-chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          username: patient.username,
          sender:   role,
          content
        })
      });
      // reload chat
      const res  = await fetch(`${BACKEND_URL}/patient-chat/${patient.username}`);
      const json = await res.json();
      setMessages(
        (json.messages || []).map(m => ({
          role:      m.sender,
          content:   m.content,
          timestamp: m.timestamp
        }))
      );
    } catch (err) {
      console.error('Error sending message:', err);
    }
  };

  /** 6️⃣ Clear chat history **/
  const handleClearHistory = async () => {
    if (!window.confirm('Delete all patient chat history?')) return;
    try {
      await fetch(`${BACKEND_URL}/patient-chat/${patient.username}`, { method: 'DELETE' });
      setMessages([]);
    } catch (err) {
      console.error('Error clearing history:', err);
    }
  };

  const handleVitalsChange = e => {
    const { name, value } = e.target;
    setManualVitals(v => ({ ...v, [name]: value }));
  };

  const handleVitalsSubmit = async e => {
    e.preventDefault();
    setVitalsLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/vitals/${patient.username}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          heart_rate: manualVitals.heartRate,
          systolic_bp: manualVitals.systolicBP,
          diastolic_bp: manualVitals.diastolicBP,
          respiratory_rate: manualVitals.respiratoryRate,
          temperature: manualVitals.temperature,
          oxygen_saturation: manualVitals.oxygenSaturation
        })
      });
      if (res.ok) {
        alert('✅ Vitals updated successfully!');
        setShowVitalsForm(false);
        setManualVitals({
          heartRate: '',
          systolicBP: '',
          diastolicBP: '',
          respiratoryRate: '',
          temperature: '',
          oxygenSaturation: ''
        });
        // Refresh vitals
        const vitalsRes = await fetch(`${BACKEND_URL}/vitals/${patient.username}`);
        const vitalsJson = await vitalsRes.json();
        setVitals(vitalsJson);
      } else {
        alert('❌ Failed to update vitals.');
      }
    } catch (err) {
      alert('❌ Error updating vitals.');
      console.error(err);
    } finally {
      setVitalsLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Alerts banner */}
      {alerts.length > 0 && (
        <div className="mb-4 p-3 bg-red-100 text-red-800 rounded">
          <strong>🚨 Alerts:</strong>
          <ul className="list-disc pl-5">
            {alerts.map((msg, i) => <li key={i}>{msg}</li>)}
          </ul>
        </div>
      )}

      <h3 className="text-xl font-semibold mb-3">🧾 Profile: {patient.name}</h3>

      {/* Manual Vitals Entry */}
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded mb-4"
        onClick={() => setShowVitalsForm(v => !v)}
        type="button"
      >
        {showVitalsForm ? 'Cancel Manual Vitals Entry' : 'Enter Vitals Manually'}
      </button>
      {showVitalsForm && (
        <form onSubmit={handleVitalsSubmit} className="mb-6 p-4 border rounded bg-gray-50">
          <div className="mb-2">
            <label className="block mb-1">Heart Rate (bpm):</label>
            <input type="number" name="heartRate" value={manualVitals.heartRate} onChange={handleVitalsChange} className="border p-1 rounded w-full" required />
          </div>
          <div className="mb-2 flex gap-2">
            <div className="flex-1">
              <label className="block mb-1">Systolic BP (mmHg):</label>
              <input type="number" name="systolicBP" value={manualVitals.systolicBP} onChange={handleVitalsChange} className="border p-1 rounded w-full" required />
            </div>
            <div className="flex-1">
              <label className="block mb-1">Diastolic BP (mmHg):</label>
              <input type="number" name="diastolicBP" value={manualVitals.diastolicBP} onChange={handleVitalsChange} className="border p-1 rounded w-full" required />
            </div>
          </div>
          <div className="mb-2">
            <label className="block mb-1">Respiratory Rate (breaths/min):</label>
            <input type="number" name="respiratoryRate" value={manualVitals.respiratoryRate} onChange={handleVitalsChange} className="border p-1 rounded w-full" required />
          </div>
          <div className="mb-2">
            <label className="block mb-1">Temperature (°C):</label>
            <input type="number" step="0.1" name="temperature" value={manualVitals.temperature} onChange={handleVitalsChange} className="border p-1 rounded w-full" required />
          </div>
          <div className="mb-2">
            <label className="block mb-1">Oxygen Saturation (SpO2, %):</label>
            <input type="number" name="oxygenSaturation" value={manualVitals.oxygenSaturation} onChange={handleVitalsChange} className="border p-1 rounded w-full" required />
          </div>
          <button
            type="submit"
            className={`mt-2 px-4 py-2 rounded ${vitalsLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 text-white'}`}
            disabled={vitalsLoading}
          >
            {vitalsLoading ? 'Saving…' : 'Save Vitals'}
          </button>
        </form>
      )}

      {/* free-text summary input */}
      <textarea
        value={summary}
        onChange={e => setSummary(e.target.value)}
        placeholder="Paste or type clinical summary here…"
        className="w-full p-2 border rounded mb-3 h-32"
      />

      <button
        onClick={handleParseAndSave}
        disabled={loading}
        className={`px-4 py-2 rounded mb-4 ${
          loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 text-white'
        }`}
      >
        {loading ? 'Parsing patient summary…' : 'Parse & Save Profile via AI'}
      </button>

      {/* Structured Profile table */}
      {parsedProfile && (
        <div className="mb-6">
          <h5 className="text-md font-semibold mb-2">Structured Profile</h5>
          <ProfileTable profile={parsedProfile} />
        </div>
      )}

      {/* Missing-fields follow-up UI */}
      {missingFields.length > 0 && (
        <div className="mb-6">
          <div className="text-sm text-yellow-800 bg-yellow-100 p-2 rounded mb-2">
            <strong>Missing Fields Needing Follow-up:</strong>
            <ul className="list-disc pl-6">
              {missingFields.map((f, i) => (
                <li key={i}>
                  <strong>{f.parameter}:</strong> {f.question}{' '}
                  <em>({f.guideline_ref})</em>
                </li>
              ))}
            </ul>
          </div>
          <NurseAIChat
            username={patient.username}
            questions={missingFields}
            onUpdate={() => {
              /* after they answer follow-up, re-load profile */
              fetch(`${BACKEND_URL}/profile/${patient.username}`)
                .then(r => r.json())
                .then(j => setParsedProfile(j.profile))
                .catch(console.error);
            }}
          />
        </div>
      )}

      {/* Patient ↔ Care-Team chat */}
      <div className="flex justify-between items-center mb-2">
        <h5 className="text-lg font-semibold">Patient ↔ Care-Team Chat</h5>
        <button
          onClick={handleClearHistory}
          className="bg-red-600 text-white px-3 py-1 rounded text-sm"
        >
          🗑️ Clear History
        </button>
      </div>

      <ChatWithCareTeam
        messages={messages}
        onSubmit={handleSend}
        useBot={false}
        currentSender="nurse"
      />
    </div>
  );
}
















