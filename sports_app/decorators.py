from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(user):
        return user.is_authenticated() and (user.groups.filter(name__in=group_names).exists() or user.is_superuser)
    return user_passes_test(in_groups)