from django.db import models
from django.utils.text import slugify


class Region(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)
