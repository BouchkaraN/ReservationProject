from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import Salle, Reservation
from .forms import ReservationForm


def liste_salles(request):
    """Page 1: Liste de toutes les salles"""
    salles = Salle.objects.all().order_by('etage', 'nom')

    # Filtre de recherche
    search = request.GET.get('search', '')
    if search:
        salles = salles.filter(
            Q(nom__icontains=search) |
            Q(equipements__icontains=search)
        )

    # Filtre par capacité
    capacite_min = request.GET.get('capacite', '')
    if capacite_min:
        salles = salles.filter(capacite__gte=capacite_min)

    context = {
        'salles': salles,
        'search': search,
        'capacite_min': capacite_min,
    }
    return render(request, 'Salles/liste_salles.html', context)


def detail_salle(request, salle_id):
    """Page 2: Détail d'une salle avec ses réservations"""
    salle = get_object_or_404(Salle, pk=salle_id)

    # Réservations futures pour cette salle
    reservations = Reservation.objects.filter(
        salle=salle,
        date__gte=date.today(),
        validee=True
    ).order_by('date', 'heure_debut')[:10]

    context = {
        'salle': salle,
        'reservations': reservations,
    }
    return render(request, 'Salles/detail_salle.html', context)


def reserver(request, salle_id):
    salle = get_object_or_404(Salle, pk=salle_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST, salle=salle)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.salle = salle
            if salle.est_disponible( reservation.date,reservation.heure_debut,reservation.heure_fin ):
                reservation.save()
                messages.success(request,
                    f'Réservation confirmée pour {salle.nom} le {reservation.date}')
                return redirect('salles:confirmation', reservation_id=reservation.id)
            else:
                messages.error(
                    request,
                    'Cette salle est déjà réservée pour ce créneau horaire.'
                )
    else:
        form = ReservationForm(salle=salle)
    context = {
        'salle': salle,
        'form': form,}
    return render(request, 'Salles/reserver.html', context)


def confirmation(request, reservation_id):
    """Page 4: Confirmation de réservation"""
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    context = {
        'reservation': reservation,
    }
    return render(request, 'Salles/confirmation.html', context)


def mes_reservations(request):
    """Page 5: Recherche de réservations par email"""
    reservations = []
    email = request.GET.get('email', '')

    if email:
        reservations = Reservation.objects.filter(
            email=email,
            validee=True
        ).order_by('-date', '-heure_debut')

    context = {
        'reservations': reservations,
        'email': email,
    }
    return render(request, 'Salles/mes_reservations.html', context)


def annuler_reservation(request, reservation_id):
    """Annuler une réservation"""
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    if request.method == 'POST':
        reservation.validee = False
        reservation.save()
        messages.success(request, 'Réservation annulée avec succès.')
        return redirect('salles:mes_reservations') + f'?email={reservation.email}'

    return redirect('salles:liste_salles')