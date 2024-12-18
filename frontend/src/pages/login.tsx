import { useRouter } from 'next/router';
import { useState, FormEvent } from 'react';
import AuthLayout from '@/components/auth/AuthLayout';
import styles from '@/styles/auth.module.css';
import { CalendarBackground } from '@/components/auth/CalendarBackground';
import Link from 'next/link';

export const dynamic = 'force-static';

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
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        credentials: 'include',
      });

      const data = await response.json();

      if (response.status === 401) {
        setError('Invalid username or password');
        setIsLoading(false);
        return;
      }

      if (!response.ok) {
        throw new Error(data.message || 'Login failed');
      }

      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('isLoggedIn', 'true');
        
        await router.push('/calendar');
      } else {
        throw new Error('No user data received');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'Login failed');
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
        <i className={styles.ringCircle} style={{"--clr": "#00ff0a"} as any} />
        <i className={styles.ringCircle} style={{"--clr": "#ff0057"} as any} />
        <i className={styles.ringCircle} style={{"--clr": "#fffd44"} as any} />
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
                  Don't have an account? Register here
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