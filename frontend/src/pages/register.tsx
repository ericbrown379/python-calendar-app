import { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import AuthLayout from '@/components/auth/AuthLayout';
import styles from '@/styles/auth.module.css';
import { CalendarBackground } from '@/components/auth/CalendarBackground';

export default function Register() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        privacyPolicy: false
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        // Validate password
        const forbiddenChars = new Set("#$%^&*(){}[]<>?");
        const hasSpecialChar = /[!@#$%^&+=]/.test(formData.password);
        const hasForbiddenChar = [...formData.password].some(char => forbiddenChars.has(char));

        if (!hasSpecialChar) {
            setError('Password must contain at least one special character (!, @, #, etc.)');
            setIsLoading(false);
            return;
        }

        if (hasForbiddenChar) {
            setError('Password contains forbidden characters (#$%^&*(){}[]<>?)');
            setIsLoading(false);
            return;
        }

        if (!formData.privacyPolicy) {
            setError('Please accept the privacy policy');
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.email,
                    username: formData.username,
                    password: formData.password
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Registration failed');
            }

            // Registration successful
            router.push('/login?registered=true');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Registration failed');
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
                <i className={styles.ringCircle} style={{"--clr": "#00ff0a"} as any} />
                <i className={styles.ringCircle} style={{"--clr": "#ff0057"} as any} />
                <i className={styles.ringCircle} style={{"--clr": "#fffd44"} as any} />
                <div className={styles.loginWrapper}>
                    <AuthLayout title="Create Account">
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
                                    id="privacyPolicy"
                                    name="privacyPolicy"
                                    checked={formData.privacyPolicy}
                                    onChange={handleChange}
                                    className={styles.checkbox}
                                    disabled={isLoading}
                                />
                                <label htmlFor="privacyPolicy" className={styles.checkboxLabel}>
                                    I agree to the <Link href="/privacy" className={styles.link}>Privacy Policy</Link>
                                </label>
                            </div>

                            <button 
                                type="submit" 
                                className={`${styles.button} ${isLoading ? styles.loading : ''}`}
                                disabled={isLoading}
                            >
                                {isLoading ? 'Creating Account...' : 'Register'}
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