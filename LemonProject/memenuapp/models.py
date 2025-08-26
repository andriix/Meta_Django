from django.db import models

# Create your models here.
class MenuItem(models.Model)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to="menu_images/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return self.name