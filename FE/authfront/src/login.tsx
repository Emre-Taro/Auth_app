import React, {useState} from "react";
import { useNavigate } from "react-router-dom";

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const validateForm = () => {
        if (!username || !password) {
        setError('Username and password are required');
        return false;
        }
        setError('');
        return true;
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!validateForm()) return;
        setLoading(true);

        // エンコード形式でusernameとpasswordを送っている => バックエンドのOAuth2PasswordRequestFormが期待している形式になる
        const formDetails = new URLSearchParams();
        formDetails.append('username', username);
        formDetails.append('password', password);

        try {
        // バックエンドの./tokenのエンドポイントにPOSTリクエストを送っている
        const response = await fetch('http://localhost:8000/token', {
            method: 'POST', // postリクエスト
            headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formDetails,
        });

        setLoading(false);

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            navigate('/protected');
        } else {
            const errorData = await response.json();
            setError(errorData.detail || 'Authentication failed!');
        }
        } catch (error) {
        setLoading(false);
        setError('An error occurred. Please try again later.');
        }
    };
   
    return (
        <>
            <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f3f4f6',
      }}
    >
      <form
        style={{
          backgroundColor: '#fff',
          padding: '40px',
          borderRadius: '10px',
          boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
          minWidth: '300px',
          width: '100%',
          maxWidth: '400px',
        }}
        onSubmit={handleSubmit}
      >
        {/* Username */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ fontSize: '18px', display: 'block', marginBottom: '8px' }}>
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{
              width: '100%',
              padding: '10px',
              fontSize: '16px',
              borderRadius: '5px',
              border: '1px solid #ccc',
            }}
          />
        </div>

        {/* Password */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ fontSize: '18px', display: 'block', marginBottom: '8px' }}>
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: '100%',
              padding: '10px',
              fontSize: '16px',
              borderRadius: '5px',
              border: '1px solid #ccc',
            }}
          />
        </div>

        {/* Submit */}
        <div>
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '10px',
              fontSize: '16px',
              fontWeight: 'bold',
              backgroundColor: loading ? '#9ca3af' : '#3b82f6',
              color: '#fff',
              border: 'none',
              borderRadius: '5px',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.3s ease',
            }}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
          {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
      </form>
    </div>
        </>
    )
}

export default Login;