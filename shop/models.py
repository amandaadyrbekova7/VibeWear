from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Футболки", "Футболки"),
        ("Худи", "Худи"),
        ("Джинсы", "Джинсы"),
        ("Куртки", "Куртки"),
        ("Обувь", "Обувь"),
        ("Рубашки", "Рубашки"),
        ("Штаны", "Штаны"),
        ("Свитшоты", "Свитшоты"),
    ]

    name = models.CharField(max_length=200, verbose_name="Название")
    price = models.PositiveIntegerField(verbose_name="Цена")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Категория")
    image = models.CharField(max_length=255, verbose_name="Путь к картинке")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name