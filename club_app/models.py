from collections import OrderedDict

from django.db import models
from django.utils import timezone

from django_jinja_knockout.tpl import format_local_date, flatten_dict, str_dict, reverse, Str


class Profile(models.Model):
    first_name = models.CharField(max_length=30, verbose_name='First name')
    last_name = models.CharField(max_length=30, verbose_name='Last name')
    birth_date = models.DateField(db_index=True, verbose_name='Birth date')

    class Meta:
        unique_together = ('first_name', 'last_name', 'birth_date')
        verbose_name = 'Sportsman profile'
        verbose_name_plural = 'Sportsmen profiles'
        ordering = ('first_name', 'last_name', 'birth_date')

    def get_str_fields(self):
        return OrderedDict([
            ('first_name', self.first_name),
            ('last_name', self.last_name),
            ('birth_date', format_local_date(self.birth_date))
        ])

    def __str__(self):
        return ' '.join([self.first_name, self.last_name])


class Manufacturer(models.Model):
    company_name = models.CharField(max_length=64, unique=True, verbose_name='Company name')
    direct_shipping = models.BooleanField(verbose_name='Direct shipping')

    class Meta:
        verbose_name = 'Sport equipment manufacturer'
        verbose_name_plural = 'Sport equipment manufacturers'
        ordering = ('company_name',)

    def get_str_fields(self):
        str_fields = OrderedDict([
            ('company_name', self.company_name),
        ])
        str_fields['direct_shipping'] = 'Yes (direct)' if self.direct_shipping else 'No (remote)'
        return str_fields

    def __str__(self):
        return ' › '.join(self.get_str_fields().values())


class Club(models.Model):
    CATEGORY_RECREATIONAL = 0
    CATEGORY_PROFESSIONAL = 1
    CATEGORIES = (
        (CATEGORY_RECREATIONAL, 'Recreational'),
        (CATEGORY_PROFESSIONAL, 'Professional'),
    )
    title = models.CharField(max_length=64, unique=True, verbose_name='Title')
    category = models.IntegerField(
        choices=CATEGORIES, default=CATEGORY_RECREATIONAL, db_index=True, verbose_name='Category'
    )
    foundation_date = models.DateField(db_index=True, verbose_name='Foundation date')
    last_update = models.DateTimeField(db_index=True, verbose_name='Last update')

    class Meta:
        verbose_name = 'Sport club'
        verbose_name_plural = 'Sport clubs'
        ordering = ('title',)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.foundation_date is None:
                self.foundation_date = timezone.now()
            self.last_update = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        url = Str(reverse('club_detail', kwargs={'club_id': self.pk}))
        url.text = str(self.title)
        return url

    def get_str_fields(self):
        return OrderedDict([
            ('title', self.title),
            ('category', self.get_category_display()),
            ('foundation_date', format_local_date(self.foundation_date)),
            ('last_update', format_local_date(self.last_update))
        ])

    def __str__(self):
        return ' › '.join(self.get_str_fields().values())


class Equipment(models.Model):
    CATEGORY_RACKET = 0
    CATEGORY_BALL = 1
    CATEGORY_SHUTTLECOCK = 2
    CATEGORY_OTHER = 3
    CATEGORIES = (
        (CATEGORY_RACKET, 'Racket'),
        (CATEGORY_BALL, 'Ball'),
        (CATEGORY_SHUTTLECOCK, 'Shuttlecock'),
        (CATEGORY_OTHER, 'Other type'),
    )
    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name='Club')
    manufacturer = models.ForeignKey(
        Manufacturer, null=True, blank=True, on_delete=models.CASCADE, verbose_name='Manufacturer'
    )
    inventory_name = models.CharField(max_length=64, verbose_name='Inventory name')
    category = models.IntegerField(
        choices=CATEGORIES, default=CATEGORY_RACKET, db_index=True, verbose_name='Category'
    )

    class Meta:
        verbose_name = 'Sport club equipment'
        verbose_name_plural = 'Sport club equipments'

    def get_absolute_url(self):
        url = Str(reverse('equipment_detail', kwargs={'equipment_id': self.pk}))
        url.text = str(self.inventory_name)
        return url

    def get_str_fields(self):
        str_fields = OrderedDict([
            ('club', self.club.get_str_fields()),
        ])
        if self.manufacturer is not None:
            str_fields['manufacturer'] = self.manufacturer.get_str_fields()
        str_fields['inventory_name'] = self.inventory_name
        str_fields['category'] = self.get_category_display()
        return str_fields

    def __str__(self):
        str_fields = self.get_str_fields()
        return str_dict(str_fields)


class Member(models.Model):
    SPORT_BADMINTON = 0
    SPORT_TENNIS = 1
    SPORT_TABLE_TENNIS = 2
    SPORT_SQUASH = 3
    SPORT_ANOTHER = 4
    BASIC_SPORTS = (
        (SPORT_BADMINTON, 'Badminton'),
        (SPORT_TENNIS, 'Tennis'),
        (SPORT_TABLE_TENNIS, 'Table tennis'),
    )
    SPORTS = BASIC_SPORTS + (
        (SPORT_SQUASH, 'Squash'),
        (SPORT_ANOTHER, 'Another sport'),
    )
    ROLE_OWNER = 0
    ROLE_FOUNDER = 1
    ROLE_MEMBER = 2
    ROLES = (
        (ROLE_OWNER, 'Owner'),
        (ROLE_FOUNDER, 'Founder'),
        (ROLE_MEMBER, 'Member'),
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Sportsman')
    club = models.ForeignKey(Club, blank=True, on_delete=models.CASCADE, verbose_name='Club')
    last_visit = models.DateTimeField(db_index=True, verbose_name='Last visit time')
    plays = models.IntegerField(choices=SPORTS, default=SPORT_ANOTHER, verbose_name='Plays sport')
    role = models.IntegerField(choices=ROLES, default=ROLE_MEMBER, verbose_name='Member role')
    note = models.TextField(max_length=16384, blank=True, default='', verbose_name='Note')
    is_endorsed = models.BooleanField(default=False, verbose_name='Endorsed')

    class Meta:
        unique_together = ('profile', 'club')
        verbose_name = 'Sport club member'
        verbose_name_plural = 'Sport club members'

    def get_absolute_url(self):
        url = Str(reverse('member_detail', kwargs={'member_id': self.pk}))
        str_fields = flatten_dict(self.get_str_fields(), enclosure_fmt=None)
        url.text = ' / '.join([str_fields['profile'], str_fields['club']])
        return url

    def get_str_fields(self):
        parts = OrderedDict([
            ('profile', self.profile.get_str_fields()),
            ('club', self.club.get_str_fields()),
            ('last_visit', format_local_date(self.last_visit)),
            ('plays', self.get_plays_display()),
            ('role', self.get_role_display()),
            ('is_endorsed', 'endorsed' if self.is_endorsed else 'unofficial')
        ])
        return parts

    def __str__(self):
        str_fields = self.get_str_fields()
        return str_dict(str_fields)
