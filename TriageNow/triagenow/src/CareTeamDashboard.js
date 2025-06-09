import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth }     from './AuthContext'
import NurseAssistantChat from './NurseAssistantChat'
import { BACKEND_URL } from './config';

export default function CareTeamDashboard() {
  const { user } = useAuth()
  const [patients, setPatients]         = useState([])
  const [usernameInput, setUsernameInput] = useState('')
  const [triageUsername, setTriageUsername] = useState('')
  const [profile, setProfile]           = useState(null)

  const navigate = useNavigate()

  // load your patient list
  useEffect(() => {
    fetch(`${BACKEND_URL}/patients`)
      .then(r => r.json())
      .then(setPatients)
      .catch(console.error)
  }, [])

  // when nurse enters a username, fetch that patient’s saved profile
  useEffect(() => {
    if (!triageUsername) return
    fetch(`${BACKEND_URL}/profile/${triageUsername}`)
      .then(r => r.json())
      .then(d => {
        setProfile(d.profile || null)
      })
      .catch(console.error)
  }, [triageUsername])

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">👩‍⚕️ Care Team Dashboard</h2>

      {/* ── Nurse Triage Assistant ── */}
      <div className="bg-white border rounded shadow p-4 mb-6">
        <h3 className="font-semibold text-lg mb-2">🩺 Nurse Triage Assistant</h3>
        <div className="flex space-x-2 mb-3">
          <input
            type="text"
            value={usernameInput}
            onChange={e => setUsernameInput(e.target.value)}
            placeholder="Enter patient username"
            className="border px-3 py-2 flex-grow rounded"
          />
          <button
            onClick={() => setTriageUsername(usernameInput.trim())}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Load Patient
          </button>
        </div>
        {triageUsername && profile
          ? <NurseAssistantChat
              patientUsername={triageUsername}
              profile={profile}
            />
          : <p className="text-sm text-gray-600">— awaiting patient username …</p>}
      </div>

      {/* ── Clickable List of All Patients ── */}
      <div className="bg-white border rounded shadow p-4">
        <h3 className="font-semibold text-lg mb-2">📋 Your Patients</h3>
        <ul className="divide-y">
          {patients.map(p => (
            <li
              key={p.username}
              onClick={() => navigate(`/care-team/patient/${p.username}`)}
              className="py-2 px-3 cursor-pointer hover:bg-gray-100"
            >
              {p.name} ({p.username})
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}


