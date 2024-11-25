from datetime import datetime, timedelta
from typing import List, Dict
from models import EventSuggestion, Event, db
from recommendation_engine import EventRecommendar

class EventsuggestionService:
    def __init__(self):
        self.recommender = EventRecommendar()
        self.refresh_interval = timedelta(hours=24)
        self.last_refresh = None

    def get_suggestions(self, user_id: int, target_date: datetime) -> List[EventSuggestion]:
        """Get event suggestions for a user"""
        try:
            print(f"Getting suggestions for user {user_id} on {target_date}")
            
            # Get existing non-dismissed suggestions
            suggestions = EventSuggestion.query.filter_by(
                user_id=user_id,
                suggested_date=target_date,
                is_dismissed=False
            ).all()

            if not suggestions:
                print("No existing suggestions found, generating new ones")
                # Get historical events for training
                historical_events = Event.query.filter_by(user_id=user_id).all()
                if historical_events:
                    # Convert events to dictionary format for recommender
                    event_dicts = [{
                        'name': event.name,
                        'date': event.date,
                        'start_time': event.start_time,
                        'end_time': event.end_time,
                        'location': event.location
                    } for event in historical_events]

                    # Train recommender and get suggestions
                    self.recommender.train(event_dicts)
                    new_suggestions = self.recommender.get_recommendations(user_id, target_date)

                    # Create suggestion objects
                    for sugg in new_suggestions:
                        suggestion = EventSuggestion(
                            user_id=user_id,
                            event_name=sugg['event']['name'],
                            suggested_date=target_date,
                            suggested_time=sugg['event']['start_time'],
                            explanation=sugg['explanation'],
                            similarity_score=sugg['score']
                        )
                        db.session.add(suggestion)

                    try:
                        db.session.commit()
                        print("New suggestions saved successfully")
                        suggestions = EventSuggestion.query.filter_by(
                            user_id=user_id,
                            suggested_date=target_date,
                            is_dismissed=False
                        ).all()
                    except Exception as e:
                        print(f"Error saving suggestions: {str(e)}")
                        db.session.rollback()

            return suggestions

        except Exception as e:
            print(f"Error getting suggestions: {str(e)}")
            return []

    def dismiss_suggestion(self, suggestion_id: int, user_feedback: str = None):
        """Dismiss a suggestion and optionally provide feedback"""
        try:
            suggestion = EventSuggestion.query.get(suggestion_id)
            if suggestion:
                suggestion.is_dismissed = True
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error dismissing suggestion: {str(e)}")

    def should_refresh(self) -> bool:
        """Check if suggestions should be refreshed"""
        if self.last_refresh is None:
            return True
        time_since_refresh = datetime.utcnow() - self.last_refresh
        return time_since_refresh > self.refresh_interval

    def refresh_suggestions(self):
        """Refresh suggestions and clean up old ones"""
        try:
            # Update last refresh time
            self.last_refresh = datetime.utcnow()
            
            # Delete old dismissed suggestions
            old_date = datetime.utcnow() - timedelta(days=7)
            EventSuggestion.query.filter(
                EventSuggestion.created_at < old_date,
                EventSuggestion.is_dismissed == True
            ).delete()
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error refreshing suggestions: {str(e)}")