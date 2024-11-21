import { createSlice, PayloadAction } from "@reduxjs/toolkit";

// Define the Event interface
interface Event {
    id: string;
    title: string;
    startTime: string;
    endTime: string;
}

// Initial state: An empty array of Event
const initialState: Event[] = [];

// Create the Redux slice
const eventsSlice = createSlice({
    name: "events", // Name of the slice
    initialState,
    reducers: {
        // Add a new event
        addEvent(state, action: PayloadAction<Event>) {
            state.push(action.payload);
        },
        // Update an existing event by ID
        updateEvent(state, action: PayloadAction<Event>) {
            const index = state.findIndex((e: Event) => e.id === action.payload.id);
            if (index >= 0) {
                state[index] = action.payload;
            }
        },
        // Delete an event by ID
        deleteEvent(state, action: PayloadAction<string>) {
            return state.filter((e: Event) => e.id !== action.payload);
        },
    },
});

// Export actions and reducer
export const { addEvent, updateEvent, deleteEvent } = eventsSlice.actions;
export default eventsSlice.reducer;