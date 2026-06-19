from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Notification


@login_required
def notification_list_view(request):

    notifications = Notification.objects.filter(
        user=request.user
    )

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    return render(
        request,
        'notifications/list.html',
        {
            'notifications': notifications
        }
    )