import React, { useState } from 'react';
import axios from 'axios';
import './login.css';
import { Link } from 'react-router-dom';
import { useNavigate } from "react-router-dom";

export const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState('');
  const [errors, setErrors] = useState({
    username:'',
    password:''
    });
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [dialogMessage, setDialogMessage] = useState("");

  const closeDialog = () => {
      setIsDialogOpen(false);
      if (dialogMessage.includes('Login')) {
          navigate('/dashboard');
      } 
  }
  const handleLogin = async (e) => {
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
      const response = await axios.post('http://localhost:8000/auth/login/', {
        username,
        password
      });
      setMsg(response.data.message);
      setIsDialogOpen(true);
      setDialogMessage(response.data.message);
      localStorage.setItem('username', response.data.username);
      localStorage.setItem('user_type', response.data.user_type);

      
    } catch (error) {
      setMsg(error.response?.data?.error || 'An error occurred');
    }
  };

  return (
    <div>
          <h1>KV Secure Storage</h1>

    <div className='LoginCard'>
      
      <form onSubmit={handleLogin}>
      <h2 className='LoginTitle'>Login</h2>
        <input
          type="text"
          name='username'
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

        <button type="submit">Login</button>
        <div id='dont_have'><p>Don't have an Account?<Link to='/register'> Register for Free</Link> </p></div>

      </form>
      {isDialogOpen && (
                <div className="dialogBoxLogin">
                    <div className="dialogContentLogin">
                        <p>{msg}</p>
                        <button onClick={closeDialog}>OK</button>
                    </div>
                </div>
            )}
    </div>
    </div>
  );
}
