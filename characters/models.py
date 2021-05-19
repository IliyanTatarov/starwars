from django.db import models
from django.urls import reverse


class Collection(models.Model):
    csv_file = models.FileField(upload_to='csv/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.csv_file.name}'

    def get_absolute_url(self):
        return reverse('characters:collection', kwargs={
            'id': self.pk,
        })
