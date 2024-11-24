from datetime import datetime, timedelta
from recommendation_engine import EventRecommendar
from typing import List, Dict, Tuple
from models import EventSuggestion, Event, db 

class EventsuggestionService:
    def __init__(self):
        self.recommendar = EventRecommendar()
        self.referesh_interval = timedelta(hours=24)
        self.last_referesh = None


    def get_suggestions(self, user_id: int, date: datetime) -> List[Dict]:
        """Get event sugestion for a user"""
        # Check if we need to refresh suggestions
        if self.__should_refresh_suggestions():
            self.referesh_interval()

        
        # Get existing non-dismissed suggestions
        suggestions = EventSuggestion.query.filter_by(
            user_id=user_id,
            suggested_date=date,
            is_dismissed=False
        ).all()

        if not suggestions:
            # Generate new suggestions
            historical_events = Event.query.filter_by(user_id=user_id).all()
            self.recommender.train([event.__dict__ for event in historical_events])
            new_suggestions = self.recommender.get_recommendations(user_id, date)
            

            for suggestion in new_suggestions:
                event_suggestion = EventSuggestion(
                    user_id=user_id,
                    event_name=suggestion['event']['name'],
                    suggested_date=date,
                    suggested_time=suggestion['event']['start_time'],
                    explanation=suggestion['explanation'],
                    similarity_score=suggestion['score']
                )
                db.session.add(event_suggestion)
            db.session.commit()

            suggestions = EventSuggestion.query.filter_by(
                user_id=user_id,
                suggested_date=date,
                is_dismissed=False,
            ).all()


            return suggestions
    
    def dimiss_suggestion(self, suggestion_id: int, user_feedback: str=None):
        """Dimiss  suggetion and optionally providde feedback"""
        suggestion = EventSuggestion.query.get(suggestion_id)
        if suggestion:
            suggestion.is_dimissed = True
            if user_feedback:
                self.recommender.update_model(suggestion.__dict__,user_feedback)
            db.session.commit()


    def _should_refresh_suggestions(self) -> bool:
        """Check if suggestions should be refreshed"""
        return(
            not self.last_referesh or 
            datetime.utcnow() - self.last_refresh > self.referesh_interval
        )
    
    def _refresh_suggestions(self):
        """Refresh all suggestions"""
        self.last_refresh = datetime.utcnow()
        # Delete old dismissed suggestions
        old_date = datetime.utcnow()
        EventSuggestion.query.filter(
            EventSuggestion.created_at < old_date,
            EventSuggestion.is_dismissed == True
        ).delete()
        db.session.commit()
