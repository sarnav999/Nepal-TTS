import React, { useState } from 'react';
import { useAuth } from './AuthContext';  // 👈 Make sure this exists
import { BACKEND_URL } from './config';

function BoredChat() {
  const { user } = useAuth();  // 👈 Pull logged-in user info
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/bored-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: user?.username,   // 👈 Add this line
          messages: newMessages
        })
      });

      const data = await res.json();
      const reply = data.answer || '❌ No response.';
      setMessages([...newMessages, { role: 'assistant', content: reply }]);
    } catch (err) {
      setMessages([...newMessages, { role: 'assistant', content: '❌ Network error' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-xl font-bold mb-4">🧠 Bored Chat – Ask Me Anything!</h2>
      <div className="h-96 overflow-y-scroll border rounded p-3 bg-gray-50 mb-3">
        {messages.map((msg, i) => (
          <div key={i} className={`mb-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`inline-block px-3 py-2 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-green-200'}`}>
              {msg.content}
            </span>
          </div>
        ))}
        {loading && <p className="text-gray-500">Thinking...</p>}
      </div>
      <input
        className="w-full p-2 border rounded mb-2"
        placeholder="Ask me something fun or educational..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button onClick={handleSend} className="w-full bg-pink-500 text-white py-2 rounded">
        Send
      </button>
    </div>
  );
}

export default BoredChat;


