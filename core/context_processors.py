def theme_processor(request):
    """
    Injects the active tenant's theme configuration into the context.
    Requires `request.user.university` to be available.
    """
    theme = {
        'primary_color': '#22c55e',  # default brand 500
        'secondary_color': '#16a34a', # default brand 600
        'logo_url': None,
    }

    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'university') and request.user.university:
            uni = request.user.university
            theme['primary_color'] = uni.primary_color
            theme['secondary_color'] = uni.secondary_color
            theme['logo_url'] = uni.logo_url

    return {'theme': theme}
