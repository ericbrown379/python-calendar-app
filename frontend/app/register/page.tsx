'use client';

import { useRouter } from 'next/navigation';
import { useState, FormEvent, CSSProperties } from 'react';
import AuthLayout from '@/components/auth/AuthLayout';
import styles from '@/styles/auth.module.css';
import { CalendarBackground } from '@/components/auth/CalendarBackground';
import Link from 'next/link';
import { ApiService } from '@/services/api';

type RingStyle = CSSProperties & {
  '--clr': string;
}

export default function Register() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    privacy: false
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!formData.privacy) {
      setError('Please accept the privacy policy');
      return;
    }
    setError('');
    setIsLoading(true);

    try {
      await ApiService.register(formData.username, formData.email, formData.password);
      router.push('/login');
    } catch (err) {
      console.error('Registration error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
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
          <AuthLayout title="Register">
            <form onSubmit={handleSubmit} className={styles.form}>
              {error && (
                <div className={styles.error}>
                  {error}
                </div>
              )}
              
              <div className={styles.inputGroup}>
                <label htmlFor="email" className={styles.label}>
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={styles.input}
                  disabled={isLoading}
                  required
                />
              </div>

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

              <div className={styles.checkboxGroup}>
                <input
                  type="checkbox"
                  id="privacy"
                  name="privacy"
                  checked={formData.privacy}
                  onChange={handleChange}
                  className={styles.checkbox}
                  disabled={isLoading}
                />
                <label htmlFor="privacy" className={styles.checkboxLabel}>
                  I agree to the <Link href="/privacy" className={styles.link}>Privacy Policy</Link>
                </label>
              </div>

              <button 
                type="submit" 
                className={`${styles.button} ${isLoading ? styles.loading : ''}`}
                disabled={isLoading}
              >
                {isLoading ? 'Registering...' : 'Register'}
              </button>

              <div className={styles.links}>
                <Link href="/login" className={styles.link}>
                  Already have an account? Login here
                </Link>
              </div>
            </form>
          </AuthLayout>
        </div>
      </div>
    </div>
  );
}