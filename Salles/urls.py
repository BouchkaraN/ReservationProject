from django.urls import path
from . import views

app_name = 'salles'

urlpatterns = [
    path('', views.liste_salles, name='liste_salles'),
    path('salle/<int:salle_id>/', views.detail_salle, name='detail_salle'),
    path('salle/<int:salle_id>/reserver/', views.reserver, name='reserver'),
    path('confirmation/<int:reservation_id>/', views.confirmation, name='confirmation'),
    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('annuler/<int:reservation_id>/', views.annuler_reservation, name='annuler_reservation'),
]