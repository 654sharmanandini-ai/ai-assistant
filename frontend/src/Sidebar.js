import React, { useState, useRef, useEffect } from 'react';

function Sidebar({ chats, activeChatId, onNewChat, onSelectChat, onDeleteChat, onRenameChat, onToggleSidebar, onSearchOpen, userName, onLogout, onLoginOpen }) {
  const [hoveredId, setHoveredId] = useState(null);
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [renamingId, setRenamingId] = useState(null);
  const [renameValue, setRenameValue] = useState('');
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpenId(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleRename = (chat) => {
    setRenamingId(chat.id);
    setRenameValue(chat.title);
    setMenuOpenId(null);
  };

  const submitRename = async (chatId) => {
    if (renameValue.trim()) {
      await onRenameChat(chatId, renameValue.trim());
    }
    setRenamingId(null);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-top">
          <h2>🌍 Pular AI</h2>
          <button className="toggle-btn" onClick={onToggleSidebar} title="Close sidebar">
            ☰
          </button>
        </div>
        <button className="new-chat-btn" onClick={onNewChat}>
          + New Chat
        </button>
        <button className="search-chat-btn" onClick={onSearchOpen}>
          🔍 Search chats
        </button>
      </div>

      <div className="chat-list">
        {chats.length === 0 && (
          <p className="no-chats">No chats yet. Click + New Chat!</p>
        )}
        {chats.map(chat => (
          <div
            key={chat.id}
            className={`chat-item ${activeChatId === chat.id ? 'active' : ''}`}
            onClick={() => !renamingId && onSelectChat(chat.id)}
            onMouseEnter={() => setHoveredId(chat.id)}
            onMouseLeave={() => setHoveredId(null)}
          >
            {renamingId === chat.id ? (
              <input
                className="rename-input"
                value={renameValue}
                onChange={(e) => setRenameValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') submitRename(chat.id);
                  if (e.key === 'Escape') setRenamingId(null);
                }}
                onBlur={() => submitRename(chat.id)}
                autoFocus
                onClick={(e) => e.stopPropagation()}
              />
            ) : (
              <>
                <span className="chat-title">💬 {chat.title}</span>
                {(hoveredId === chat.id || menuOpenId === chat.id) && (
                  <div className="menu-wrapper" ref={menuOpenId === chat.id ? menuRef : null}>
                    <button
                      className="dots-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setMenuOpenId(menuOpenId === chat.id ? null : chat.id);
                      }}
                    >
                      ···
                    </button>
                    {menuOpenId === chat.id && (
                      <div className="dropdown-menu">
                        <button
                          className="dropdown-item"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRename(chat);
                          }}
                        >
                           Rename
                        </button>
                        <button
                          className="dropdown-item delete"
                          onClick={(e) => {
                            e.stopPropagation();
                            setMenuOpenId(null);
                            onDeleteChat(chat.id);
                          }}
                        >
                           Delete
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        ))}
      </div>
    <div className="sidebar-footer">
        {userName ? (
          <div className="user-info">
            <div className="user-avatar">{userName.charAt(0).toUpperCase()}</div>
            <div className="user-details">
              <span className="user-name">{userName}</span>
              <button className="logout-btn" onClick={onLogout}>Sign out</button>
            </div>
          </div>
        ) : (
          <button className="sidebar-login-btn" onClick={onLoginOpen}>
            Login / Sign Up
          </button>
        )}
      </div>
    </div>
  );
}

export default Sidebar;