from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils import timezone


class Achievement(models.Model):
    name = models.CharField('название', max_length=64, unique=True)
    description = models.TextField('описание', blank=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'достижение'
        verbose_name_plural = 'достижения'

    def __str__(self):
        return self.name


class Cat(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='cats',
    )
    name = models.CharField(max_length=16, validators=[MinLengthValidator(2)])
    color = models.CharField(max_length=16, validators=[MinLengthValidator(3)])
    birth_year = models.IntegerField(blank=True, null=True)
    achievements = models.ManyToManyField(Achievement, blank=True, related_name='cats', verbose_name='достижения')

    def clean(self):
        super().clean()
        if self.birth_year is not None and not 1900 <= self.birth_year <= timezone.localdate().year:
            raise ValidationError({'birth_year': 'Год рождения должен быть от 1900 до текущего года.'})

    class Meta:
        verbose_name = 'кот'
        verbose_name_plural = 'коты'

    def __str__(self):
        return self.name
