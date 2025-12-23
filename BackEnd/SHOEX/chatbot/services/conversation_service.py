from django.utils import timezone


def get_or_create_session(request):
    """Get or create chat session ID from request."""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    return session_key


def save_message(session_id, role, content, intent=None):
    """Save chat message to session or database. Currently stores in session only."""
    # For now, we're not persisting to database
    # Can implement ChatMessage model later if needed
    pass
