import { useState } from 'react';
import { authAPI } from '../api';

const AuthTest = () => {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testLogin = async () => {
    setLoading(true);
    try {
      const response = await authAPI.login({
        username: 'admin_demo',
        password: 'Admin@2026'
      });
      setResult(`Success! Got tokens: ${JSON.stringify(response.data, null, 2)}`);
    } catch (error) {
      setResult(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h3>Authentication Test</h3>
      <button onClick={testLogin} disabled={loading}>
        {loading ? 'Testing...' : 'Test Login'}
      </button>
      <pre style={{ marginTop: '20px', background: '#f5f5f5', padding: '10px' }}>
        {result}
      </pre>
    </div>
  );
};

export default AuthTest;