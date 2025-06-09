// src/components/CareTeamPatientPage.js
import React, { useEffect, useState } from 'react';
import { useParams }           from 'react-router-dom';
import CareTeamPatientView     from './CareTeamPatientView';
import { BACKEND_URL } from './config';

export default function CareTeamPatientPage() {
  const { username } = useParams();
  const [patient, setPatient] = useState(null);

  // fetch your roster once, then find the selected user
  useEffect(() => {
    fetch(`${BACKEND_URL}/patients`)
      .then(r => r.json())
      .then(list => {
        const found = list.find(p => p.username === username);
        setPatient(found || null);
      })
      .catch(console.error);
  }, [username]);

  if (patient === null) {
    // still loading or not found
    return <p className="p-6">Loading patient…</p>;
  }

  return <CareTeamPatientView patient={patient} />;
}
