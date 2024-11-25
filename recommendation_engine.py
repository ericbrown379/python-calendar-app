from sklearn.preprocessing import StandardScaler
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Tuple


class EventRecommendar:
    def __init__(self):
        self.scaler = StandardScaler()
        self.similarity_threshold = 0.5

    def _extract_features(self, event: Dict) -> np.ndarray:
        """Extract numerical features from event data"""
        try:
            features = []
            # Time of day (normalized to 0-1)
            start_time = datetime.strptime(event['start_time'], '%H:%M:%S')
            time_feature = (start_time.hour * 60 + start_time.minute) / (24 * 60)
            features.append(time_feature)
            
            # Day of week (normalized to 0-1)
            if isinstance(event['date'], str):
                date_obj = datetime.strptime(event['date'], '%Y-%m-%d')
            else:
                date_obj = event['date']
            day_feature = date_obj.weekday() / 7
            features.append(day_feature)
            
            # Duration in hours (normalized to 0-1)
            end_time = datetime.strptime(event['end_time'], '%H:%M:%S')
            duration = (end_time.hour * 60 + end_time.minute) - (start_time.hour * 60 + start_time.minute)
            duration_feature = duration / (24 * 60)
            features.append(duration_feature)
            
            return np.array(features)
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return np.array([0, 0, 0])  # Return default features on error

    def train(self, historical_events: List[Dict]):
        """Train the recommendation engine on historical event data"""
        if not historical_events:
            print("No historical events provided for training")
            return

        try:
            print(f"Training on {len(historical_events)} historical events")
            features = []
            for event in historical_events:
                event_features = self._extract_features(event)
                if event_features is not None:
                    features.append(event_features)

            if features:
                features = np.array(features)
                self.scaler.fit(features)
                self.historical_features = self.scaler.transform(features)
                self.historical_events = historical_events
                print("Training completed successfully")
            else:
                print("No valid features extracted for training")
        except Exception as e:
            print(f"Error during training: {str(e)}")

    def get_recommendations(self, user_id: int, target_date: datetime, limit: int = 3) -> List[Dict]:
        """Generate event recommendations for a specific date"""
        if not hasattr(self, 'historical_events') or not self.historical_events:
            print("No historical data available for recommendations")
            return []

        try:
            recommendations = []
            day_of_week = target_date.weekday()
            
            # Find similar events from history
            for idx, event in enumerate(self.historical_events):
                event_date = datetime.strptime(event['date'], '%Y-%m-%d') if isinstance(event['date'], str) else event['date']
                if event_date.weekday() == day_of_week:
                    similarity_score = self._calculate_similarity(idx)
                    if similarity_score > self.similarity_threshold:
                        recommendations.append({
                            'event': event,
                            'score': similarity_score,
                            'explanation': self._generate_explanation(event, similarity_score)
                        })
            
            # Sort by similarity score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:limit]
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return []

    def _calculate_similarity(self, idx: int) -> float:
        """Calculate similarity score for an event"""
        try:
            similarity = np.mean(1 - np.abs(self.historical_features - self.historical_features[idx]), axis=1)
            return float(similarity.mean())
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0

    def _generate_explanation(self, event: Dict, score: float) -> str:
        """Generate human-readable explanation for recommendation"""
        try:
            explanations = []
            if score > 0.8:
                explanations.append("This event is very similar to your past preferences")
            elif score > 0.6:
                explanations.append("This type of event matches your usual schedule")
            
            time_str = datetime.strptime(event['start_time'], '%H:%M:%S').strftime('%I:%M %p')
            explanations.append(f"You often schedule events around {time_str}")
            
            return " and ".join(explanations)
        except Exception as e:
            print(f"Error generating explanation: {str(e)}")
            return "Recommended based on your past events"

    def update_model(self, new_event: Dict, user_feedback: str):
        """Update model with new event data and user feedback"""
        if not new_event:
            return

        try:
            features = self._extract_features(new_event)
            if features is not None:
                if not hasattr(self, 'historical_features'):
                    self.historical_features = self.scaler.fit_transform(features.reshape(1, -1))
                else:
                    self.historical_features = np.vstack([
                        self.historical_features,
                        self.scaler.transform(features.reshape(1, -1))
                    ])
                
                if not hasattr(self, 'historical_events'):
                    self.historical_events = [new_event]
                else:
                    self.historical_events.append(new_event)
                
                # Adjust similarity threshold based on feedback
                if user_feedback == 'positive':
                    self.similarity_threshold = max(0.6, self.similarity_threshold - 0.02)
                elif user_feedback == 'negative':
                    self.similarity_threshold = min(0.9, self.similarity_threshold + 0.02)
                
                print("Model updated successfully")
        except Exception as e:
            print(f"Error updating model: {str(e)}")