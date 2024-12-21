'use client';

import { useRouter } from 'next/navigation'; // Note: Next 13+ uses 'next/navigation'
import { useState, FormEvent, CSSProperties } from 'react';
import AuthLayout from '@/components/auth/AuthLayout';
import styles from '@/styles/auth.module.css';
import { CalendarBackground } from '@/components/auth/CalendarBackground';
import Link from 'next/link';
import { ApiService } from '@/services/api';

type RingStyle = CSSProperties & {
  '--clr': string;
}

export default function Login() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await ApiService.login(formData.username, formData.password);

      if (response.user) {
        // Store user data if needed
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('isLoggedIn', 'true');
        await router.push('/calendar');
      } else {
        throw new Error('No user data received');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className={styles.container}>
      <CalendarBackground />
      <div className={styles.ring}>
        <i className={styles.ringCircle} style={{'--clr': '#00ff0a'} as RingStyle} />
        <i className={styles.ringCircle} style={{'--clr': '#ff0057'} as RingStyle} />
        <i className={styles.ringCircle} style={{'--clr': '#fffd44'} as RingStyle} />
        <div className={styles.loginWrapper}>
          <AuthLayout title="Login">
            <form onSubmit={handleSubmit} className={styles.form}>
              {error && (
                <div className={styles.error}>
                  {error}
                </div>
              )}
              
              <div className={styles.inputGroup}>
                <label htmlFor="username" className={styles.label}>
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className={styles.input}
                  disabled={isLoading}
                  required
                />
              </div>

              <div className={styles.inputGroup}>
                <label htmlFor="password" className={styles.label}>
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={styles.input}
                  disabled={isLoading}
                  required
                />
              </div>

              <button 
                type="submit" 
                className={`${styles.button} ${isLoading ? styles.loading : ''}`}
                disabled={isLoading}
              >
                {isLoading ? 'Logging in...' : 'Login'}
              </button>

              <div className={styles.links}>
                <Link href="/register" className={styles.link}>
                Don&apos;t have an account? Register here
                </Link>
                <Link href="/forgot-password" className={styles.link}>
                  Forgot password?
                </Link>
              </div>
            </form>
          </AuthLayout>
        </div>
      </div>
    </div>
  );
}
