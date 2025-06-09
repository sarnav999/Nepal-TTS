import React, { useEffect, useState } from 'react';
import { useNavigate }        from 'react-router-dom';
import { useAuth }            from './AuthContext';
import ChatWithSonar          from './ChatWithSonar';
import ChatWithCareTeam       from './ChatWithCareTeam';
import {BACKEND_URL} from "./config";

export default function PatientDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // UI toggles
  const [showChat, setShowChat]                   = useState(false);
  const [showContactOptions, setShowContactOptions] = useState(false);
  const [contactMode, setContactMode]             = useState(null); // 'chat' or null

  // Data
  const [profile, setProfile]                     = useState(null);
  const [alerts, setAlerts]                       = useState([]);
  const [careTeamMessages, setCareTeamMessages]   = useState([]);

  // Bot fallback
  const useBot = careTeamMessages.length >= 3;

  /** 1️⃣ Load structured profile & derive alerts **/
  useEffect(() => {
    if (!user) return;
    async function fetchProfile() {
      try {
        const res  = await fetch(`${BACKEND_URL}/profile/${user.username}`);
        const json = await res.json();
        if (json.profile) {
          setProfile(json.profile);
          const formattedAlerts = (json.profile.alerts || []).map(a => {
            const refs = Array.isArray(a.guideline_ref)
              ? a.guideline_ref.join(', ')
              : a.guideline_ref || '';
            return `${a.parameter}: ${a.value}` + (refs ? ` (Refs: ${refs})` : '');
          });
          setAlerts(formattedAlerts);
        }
      } catch (err) {
        console.error('❌ Failed to load profile:', err);
      }
    }
    fetchProfile();
  }, [user.username]);

  /** 2️⃣ Load persisted patient↔care chat **/
  async function loadHistory() {
    if (!user) return;
    try {
      const res  = await fetch(`${BACKEND_URL}/patient-chat/${user.username}`);
      const json = await res.json();
      setCareTeamMessages(
        (json.messages || []).map(m => ({
          role:      m.sender,    // 'user' or 'nurse'
          content:   m.content,
          timestamp: m.timestamp
        }))
      );
    } catch(err) {
      console.error("❌ Failed to load chat:", err);
    }
  }
  useEffect(() => {
    loadHistory();
  }, [user.username]);

  /** 3️⃣ Send a new patient‐team message **/
  const handleCareTeamSubmit = async ({ role, content }) => {
    try {
      await fetch(`${BACKEND_URL}/patient-chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          username: user.username,
          sender:   role,
          content
        })
      });
      await loadHistory();
    } catch(err) {
      console.error("❌ Failed to send message:", err);
    }
  };

  /** 4️⃣ Clear chat history **/
  const handleClearHistory = async () => {
    if (!window.confirm("Delete your chat history?")) return;
    try {
      await fetch(`${BACKEND_URL}/patient-chat/${user.username}`, {
        method: 'DELETE'
      });
      setCareTeamMessages([]);
    } catch(err) {
      console.error("❌ Failed to clear history:", err);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Patient Dashboard</h2>
      <ul className="space-y-6">

        {/* ─── Alerts & Notifications ───────────────────── */}
        <li className="bg-white border p-4 rounded shadow">
          <h3 className="font-semibold mb-2">🔔 Alerts & Notifications</h3>
          {alerts.length ? (
            <ul className="space-y-1 text-gray-800">
              {alerts.map((msg, i) => <li key={i}>{msg}</li>)}
            </ul>
          ) : (
            <p className="text-gray-500">No alerts at this time.</p>
          )}
        </li>

        {/* ─── SonarCare Chat ───────────────────────────── */}
        <li className="bg-white border p-4 rounded shadow">
          <h3 className="font-semibold mb-2">💬 Chat with SonarCare</h3>
          {!showChat ? (
            <button
              onClick={() => setShowChat(true)}
              className="bg-purple-600 text-white px-4 py-2 rounded"
            >
              Open Chat
            </button>
          ) : (
            <div>
              <button
                onClick={() => setShowChat(false)}
                className="mb-3 bg-gray-200 px-3 py-1 rounded"
              >
                ← Back
              </button>
              <ChatWithSonar username={user.username} />
            </div>
          )}
        </li>

        {/* ─── Profile & Vitals ─────────────────────────── */}
        <li className="bg-white border p-4 rounded shadow">
          <h3 className="font-semibold mb-2">📊 Profile & Vitals</h3>
          <button
            onClick={() => navigate('/profile')}
            className="bg-green-600 text-white px-4 py-2 rounded"
          >
            View Your Data
          </button>
        </li>

        {/* ─── Nursing Team Chat ────────────────────────── */}
        <li className="bg-white border p-4 rounded shadow">
          <h3 className="font-semibold mb-2">📞 Contact Care Team</h3>
          <button
            onClick={() => setShowContactOptions(v => !v)}
            className="bg-yellow-500 text-white px-4 py-2 rounded mb-2"
          >
            {showContactOptions ? 'Hide Options' : 'Show Options'}
          </button>
          {showContactOptions && (
            <div className="space-y-2">
              <a
                href="tel:1234567890"
                className="block bg-gray-700 text-white py-2 rounded text-center"
              >
                📞 Call Nursing Station
              </a>
              <button
                onClick={() => setContactMode('chat')}
                className="w-full bg-blue-600 text-white py-2 rounded"
              >
                💬 Chat with Nursing Team
              </button>
              <button
                onClick={handleClearHistory}
                className="w-full bg-red-600 text-white py-2 rounded"
              >
                🗑️ Clear Chat History
              </button>
            </div>
          )}
          {contactMode === 'chat' && (
            <div className="mt-4">
              <ChatWithCareTeam
                messages={careTeamMessages}
                onSubmit={handleCareTeamSubmit}
                useBot={useBot}
              />
            </div>
          )}
        </li>

        {/* ─── Boredom Chat ────────────────────────────── */}
        <li className="bg-white border p-4 rounded shadow">
          <h3 className="font-semibold mb-2">🧠 I’m Bored… Teach Me Something!</h3>
          <button
            onClick={() => navigate('/bored-chat')}
            className="bg-pink-500 text-white px-4 py-2 rounded"
          >
            Open Curiosity Chat
          </button>
        </li>

        {/* ─── Emergency Contact ───────────────────────── */}
        <li className="bg-white border p-4 rounded shadow">
          <h3 className="font-semibold text-red-600 mb-2">🚨 Emergency Contact</h3>
          <a
            href="tel:911"
            className="block bg-red-600 text-white py-2 rounded text-center"
          >
            Call 911 Now
          </a>
        </li>
      </ul>
    </div>
  );
}




















