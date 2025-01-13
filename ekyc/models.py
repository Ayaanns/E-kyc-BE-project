from django.db import models

# Create your models here.
class KYCSession(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    id_card_image = models.ImageField(upload_to='id_cards/')
    liveness_score = models.FloatField()
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

