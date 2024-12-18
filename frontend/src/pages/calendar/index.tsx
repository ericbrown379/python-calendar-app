import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

export default function Calendar() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState<any>(null);

  useEffect(() => {
    const checkAuth = () => {
      const user = localStorage.getItem('user');
      console.log('Checking auth state:', user);

      if (!user) {
        console.log('No user found, redirecting to login');
        router.push('/login');
        return;
      }

      try {
        const userData = JSON.parse(user);
        setUserData(userData);
        setIsLoading(false);
      } catch (e) {
        console.error('Error parsing user data:', e);
        localStorage.removeItem('user');
        router.push('/login');
      }
    };

    checkAuth();
  }, [router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Welcome, {userData?.username}!</h1>
      <div>
        {/* Your calendar content here */}
        <p>Your calendar will be displayed here.</p>
      </div>
    </div>
  );
} 