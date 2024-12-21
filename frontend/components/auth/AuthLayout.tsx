import Head from "next/head";
import styles from "@/styles/auth.module.css";

interface AuthLayoutProps {
    children: React.ReactNode;
    title: string;
    subtitle?: string;
}

export default function AuthLayout({children, title}: AuthLayoutProps) {
    return (
        <div className={styles.container}>
            <Head>
                <title>{title}</title>
            </Head>
            <div className={styles.card}>
                <h1 className={styles.title}>{title}</h1>
                {children}
            </div>
        </div>
    );
}