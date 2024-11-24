from sklearn.preprocessing import StandardScaler
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Tuple


class EventRecommendar:
    def __init__(self):
        self.scaler = StandardScaler()
        self.similarity_threshold = 0.7


    def extract_features(self, event: Dict) -> np.ndarray:
        "Extract numbered features from event data"
        features = []
        # Time of day (normilized to 0-1)
        start_time = datetime.strptime(event['start_time'], ["%H:%M:%S"])
        time_feature = (start_time.hour * 60 + start_time.minute) / (24 * 60)
        features.append(time_feature)

        # Day of Week (normilized to 0-1)
        date = datetime.strptime(event['date'], '%Y-%m-%d')
        day_feature = date.weekday() / 7
        features.append(day_feature)

        # Duration in hours (normalized to 0-1)
        end_time = datetime.strptime(event['start_time'], ["%H:%M:%S"])
        duration = (end_time.hour * 60 + end_time.minute) - (start_time.hour * 60 + start_time.minute)
        duration_feature = duration / (24 * 60)
        features.append(duration_feature)

        return np.array(features)
    
    def train(self, historical_events: List[Dict]):
        """Train the recommendation engine on historical event data""" 
        if not historical_events:
            return


        features = np.array([self._extract_features(event) for event in historical_events])
        self.scaler.fit(features)
        self.historical_features = self.scaler.transform(features)
        self.historical_events = historical_events


    def get_recommendations(self, user_id: int, date: datetime, limit: int = 3) -> List[Dict]:
        """Generate event recommendations for a specific date"""
        if not hasattr(self, 'historical_events'):
            return []
        
        recommendations = []
        day_of_week = date.weekday()

        #Find similar events from history
        for idx, event in enumerate(self.historical_events):
            event_date = datetime.strptime(event['date'], '%Y-%m-%d')
            if event_date.weekday() == day_of_week:
                similarity_score = self._calculate_similarity(idx)
                if similarity_score > self.similarity_threshold:
                    recommendations.append({
                        'event': event,
                        'score': similarity_score,
                        'explanation': self._generate_explanation(event, similarity_score)
                    })


         # Sort by similarity score and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    def calculate_similarity(self, idx: int) -> float:
        """Calculate similarity score for an event"""
        return float(np.mean(1 - np.abs(self.historical_features - self.historical_features[idx]), axis=1).mean())
    
    def _generate_explanation(self, event: Dict, score: float) -> str:
        """Generate human-readable explanation for recommendation"""
        explanations = []
        if score > 0.8:
            explanations.append("This event is very similar to your past preferences")
        elif score > 0.6:
            explanations.append("This type of event matches your usual schedule")
            
        time_str = datetime.strptime(event['start_time'], '%H:%M:%S').strftime('%I:%M %p')
        explanations.append(f"You often schedule events around {time_str}")
        
        return " and ".join(explanations)

    def update_model(self, new_event: Dict, user_feedback: str):
        """Update model with new event data and user feedback"""
        if new_event:
            features = self._extract_features(new_event)
            self.historical_features = np.vstack([self.historical_features, self.scaler.transform(features.reshape(1, -1))])
            self.historical_events.append(new_event)
            
            # Adjust similarity threshold based on feedback
            if user_feedback == 'positive':
                self.similarity_threshold = max(0.6, self.similarity_threshold - 0.02)
            elif user_feedback == 'negative':
                self.similarity_threshold = min(0.9, self.similarity_threshold + 0.02)






