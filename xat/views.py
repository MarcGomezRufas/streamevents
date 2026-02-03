# xat/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from events.models import Event
from .models import XatMessage
from .forms import XatMessageForm

@login_required
@require_POST
def xat_send_message(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if event.status != 'live':
        return JsonResponse({'success': False, 'error': 'L’esdeveniment no està en directe.'}, status=400)
    
    form = XatMessageForm(request.POST)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.user = request.user
        msg.event = event
        msg.save()
        return JsonResponse({
            'success': True,
            'message': {
                'id': msg.id,
                'user': msg.user.username,
                'display_name': msg.get_user_display_name(),
                'message': msg.message,
                'created_at': msg.get_time_since(),
                'can_delete': msg.can_delete(request.user),
                'is_highlighted': msg.is_highlighted
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

def xat_load_messages(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    messages = XatMessage.objects.filter(event=event, is_deleted=False).order_by('created_at')[:50]
    data = [{
        'id': m.id,
        'user': m.user.username,
        'display_name': m.get_user_display_name(),
        'message': m.message,
        'created_at': m.get_time_since(),
        'can_delete': m.can_delete(request.user),
        'is_highlighted': m.is_highlighted
    } for m in messages]
    return JsonResponse({'messages': data})

@login_required
@require_POST
def xat_delete_message(request, message_pk):
    msg = get_object_or_404(XatMessage, pk=message_pk)
    if not msg.can_delete(request.user):
        return JsonResponse({'success': False, 'error': 'No tens permís.'}, status=403)
    msg.is_deleted = True
    msg.save()
    return JsonResponse({'success': True})

@login_required
@require_POST
def xat_highlight_message(request, message_pk):
    msg = get_object_or_404(XatMessage, pk=message_pk)
    if msg.event.creator != request.user:
        return JsonResponse({'success': False, 'error': 'Només el creador pot destacar.'}, status=403)
    msg.is_highlighted = not msg.is_highlighted
    msg.save()
    return JsonResponse({'success': True, 'is_highlighted': msg.is_highlighted})