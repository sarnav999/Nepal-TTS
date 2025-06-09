import React, { useEffect, useState } from 'react';
import { useAuth } from './AuthContext';
import {BACKEND_URL} from "./config";

function ViewVitals() {
  const { user } = useAuth();
  const [vitals, setVitals] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchVitals = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/vitals/${user.username}`);
        const data = await res.json();
        if (res.ok) {
          setVitals(data);
        } else {
          setMessage(data.error || data.message || 'Failed to load vitals');
        }
      } catch (err) {
        setMessage('❌ Network error');
      }
    };
    fetchVitals();
  }, [user.username]);

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h3 className="text-xl font-semibold mb-4">📊 Your Vitals</h3>
      {message && <p className="text-red-500">{message}</p>}
      {vitals && vitals.bp && (
        <ul className="space-y-2">
          <li>🩺 Blood Pressure: {vitals.bp}</li>
          <li>❤️ Heart Rate: {vitals.hr} bpm</li>
          <li>⚖️ Weight: {vitals.weight} kg</li>
          <li>🌡️ Temperature: {vitals.temp}°F</li>
          <li>🕒 Recorded At: {new Date(vitals.recorded_at).toLocaleString()}</li>
        </ul>
      )}
    </div>
  );
}

export default ViewVitals;