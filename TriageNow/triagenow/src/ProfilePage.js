// src/components/ProfilePage.js

import React, { useEffect, useState } from 'react';
import { useAuth } from './AuthContext';
import ViewVitals from './ViewVitals';
import ProfileTable from './ProfileTable';
import {BACKEND_URL} from "./config";    // ← our shared table component

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    if (!user) return;
    fetch(`${BACKEND_URL}/profile/${user.username}`)
      .then(res => res.json())
      .then(data => {
        if (data.profile) {
          setProfile(data.profile);
        }
      })
      .catch(console.error);
  }, [user.username]);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">👤 Your Profile</h2>

      {/* Basic user info */}
      <ul className="mb-6 space-y-1 text-lg">
        <li>🧑 Name: {user.name}</li>
        <li>👤 Username: {user.username}</li>
        <li>🧭 Role: {user.role}</li>
      </ul>

      {/* Vitals section */}
      <ViewVitals />

      {/* Structured Profile */}
      <div className="mt-8">
        <h4 className="text-xl font-semibold mb-3">Structured Profile</h4>
        {profile ? (
          <ProfileTable profile={profile} />
        ) : (
          <p className="text-gray-500">No structured profile found yet.</p>
        )}
      </div>
    </div>
  );
}


