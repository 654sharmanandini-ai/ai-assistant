import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import ChatBox from './ChatBox';
import Login from './Login';
import './App.css';

function App() {
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [pendingMessage, setPendingMessage] = useState(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [userName, setUserName] = useState(localStorage.getItem('userName'));
  const [loginOpen, setLoginOpen] = useState(false);

  useEffect(() => {
    fetchChats();
  }, [token]);

  useEffect(() => {
    if (pendingMessage && activeChatId && typeof pendingMessage === 'string') {
      setPendingMessage(null);
    }
  }, [activeChatId, pendingMessage]);

  const fetchChats = async () => {
    if (!token) return;
    const res = await fetch('http://localhost:8000/chats', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    setChats(Array.isArray(data) ? data : []);
  };

  const newChat = async (initialMessage = null) => {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch('http://localhost:8000/chats', { method: 'POST', headers });
    const data = await res.json();
    setChats(prev => [data, ...prev]);
    setActiveChatId(data.id);
    setMessages([]);
    if (initialMessage) setPendingMessage(initialMessage);
  };

  const selectChat = async (chatId) => {
    setActiveChatId(chatId);
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(`http://localhost:8000/chats/${chatId}/messages`, { headers });
    const data = await res.json();
    setMessages(data);
  };

  const deleteChat = async (chatId) => {
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    await fetch(`http://localhost:8000/chats/${chatId}`, { method: 'DELETE', headers });
    setChats(prev => prev.filter(c => c.id !== chatId));
    if (activeChatId === chatId) { setActiveChatId(null); setMessages([]); }
  };

  const renameChat = async (chatId, newTitle) => {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    await fetch(`http://localhost:8000/chats/${chatId}/rename`, {
      method: 'PUT', headers,
      body: JSON.stringify({ title: newTitle })
    });
    setChats(prev => prev.map(c => c.id === chatId ? { ...c, title: newTitle } : c));
  };

  const updateChatTitle = (chatId, title) => {
    setChats(prev => prev.map(c => c.id === chatId ? { ...c, title } : c));
  };

  const handleLogout = () => {
    setToken(null);
    setUserName(null);
    setChats([]);
    setActiveChatId(null);
    setMessages([]);
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
  };

  return (
    <div className="app">
      {sidebarOpen && (
        <Sidebar
          chats={chats}
          activeChatId={activeChatId}
          onNewChat={newChat}
          onSelectChat={selectChat}
          onDeleteChat={deleteChat}
          onRenameChat={renameChat}
          onToggleSidebar={() => setSidebarOpen(false)}
          onSearchOpen={() => setSearchOpen(true)}
          userName={userName}
          onLogout={handleLogout}
          onLoginOpen={() => setLoginOpen(true)}
        />
      )}

      <ChatBox
        activeChatId={activeChatId}
        messages={messages}
        setMessages={setMessages}
        updateChatTitle={updateChatTitle}
        onNewChat={newChat}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        pendingMessage={pendingMessage}
        onPendingClear={() => setPendingMessage(null)}
        token={token}
      />

      {searchOpen && (
        <div className="search-modal-overlay" onClick={() => setSearchOpen(false)}>
          <div className="search-modal" onClick={(e) => e.stopPropagation()}>
            <div className="search-modal-header">
              <input
                type="text"
                placeholder="Search chats..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                autoFocus
              />
              <button className="search-close-btn" onClick={() => setSearchOpen(false)}>✕</button>
            </div>
            <div className="search-results">
              {chats
                .filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()))
                .map(chat => (
                  <div key={chat.id} className="search-result-item"
                    onClick={() => { selectChat(chat.id); setSearchOpen(false); setSearchQuery(''); }}>
                    💬 {chat.title}
                  </div>
                ))}
              {chats.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase())).length === 0 && (
                <p className="no-results">No chats found</p>
              )}
            </div>
          </div>
        </div>
      )}

      {loginOpen && (
        <div className="search-modal-overlay" onClick={() => setLoginOpen(false)}>
          <div className="search-modal" onClick={(e) => e.stopPropagation()}>
            <Login onLogin={(t, n) => {
              setToken(t);
              setUserName(n);
              setLoginOpen(false);
              localStorage.setItem('token', t);
              localStorage.setItem('userName', n);
            }} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;