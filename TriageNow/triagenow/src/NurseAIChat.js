import React, { useState } from 'react';
import {BACKEND_URL} from "./config";

function NurseAIChat({ username, questions, onUpdate }) {
  const [responses, setResponses] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (param, value) => {
    setResponses(prev => ({ ...prev, [param]: value }));
  };

  const handleSubmit = async () => {
    try {
      const payload = { username, updates: responses };
      console.log("🔁 Sending reprocess-profile request:", payload);
      const res = await fetch(`${BACKEND_URL}/reprocess-profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const result = await res.json();
        alert("✅ Profile updated with your responses.");
        setSubmitted(true);
        if (result.remaining?.length > 0) {
          alert(`🔔 Still missing: ${result.remaining.map(f => f.parameter).join(', ')}`);
        }
        if (onUpdate) onUpdate();
      } else {
        alert("❌ Failed to update profile.");
      }
    } catch (error) {
      console.error("Update error:", error);
      alert("❌ Error sending responses.");
    }
  };

  if (!questions || questions.length === 0) return null;
  if (submitted) {
    return (
      <div className="text-green-600 p-4">
        ✅ Thank you for providing a response!!
      </div>
    );
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h4 className="text-lg font-semibold mb-4">Please provide missing information:</h4>
      <div className="space-y-4">
        {questions.map((q, idx) => (
          <div key={idx} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {q.question}
              <span className="text-xs text-gray-500 ml-2">({q.guideline_ref})</span>
            </label>
            <input
              type="text"
              className="w-full p-2 border rounded"
              onChange={(e) => handleChange(q.parameter, e.target.value)}
              placeholder={`Enter ${q.parameter}`}
            />
          </div>
        ))}
        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
        >
          Submit Responses
        </button>
      </div>
    </div>
  );
}



export default NurseAIChat;

