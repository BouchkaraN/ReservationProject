from django import forms
from .models import Reservation
from datetime import date


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['nom_utilisateur', 'email', 'date', 'heure_debut', 'heure_fin', 'nombre_participants', 'motif']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().isoformat()
            }),
            'heure_debut': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'heure_fin': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'nom_utilisateur': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre.email@example.com'
            }),
            'nombre_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'motif': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez le motif de votre réservation...'
            }),
        }
    def __init__(self, *args, **kwargs):
        self.salle = kwargs.pop('salle', None)
        super().__init__(*args, **kwargs)
    def clean(self):
        cleaned_data = super().clean()
        if self.salle:
            cleaned_data['salle'] = self.salle
        return cleaned_data