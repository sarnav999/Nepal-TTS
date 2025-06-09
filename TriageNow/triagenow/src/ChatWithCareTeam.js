// src/components/ChatWithCareTeam.js
import React, { useState } from 'react';

function ChatWithCareTeam({ messages, onSubmit, useBot, hideBotNotice }) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    onSubmit({ role: 'user', content: input.trim() });
    setInput('');
  };

  // Render each message with the proper label & background
  const renderMessage = (msg, idx) => {
    let label, bgClass;
    switch (msg.role) {
      case 'user':
        label   = 'You';
        bgClass = 'bg-blue-100';
        break;
      case 'nurse':
        label   = 'Nurse';
        bgClass = 'bg-green-100';
        break;
      case 'assistant':
        label   = 'Nurse-AI';
        bgClass = 'bg-purple-100';
        break;
      default:
        label   = msg.role;
        bgClass = 'bg-gray-100';
    }

    return (
      <div key={idx} className={`mb-1 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
        <span className={`inline-block px-2 py-1 rounded ${bgClass}`}>
          <strong>{label}:</strong> {msg.content}
          <div className="text-xs text-gray-500 mt-1">
            {msg.timestamp
              ? new Date(msg.timestamp).toLocaleString(undefined, {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })
              : 'Just now'}
          </div>
        </span>
      </div>
    );
  };

  return (
    <div className="p-3 bg-white border rounded shadow">
      <div className="h-40 overflow-y-scroll mb-2 border p-2 bg-gray-50">
        {messages.map(renderMessage)}
      </div>

      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && handleSend()}
        className="w-full p-2 border rounded mb-2"
        placeholder="Type your message..."
      />

      <button
        onClick={handleSend}
        className="bg-blue-600 text-white px-4 py-1 rounded w-full"
      >
        Send
      </button>

      {useBot && !hideBotNotice && (
        <p className="text-sm text-purple-700 mt-2">🤖 Nurse-AI is thinking…</p>
      )}
    </div>
  );
}

export default ChatWithCareTeam;



