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


# Salles/views.py (within the 'reserver' function)

def reserver(request, salle_id):
    """Page 3: Réserver une salle"""
    salle = get_object_or_404(Salle, pk=salle_id)
    if request.method == 'POST':
        # 1. Initialize the form with POST data and the Salle object
        form = ReservationForm(request.POST)
        reservation_instance = form.instance
        reservation_instance.salle = salle

        # 2. **CRITICAL FIX**: Manually assign the salle object to the form's instance
        #    before validation runs (which calls Reservation.clean())
        if form.is_valid():
            # The 'salle' field is an instance attribute on the Reservation object
            # that is about to be saved. We set it here.
            reservation = form.save(commit=False)

            # The original logic checks availability *after* is_valid() which is correct
            # for separation of concerns, but now the Model's clean() will also run the check.

            # Check availability *again* (although clean() should handle it)
            if salle.est_disponible(reservation.date, reservation.heure_debut, reservation.heure_fin):
                reservation.save()

                # ... (rest of the successful logic)
                reservation.refresh_from_db()
                print(f"DEBUG - Reservation ID: {reservation.id}")
                print(f"DEBUG - Salle ID: {reservation.salle_id}")
                try:
                    print(f"DEBUG - Salle Nom: {reservation.salle.nom}")
                except Exception as e:
                    print(f"DEBUG - ERREUR lors de l'accès à reservation.salle: {e}")

                messages.success(
                    request,
                    f'Réservation confirmée pour {salle.nom} le {reservation.date}'
                )
                return redirect('salles:confirmation', reservation_id=reservation.id)
            else:
                # If availability check fails (which should be caught by clean() too)
                messages.error(
                    request,
                    'Cette salle est déjà réservée pour ce créneau horaire.'
                )
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = ReservationForm(initial={'salle': salle})  # Optional: pre-fill/set initial values

    context = {
        'salle': salle,
        'form': form,
    }
    return render(request, 'Salles/reserver.html', context)

def confirmation(request, reservation_id):
    """Page 4: Confirmation de réservation"""
    reservation = get_object_or_404(Reservation, pk=reservation_id)

    # DÉBOGAGE: Vérifier l'accès à la salle
    print(f"DEBUG Confirmation - Reservation ID: {reservation.id}")
    print(f"DEBUG Confirmation - Salle ID: {reservation.salle_id}")
    try:
        salle_nom = reservation.salle.nom
        print(f"DEBUG Confirmation - Salle Nom: {salle_nom}")
    except Exception as e:
        print(f"DEBUG Confirmation - ERREUR: {e}")

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
        email = reservation.email
        reservation.validee = False
        reservation.save()
        messages.success(request, 'Réservation annulée avec succès.')
        return redirect(f'/salles/mes-reservations/?email={email}')

    return redirect('salles:liste_salles')