import React, { useState } from 'react';
import {BACKEND_URL} from "./config";

function TriageForm() {
  const [symptoms, setSymptoms] = useState('');
  const [medications, setMedications] = useState({
    Tylenol: false,
    Thermometer: false,
    CoughDrops: false,
    Water: false,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheckboxChange = (event) => {
    const { name, checked } = event.target;
    setMedications((prev) => ({ ...prev, [name]: checked }));
  };

  const handleSubmit = async () => {
  const selectedMeds = Object.keys(medications).filter((key) => medications[key]);
  setLoading(true);
  setResult(null);

  try {
    const response = await fetch(`${BACKEND_URL}/triage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms, medications: selectedMeds }),
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();
    setResult({
      urgency: 'Based on Sonar AI',
      plan: data?.choices?.[0]?.message?.content || data?.answer || 'No clear recommendation.',
      sources: data?.citations || [],
    });
  } catch (error) {
    console.error('Fetch error:', error);
    alert('An error occurred while fetching triage advice.');
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4 py-8">
      <div className="max-w-xl w-full bg-white p-6 rounded-xl shadow-md">
        <h1 className="text-3xl font-bold text-center mb-4">TriageNow</h1>
        <p className="text-lg text-center mb-2">How are you feeling today?</p>
        <textarea
          rows="3"
          className="w-full p-3 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Describe your symptoms..."
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
        />

        <h3 className="text-md font-semibold mb-2">What do you have with you?</h3>
        <div className="grid grid-cols-2 gap-2 mb-4">
          {Object.keys(medications).map((item) => (
            <label key={item} className="flex items-center space-x-2">
              <input
                type="checkbox"
                name={item}
                checked={medications[item]}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-blue-600"
              />
              <span>{item}</span>
            </label>
          ))}
        </div>

        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 text-white font-medium py-2 px-4 rounded-lg hover:bg-blue-700 transition"
        >
          Get Advice
        </button>
        {loading && <p className="text-center text-blue-600 mt-4">Thinking...</p>}

        {result && (
          <div className="mt-6 border-t pt-4">
            <h2 className="text-xl font-bold mb-2">Suggested Plan</h2>
            <p className="text-sm text-gray-700 mb-1">
              <strong>Urgency:</strong> {result.urgency}
            </p>
            <div
                className="prose prose-sm max-w-none text-gray-800 mb-2"
                dangerouslySetInnerHTML={{__html: result.plan}}
            />
            {result.sources.length > 0 && (
                <>
                  <p className="font-semibold mt-2">Sources:</p>
                <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
                  {result.sources.map((url, idx) => (
                    <li key={idx}>
                      <a href={url} target="_blank" rel="noreferrer" className="underline">
                        {url}
                      </a>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default TriageForm;