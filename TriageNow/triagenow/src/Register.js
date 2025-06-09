import React, { useState } from 'react';
import {BACKEND_URL} from "./config";

function Register() {
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    password: '',
    role: 'patient'
  });
  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');

    try {
      const res = await fetch(`${BACKEND_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await res.json();
      if (res.ok) {
        setMessage('✅ Registered successfully!');
      } else {
        setMessage(`❌ ${data.error || 'Registration failed.'}`);
      }
    } catch (err) {
      setMessage('❌ Network error');
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Register</h2>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input name="name" placeholder="Name" onChange={handleChange} className="w-full p-2 border rounded"/>
        <input name="username" placeholder="Username" onChange={handleChange} className="w-full p-2 border rounded"/>
        <input name="password" type="password" placeholder="Password" onChange={handleChange}
               className="w-full p-2 border rounded"/>
        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded">Register</button>
      </form>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
}

export default Register;