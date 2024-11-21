import { useEffect } from "react";
import { io } from "socket.io-client";


const socket = io("http://127.0.0.1:5000"); // Replace with your server URL if different

export const useSocket = (event: string, callback: (data: any) => void) => {
    useEffect(() => {
        // Listen for the event
        socket.on(event, callback);

        // Cleanup the listener on unmount
        return () => {
            socket.off(event);
        };
    }, [event, callback]);
};

export default socket;