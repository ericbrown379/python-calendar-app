import Head from "next/head";
import Image from "next/image";
import styles from "@/styles/auth.module.css";


interface AuthLayoutProps {
    children: React.ReactNode;
    title: string;
}

export default function AuthLayout({children, title}: AuthLayoutProps) {
    return(
        <div className={styles.container}>
            <Head>
                <title>{title}</title>
            </Head>

            <div className={styles.card}>
                <div className={styles.logoContainer}>
                    <Image
                    src="/calendar-hive-logo.png"
                    alt="Calendar Hive Logo"
                    width={120}
                    height={120}
                    priority
                    />
                </div>
                <h1 className={styles.title}>{title}</h1>
                {children}
            </div>
        </div>
    );
}
