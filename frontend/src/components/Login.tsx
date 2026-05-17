import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { LogIn, User, Lock } from 'lucide-react';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username && password) {
      login(username);
    }
  };

  return (
    <div className="min-height-screen flex items-center justify-center bg-gray-100 px-4 py-12 dark:bg-gray-900 w-full h-full min-h-screen">
      <div className="w-full max-w-md space-y-8 bg-white p-10 rounded-xl shadow-lg dark:bg-gray-800">
        <div className="text-center">
          <LogIn className="mx-auto h-12 w-12 text-blue-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            FHIR Patient Portal
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Sign in to access your healthcare data
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div className="relative">
              <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-10 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-10 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition duration-150 ease-in-out"
            >
              Sign in
            </button>
          </div>
        </form>
        <div className="mt-4 text-center text-xs text-gray-500">
          Tip: Any username/password will work for this demo.
        </div>
      </div>
    </div>
  );
};

export default Login;
