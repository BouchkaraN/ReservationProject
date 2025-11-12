from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime


class Salle(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la salle")
    capacite = models.IntegerField(verbose_name="Capacité")
    equipements = models.TextField(verbose_name="Équipements disponibles")
    etage = models.IntegerField(verbose_name="Étage")
    image_url = models.URLField(blank=True, verbose_name="URL de l'image")

    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"

    def __str__(self):
        return f"{self.nom} - Étage {self.etage} (Capacité: {self.capacite})"

    def est_disponible(self, date, heure_debut, heure_fin):
        """Vérifie si la salle est disponible pour un créneau donné"""
        reservations = self.reservation_set.filter(
            date=date,
            validee=True
        )

        for reservation in reservations:
            # Vérifier les chevauchements d'horaires
            if (heure_debut < reservation.heure_fin and
                    heure_fin > reservation.heure_debut):
                return False
        return True


class Reservation(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, verbose_name="Salle")
    nom_utilisateur = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    date = models.DateField(verbose_name="Date de réservation")
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(verbose_name="Heure de fin")
    motif = models.TextField(verbose_name="Motif de la réservation")
    nombre_participants = models.IntegerField(verbose_name="Nombre de participants")
    validee = models.BooleanField(default=True, verbose_name="Validée")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-date', '-heure_debut']

    def __str__(self):
        return f"{self.salle.nom} - {self.date} ({self.heure_debut}-{self.heure_fin})"

    def clean(self):
        """Validation personnalisée"""
        # Vérifier que l'heure de fin est après l'heure de début
        if self.heure_debut >= self.heure_fin:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")

        # Vérifier que le nombre de participants ne dépasse pas la capacité
        if self.nombre_participants > self.salle.capacite:
            raise ValidationError(
                f"Le nombre de participants ({self.nombre_participants}) "
                f"dépasse la capacité de la salle ({self.salle.capacite})."
            )

        # Vérifier la disponibilité de la salle
        if not self.salle.est_disponible(self.date, self.heure_debut, self.heure_fin):
            raise ValidationError("Cette salle est déjà réservée pour ce créneau horaire.")