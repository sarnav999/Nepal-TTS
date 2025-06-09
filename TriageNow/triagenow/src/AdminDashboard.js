import React, { useEffect, useState } from 'react';
import { BACKEND_URL } from './config';

function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [message, setMessage] = useState('');

  const currentUser = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    fetch(`${BACKEND_URL}/users?admin=${currentUser.username}`)
      .then(res => res.json())
      .then(data => setUsers(data.users))
      .catch(() => setMessage('❌ Failed to fetch users.'));
  }, [currentUser.username]);

  const handleRoleChange = async (username, role) => {
    const res = await fetch(`${BACKEND_URL}/update-role`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ admin: currentUser.username, username, role })
    });

    const data = await res.json();
    if (res.ok) {
      setUsers(users.map(u => u.username === username ? { ...u, role } : u));
      setMessage(`✅ ${username}'s role updated.`);
    } else {
      setMessage(`❌ ${data.error}`);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Admin Dashboard</h2>
      {message && <p className="mb-4 text-red-600">{message}</p>}
      <table className="w-full border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2 border">Name</th>
            <th className="p-2 border">Username</th>
            <th className="p-2 border">Role</th>
            <th className="p-2 border">Change Role</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.username} className="text-center">
              <td className="p-2 border">{user.name}</td>
              <td className="p-2 border">{user.username}</td>
              <td className="p-2 border">{user.role}</td>
              <td className="p-2 border">
                <select
                  value={user.role}
                  disabled={user.role === 'admin' && currentUser.username !== 'rootadmin'}
                  onChange={(e) => handleRoleChange(user.username, e.target.value)}
                  className="border p-1 rounded"
                >
                  <option value="patient">Patient</option>
                  <option value="care_team">Care Team</option>
                  <option value="admin">Admin</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdminDashboard;