import React, { useState } from 'react';

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email || !password) return;
    if (isRegister && !name) return;
    setLoading(true);
    setError('');
    try {
      const url = isRegister ? 'http://localhost:8000/register' : 'http://localhost:8000/login';
      const body = isRegister ? { name, email, password } : { email, password };
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Something went wrong');
        return;
      }
      localStorage.setItem('token', data.token);
      localStorage.setItem('userName', data.name);
      onLogin(data.token, data.name);
    } catch (err) {
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-box">
        <h1>🌍 Pular AI</h1>
        <p className="login-subtitle">
          {isRegister ? 'Create your account' : 'Welcome back'}
        </p>

        {isRegister && (
          <input
            className="login-input"
            type="text"
            placeholder="Your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        )}
        <input
          className="login-input"
          type="email"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="login-input"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        />

        {error && <p className="login-error">{error}</p>}

        <button className="login-btn" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In')}
        </button>

        <p className="login-switch">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}
          <button onClick={() => { setIsRegister(!isRegister); setError(''); }}>
            {isRegister ? ' Sign In' : ' Sign Up'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;