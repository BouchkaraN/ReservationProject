from django.contrib import admin
from .models import Salle, Reservation

@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'capacite', 'etage', 'equipements']
    list_filter = ['etage', 'capacite']
    search_fields = ['nom', 'equipements']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['salle', 'nom_utilisateur', 'date', 'heure_debut',
                    'heure_fin', 'validee']
    list_filter = ['validee', 'date', 'salle']
    search_fields = ['nom_utilisateur', 'email', 'motif']
    date_hierarchy = 'date'