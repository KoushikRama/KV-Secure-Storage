import React, { useState } from 'react';
import axios from 'axios';
import './register.css';
import { Link } from 'react-router-dom';

export const Register = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState('');
  const [errors, setErrors] = useState({
    username:'',
    password:''
    });
  const handleRegister = async (e) => {
    e.preventDefault();
    let formErrors = {...errors}
    if(!username){
        formErrors.username='*required'
    } else {
        formErrors.username='' 
    }

    if(!password){
        formErrors.password='*required'
    } else {
        formErrors.password='' 
    }

    if(Object.values(formErrors).some((error) => error!=="" )){
        setErrors(formErrors);
        return;
    }
    try {
      const response = await axios.post('http://localhost:8000/auth/register/', {
        username,
        password,
      });

      setMsg(response.data.message);
    } catch (error) {
      setMsg(error.response?.data?.error || 'An error occurred');
    }
  };

  return (
    <div>
    <h1>KV Secure Storage</h1>
    <div className='RegisterCard'>

      <form onSubmit={handleRegister}>
      <h2 className='RegisterTitle'>Register</h2>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
        />
        {errors.username && <span className="errors">{errors.username}</span>}
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        {errors.password && <span className="errors">{errors.password}</span>}
        <button type="submit">Register</button>
        <div id='dont_have'><p>Already Registered?<Link to='/'> Login Now</Link> </p></div>

      </form>
      <p>{msg}</p>
    </div>
    </div>
  );
}
