# events/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm

def event_list_view(request):
    form = EventSearchForm(request.GET or None)
    qs = Event.objects.select_related('creator').all()

    # Filtre per cerca
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if status:
            qs = qs.filter(status=status)
        if date_from:
            qs = qs.filter(scheduled_date__date__gte=date_from)
        if date_to:
            qs = qs.filter(scheduled_date__date__lte=date_to)

    # Esdeveniments destacats al principi
    featured = qs.filter(is_featured=True)[:4]
    qs = qs.order_by('-is_featured','-created_at')

    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/event_list.html', {'page_obj': page_obj, 'form': form, 'featured': featured})

def event_detail_view(request, pk):
    event = get_object_or_404(Event.objects.select_related('creator'), pk=pk)
    is_creator = request.user.is_authenticated and (request.user == event.creator)
    embed_url = event.get_stream_embed_url()
    return render(request, 'events/event_detail.html', {'event': event, 'is_creator': is_creator, 'embed_url': embed_url})

@login_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.creator = request.user
            # títol únic per usuari: comprovar aquí
            if Event.objects.filter(creator=request.user, title__iexact=ev.title).exists():
                form.add_error('title', "Ja tens un esdeveniment amb aquest títol.")
            else:
                ev.save()
                messages.success(request, "Esdeveniment creat correctament.")
                return redirect(ev.get_absolute_url())
    else:
        form = EventCreationForm()
    return render(request, 'events/event_form.html', {'form': form})

@login_required
def event_update_view(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    if ev.creator != request.user:
        messages.error(request, "Només el creador pot editar aquest esdeveniment.")
        return redirect(ev.get_absolute_url())

    # no permet canviar la data si ja està en directe
    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=ev)
        if form.is_valid():
            new_date = form.cleaned_data.get('scheduled_date')
            new_status = form.cleaned_data.get('status')
            if ev.is_live and new_date and new_date != ev.scheduled_date:
                form.add_error('scheduled_date', "No es pot canviar la data mentre està en directe.")
            else:
                # només el creador pot canviar l'estat (ja és el creador)
                form.save()
                messages.success(request, "Esdeveniment actualitzat.")
                return redirect(ev.get_absolute_url())
    else:
        form = EventUpdateForm(instance=ev)
    return render(request, 'events/event_form.html', {'form': form, 'event': ev})

@login_required
def event_delete_view(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    if ev.creator != request.user:
        messages.error(request, "Només el creador pot eliminar aquest esdeveniment.")
        return redirect(ev.get_absolute_url())

    if request.method == 'POST':
        ev.delete()
        messages.success(request, "Esdeveniment eliminat.")
        return redirect('events:event_list')

    return render(request, 'events/event_confirm_delete.html', {'event': ev})

@login_required
def my_events_view(request):
    qs = Event.objects.filter(creator=request.user).order_by('-created_at')
    status = request.GET.get('status')
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'events/my_events.html', {'page_obj': page_obj})

def events_by_category_view(request, category):
    category_keys = [c[0] for c in Event._meta.get_field('category').choices]
    if category not in category_keys:
        messages = ("Categoria no vàlida.")
        return redirect('events:event_list')
    qs = Event.objects.filter(category=category).order_by('-created_at')
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'events/event_list.html', {'page_obj': page_obj})
