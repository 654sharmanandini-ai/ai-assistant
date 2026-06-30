import React, { useState, useRef, useEffect } from 'react';

function ChatBox({ activeChatId, messages, setMessages, updateChatTitle, onNewChat, sidebarOpen, onToggleSidebar, pendingMessage, onPendingClear, token }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [hoveredMsgId, setHoveredMsgId] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (pendingMessage && activeChatId && typeof pendingMessage === 'string') {
      sendMessage(pendingMessage);
      onPendingClear();
    }
  }, [pendingMessage, activeChatId]);

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  const playTTS = async (text) => {
  try {
    const response = await fetch('http://localhost:8000/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
  } catch (err) {
    console.error('TTS error:', err);
  }
};
  const sendMessage = async (text) => {
    if (!text || typeof text !== 'string' || !text.trim() || !activeChatId) return;
    const userMsg = { role: 'user', content: text, time: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    try {
     const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ chat_id: activeChatId, message: text, history: messages })
      });
      const data = await res.json();
      const aiMsg = { role: 'assistant', content: data.response, time: new Date() };
      setMessages(prev => [...prev, aiMsg]);
      playTTS(data.response);
      if (data.title) updateChatTitle(activeChatId, data.title);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const retryMessage = (content) => sendMessage(content);

  const [copiedId, setCopiedId] = useState(null);

  const copyMessage = (content, i) => {
    navigator.clipboard.writeText(content);
    setCopiedId(i);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const startEdit = (i, content) => {
    setEditingId(i);
    setEditValue(content);
  };

  const submitEdit = (i) => {
    const newMessages = messages.slice(0, i);
    setMessages(newMessages);
    setEditingId(null);
    sendMessage(editValue);
  };

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream);
    audioChunksRef.current = [];
    mediaRecorderRef.current.ondataavailable = (e) => audioChunksRef.current.push(e.data);
    mediaRecorderRef.current.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
      const formData = new FormData();
      formData.append('file', audioBlob, 'voice.wav');
      const res = await fetch('http://localhost:8000/voice', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.text) setInput(data.text);
    };
    mediaRecorderRef.current.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  if (!activeChatId) {
    return (
      <div className="chatbox empty">
        <div className="topbar">
          {!sidebarOpen && <button className="toggle-btn-main" onClick={onToggleSidebar}>☰</button>}
        </div>
        <div className="empty-state">
          <h1>🌍 Pular AI Assistant</h1>
          <p>What's on your mind today?</p>
          <div className="home-input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={async (e) => {
                if (e.key === 'Enter' && input.trim()) {
                  const msg = input;
                  setInput('');
                  await onNewChat(msg);
                }
              }}
              placeholder="Ask anything..."
            />
            <button className={`mic-btn ${recording ? 'recording' : ''}`} onClick={recording ? stopRecording : startRecording}>
              {recording ? '⏹' : '🎤'}
            </button>
            <button className="send-btn" onClick={async () => {
              if (input.trim()) { const msg = input; setInput(''); await onNewChat(msg); }
            }}>➤</button>
          </div>
          <p className="subtitle">Speaks Pular • Fulfulde • Pulaar</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chatbox">
      <div className="topbar">
        {!sidebarOpen && <button className="toggle-btn-main" onClick={onToggleSidebar}>☰</button>}
      </div>

      <div className="messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.role}`}
            onMouseEnter={() => setHoveredMsgId(i)}
            onMouseLeave={() => setHoveredMsgId(null)}
          >
            {/* BUBBLE */}
            <div className="bubble">
              {msg.role === 'assistant' && <span className="avatar">🌍</span>}
              {editingId === i ? (
                <div className="edit-box">
                  <textarea
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    rows={3}
                  />
                  <div className="edit-actions">
                    <button className="edit-save" onClick={() => submitEdit(i)}>Send</button>
                    <button className="edit-cancel" onClick={() => setEditingId(null)}>Cancel</button>
                  </div>
                </div>
              ) : (
                <p>{msg.content}</p>
              )}
            </div>

            {/* ACTION BUTTONS — BUBBLE KE BAAD */}
            {hoveredMsgId === i && editingId !== i && (
              <div className={`msg-actions ${msg.role}`}>
                {msg.time && <span className="msg-time">{formatTime(msg.time)}</span>}
                {msg.role === 'user' && (
                  <button className="action-btn" onClick={() => retryMessage(msg.content)} title="Retry">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M1 4v6h6"/><path d="M3.51 15a9 9 0 1 0 .49-3.51"/>
                    </svg>
                  </button>
                )}
                {msg.role === 'user' && (
                  <button className="action-btn" onClick={() => startEdit(i, msg.content)} title="Edit">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                )}
                <button className="action-btn" onClick={() => copyMessage(msg.content, i)} title="Copy">
                  {copiedId === i ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="2.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                  )}
                </button>
                {msg.role === 'assistant' && (
                  <button className="action-btn" onClick={() => playTTS(msg.content)} title="Play">
                    🔊
                  </button>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="bubble">
              <span className="avatar">🌍</span>
              <p className="typing">Jamma is thinking...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage(input)}
          placeholder="Message Jamma..."
          disabled={loading}
        />
        <button className={`mic-btn ${recording ? 'recording' : ''}`} onClick={recording ? stopRecording : startRecording}>
          {recording ? '⏹' : '🎤'}
        </button>
        <button className="send-btn" onClick={() => sendMessage(input)} disabled={loading}>➤</button>
      </div>
    </div>
  );
}

export default ChatBox;