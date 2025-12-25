def user_flags(request):
    """Expose simple session-based flags to templates.

    Provides:
    - is_service_provider (bool)
    - is_user (bool)
    - logged_in_username
    - logged_in_user_id
    """
    return {
        'is_service_provider': request.session.get('is_service_provider', False),
        'is_user': request.session.get('is_user', False),
        'logged_in_username': request.session.get('logged_in_username'),
        'logged_in_user_id': request.session.get('logged_in_user_id'),
    }