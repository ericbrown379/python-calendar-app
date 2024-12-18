import { useState } from "react";
import Link from "next/link";
import styles from "@/styles/auth.module.css";

interface LoginFormProps {
    onSubmit: (username: string, password: string) => Promise<void>;
    error?: string;
}

export default function LoginForm({ onSubmit, error }: LoginFormProps){
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        await onSubmit(username, password);
        setIsLoading(false);
    };

    return (
        <form onSubmit={handleSubmit} className={styles.form}>
            {error && <div className={styles.error}>{error}</div>}

            <div className={styles.inputGroup}>
                <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
                className={styles.input}
                required
                />
            </div>

            <div className={styles.inputGroup}>
                <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className={styles.input}
                required
                />
            </div>
            <button
            type="submit"
            className={styles.submitButton}
            disabled={isLoading}
            >
                {isLoading ? "Logging in..." : "Login"}
            </button>

            <div className={styles.links}>
                <Link href="/auth/register">
                Don't have an account? Register
                </Link>
                <Link href="/auth/forgot-password">
                Forgot password?
                </Link>
            </div>
        </form>
    );
}
