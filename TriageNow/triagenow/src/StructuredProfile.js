// StructuredProfile.js
import React from 'react';

const categoryMap = {
  demographics: ['age', 'sex', 'gestational_age', 'race_ethnicity'],
  vitals: ['hr', 'bp', 'spo2', 'rr', 'temp', 'weight', 'bmi', 'glucose'],
  conditions: ['conditions', 'nyha', 'comorbidities'],
  treatments: ['medications', 'devices'],
  behavioral: ['activity_goal', 'sobriety_plan', 'diet'],
  infectious: ['covid_dx_date', 'vax_status']
};

const fieldLabels = {
  age: 'Age',
  sex: 'Sex',
  gestational_age: 'Gestational Age',
  race_ethnicity: 'Race/Ethnicity',
  hr: 'Heart Rate',
  bp: 'Blood Pressure',
  spo2: 'SpO₂',
  rr: 'Respiratory Rate',
  temp: 'Temperature',
  weight: 'Weight',
  bmi: 'BMI',
  glucose: 'Glucose',
  conditions: 'Conditions',
  nyha: 'NYHA Class',
  comorbidities: 'Comorbidities',
  medications: 'Medications',
  devices: 'Devices',
  activity_goal: 'Activity Goal',
  sobriety_plan: 'Sobriety Plan',
  diet: 'Diet',
  covid_dx_date: 'COVID-19 Diagnosis',
  vax_status: 'Vaccination Status'
};

const StructuredProfile = ({ profile }) => {
  if (!profile) return null;

  return (
    <div className="space-y-6">
      {/* Missing Fields Warning */}
      {profile.missing_fields?.length > 0 && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800 p-4 rounded">
          <strong>⚠️ Missing Important Data:</strong>
          <ul className="list-disc pl-5 mt-2">
            {profile.missing_fields.map((field, i) => (
              <li key={i}>{field}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Category Sections */}
      {Object.entries(categoryMap).map(([category, fields]) => {
        const categoryData = fields
          .filter(field => profile[field] !== undefined)
          .map(field => ({
            label: fieldLabels[field],
            value: Array.isArray(profile[field])
              ? profile[field].join(', ')
              : profile[field]
          }));

        if (categoryData.length === 0) return null;

        return (
          <div key={category} className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
              {category.replace(/_/g, ' ')}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {categoryData.map(({ label, value }, i) => (
                <div key={i} className="flex items-center">
                  <span className="text-gray-600 text-sm w-32 flex-shrink-0">
                    {label}:
                  </span>
                  <span className="text-gray-800 font-medium">
                    {value || '—'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StructuredProfile;