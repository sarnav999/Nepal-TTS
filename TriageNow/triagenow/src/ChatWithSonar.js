// src/components/ChatWithSonar.js
import React, { useState } from 'react';
import {BACKEND_URL} from "./config";

export default function ChatWithSonar({ username, profile }) {
  const [messages, setMessages] = useState([]);
  const [input,    setInput]    = useState('');
  const [loading,  setLoading]  = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input.trim() };
    const convo   = [...messages, userMsg];
    setMessages(convo);
    setInput('');
    setLoading(true);

    // Build payload including the entire profile JSON
    const payload = {
      username,
      profile,
      messages: convo
    };

    console.log('📤 Sending to /sonar-chat:', payload);

    try {
      const res  = await fetch(`${BACKEND_URL}/sonar-chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload)
      });
      const data = await res.json();

      let assistantText = data.answer;
      if (data.citations && data.citations.length) {
        assistantText += '\n\nSources:\n' +
          data.citations.map((c,i) => `${i+1}. ${c}`).join('\n');
      }

      setMessages(prev => [...prev, { role: 'assistant', content: assistantText }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: '❌ Error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded shadow max-w-xl mx-auto">
      <div className="h-80 overflow-y-auto mb-2 border p-2 bg-gray-50">
        {messages.map((m,i) => (
          <div key={i} className={m.role==='user' ? 'text-right' : 'text-left'}>
            <span className={
              m.role==='user'
                ? 'inline-block bg-blue-200 text-black px-3 py-1 rounded'
                : 'inline-block bg-gray-200 text-black px-3 py-1 rounded'
            }>
              {m.content}
            </span>
          </div>
        ))}
        {loading && <p className="text-sm text-gray-500">SonarCare is thinking…</p>}
      </div>

      <div className="flex space-x-2">
        <input
          className="flex-1 border p-2 rounded"
          placeholder="Ask SonarCare…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key==='Enter' && sendMessage()}
        />
        <button
          className="bg-blue-600 text-white px-4 rounded"
          onClick={sendMessage}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}


