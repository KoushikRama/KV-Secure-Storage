import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './dashboard.css';

export const Dashboard = () => {
  const [apps, setApps] = useState([]);
  const [users, setUsers] = useState([]);
  const [newApp, setNewApp] = useState({ app_name: '', app_password: '' , app_username:''});
  const [msg, setMsg] = useState('');
  const [userType, setUserType] = useState(null);
  const username = localStorage.getItem('username');
  useEffect(() => {
    if (!username) return;

    axios.get('http://localhost:8000/user/type', {
      params: { username }
    })
    .then(res => setUserType(res.data.user_type))
    .catch(err => console.error('Error fetching userType:', err));
  }, [username]);

  useEffect(() => {
    if (userType === 'admin') {
      axios.get('http://localhost:8000/admin/users')
        .then(res => setUsers(res.data))
        .catch(err => console.error(err));
    } else {
      axios.get('http://localhost:8000/user/apps', { params: { username } })
        .then(res => setApps(res.data))
        .catch(err => console.error(err));
    }
  }, [userType, username]);

  const handleAddApp = (e) => {
    e.preventDefault();
  
    if (!username || !newApp.app_name || !newApp.app_username || !newApp.app_password) {
      setMsg('Please fill in all fields.');
      return;
    }
    
    console.log(username);
  
    axios.post('http://localhost:8000/user/apps', {
      username,
      app_name: newApp.app_name,
      app_username: newApp.app_username,
      app_password: newApp.app_password,
    })
    .then(res => {
      setMsg(res.data.message);
      setNewApp({ app_name: '', app_password: '', app_username: '' });
      return axios.get('http://localhost:8000/user/apps', { params: { username } });
    })
    .then(res => setApps(res.data))
    .catch(err => {
      setMsg('Error adding app.');
      console.error(err);
    });
  };
  

  if (userType === 'admin') {
    return (
      <div className='Dashboard'>
        <h2>Admin Dashboard</h2>
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Created At</th>
              <th>Last Login</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user, index) => (
              <tr key={index}>
                <td>{user.username}</td>
                <td>{new Date(user.created_at).toLocaleString()}</td>
                <td>{user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className='Dashboard'>
      <h2>User Dashboard</h2>
      <form onSubmit={handleAddApp} className='addAppForm'>
        <input
          type='text'
          placeholder='App Name'
          value={newApp.app_name}
          onChange={(e) => setNewApp({ ...newApp, app_name: e.target.value })}
        />
        <input
          type='text'
          placeholder='Username'
          value={newApp.app_username}
          onChange={(e) => setNewApp({ ...newApp, app_username: e.target.value })}
        />
        <input
          type='password'
          placeholder='Password'
          value={newApp.app_password}
          onChange={(e) => setNewApp({ ...newApp, app_password: e.target.value })}
        />
        <button type='submit'>Add App</button>
      </form>
      <p>{msg}</p>
      <table>
        <thead>
          <tr>
            <th>App Name</th>
            <th>Username</th>
            <th>Password</th>
            <th>Added On</th>
          </tr>
        </thead>
        <tbody>
          {apps.map((app, index) => (
            <tr key={index}>
              <td>{app.app_name}</td>
              <td>{app.app_username}</td>
              <td>{app.app_password}</td>
              <td>{new Date(app.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
