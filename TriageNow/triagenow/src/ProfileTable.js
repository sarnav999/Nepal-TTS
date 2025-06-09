// src/components/ProfileTable.js
import React from 'react';

/**
 * Takes a parsedProfile object (the AI JSON) and flattens
 * it into an array of { field, value } rows, then renders a table.
 */
export default function ProfileTable({ profile }) {
  if (!profile) return null;

  // Helper: flatten the JSON structure into [ { field, value }, ... ]
  const flatten = () => {
    const rows = [];

    // Top-level simple fields (unlikely in your case)
    // then nested objects/arrays
    Object.entries(profile).forEach(([section, data]) => {
      if (data == null) return;

      // If it's an array of scalars:
      if (Array.isArray(data) && data.every(x => typeof x !== 'object')) {
        rows.push({ field: section, value: data.join(', ') });
      }
      // If it's an object:
      else if (typeof data === 'object') {
        Object.entries(data).forEach(([key, val]) => {
          if (val == null) return;
          // LOINC‐style objects: { loinc, unit, value }
          if (
            typeof val === 'object' &&
            'value' in val &&
            val.value != null
          ) {
            const unit = val.unit || '';
            rows.push({
              field: key,
              value: `${val.value}${unit}`
            });
          }
          // array of strings (e.g. ["insulin","metformin"])
          else if (Array.isArray(val)) {
            rows.push({ field: key, value: val.join(', ') });
          }
          // nested object fallback
          else if (typeof val === 'object') {
            rows.push({
              field: key,
              value: JSON.stringify(val)
            });
          }
          // primitive
          else {
            rows.push({ field: key, value: val.toString() });
          }
        });
      }
      // primitive fallback
      else {
        rows.push({ field: section, value: data.toString() });
      }
    });

    return rows;
  };

  const rows = flatten();

  return (
    <div className="max-w-xl mx-auto overflow-x-auto">
      <table className="min-w-full table-auto border-collapse">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-3 py-1 text-left">Field</th>
            <th className="border px-3 py-1 text-left">Value</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr
              key={i}
              className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
            >
              <td className="border px-3 py-1 align-top">{r.field}</td>
              <td className="border px-3 py-1 whitespace-pre-wrap">
                {r.value}
              </td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td
                colSpan={2}
                className="border px-3 py-3 text-center text-gray-500"
              >
                No profile data found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
