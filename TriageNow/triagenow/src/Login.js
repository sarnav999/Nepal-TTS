import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import { BACKEND_URL } from './config';


function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [message, setMessage] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');

    try {
      const res = await fetch(`${BACKEND_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await res.json();
      if (res.ok) {
        login(data.user);
        if (data.user.role === 'care_team') navigate('/care-dashboard');
        else if (data.user.role === 'admin') navigate('/admin-dashboard');
        else navigate('/dashboard');
      } else {
        setMessage(`❌ ${data.error || 'Login failed.'}`);
      }
    } catch (err) {
      setMessage('❌ Network error');
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Login</h2>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input name="username" placeholder="Username" onChange={handleChange} className="w-full p-2 border rounded" />
        <input name="password" type="password" placeholder="Password" onChange={handleChange} className="w-full p-2 border rounded" />
        <button type="submit" className="w-full bg-green-600 text-white py-2 rounded">Login</button>
      </form>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
}

export default Login;