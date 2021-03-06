from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from solo.models import SingletonModel
from embed_video.fields import EmbedVideoField
import os
from . import services, utils, managers
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from abc import ABC, abstractmethod


############################################################
# EVENTS


@receiver(models.signals.post_delete)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    try:
        for file in instance.file_list():
            if file:
                utils.delete_file_with_instance(file)
    except AttributeError:
        pass


@receiver(models.signals.pre_save)
def auto_delete_file_on_change(sender, instance, **kwargs):
    try:
        if not instance.pk:
            return False

        try:
            old_files = sender.objects.get(pk=instance.pk).file_list()
        except sender.DoesNotExist:
            return False

        new_files = instance.file_list()
        for index, new_file in enumerate(new_files):
            if not new_file == old_files[index]:
                utils.delete_file_with_instance(old_files[index])
    except AttributeError:
        pass


############################################################
# MODELS


class SEO(models.Model):
    seo_title = models.TextField(verbose_name='Title', max_length=255, null=True)
    seo_keywords = models.TextField(verbose_name='Keywords', max_length=255, null=True)
    seo_description = models.TextField(verbose_name='Description', max_length=255, null=True)
    seo_url = models.URLField(verbose_name='URL', null=True)

    def __str__(self):
        return self.seo_title


class CustomAbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator()

    email = models.CharField(
        _('email address'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[],
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = managers.CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class User(CustomAbstractUser):
    R = 1
    U = 2
    LANGUAGE = (
        ('R', 'Rus'),
        ('U', 'Ukr'),
    )
    M = 1
    F = 2
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    CITY = (
        ('OD', 'Одесса'),
        ('KY', 'Киев'),
        ('KHAR', 'Харьков'),
    )

    phone = models.CharField(verbose_name='Номер телефона', max_length=60)
    address = models.TextField(verbose_name='Адрес', max_length=255)
    card_number = models.CharField(verbose_name='Номер карты', max_length=255)
    language = models.CharField(verbose_name='Язык', max_length=1, choices=LANGUAGE, default=R)
    gender = models.CharField(verbose_name='Пол', max_length=1, choices=GENDER, default=M)
    city = models.CharField(verbose_name='', choices=CITY, max_length=4)  # пустой вербоус нейм, конфликт с crispy forms
    date_of_birth = models.DateField(verbose_name='Дата рождения', null=True)

    def __str__(self):
        return self.email


class Cinema(models.Model):
    cinema_name = models.CharField(max_length=255, verbose_name='Название кинотеатра')
    cinema_description = models.TextField(verbose_name='Описание конотеатра', blank=True)
    cinema_condition = models.TextField(verbose_name='Условия кинотеатра', blank=True)
    cinema_logo = models.ImageField(verbose_name='Логотип кинотеатра', upload_to='images/cinema/logo/')
    cinema_upper_banner = models.ImageField('Верхний баннер кинотеатра', upload_to='images/cinema/upper_banner/')
    cinema_image1 = models.ImageField('Первое изображение', upload_to='images/cinema/')
    cinema_image2 = models.ImageField('Второе изображение', upload_to='images/cinema/')
    cinema_image3 = models.ImageField('Третее изображение', upload_to='images/cinema/')
    cinema_image4 = models.ImageField('Четвёртое изображение', upload_to='images/cinema/')
    cinema_image5 = models.ImageField('Пятое изображение', upload_to='images/cinema/')
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(Cinema, self).save(*args, **kwargs)

    def get_logo_image(self):
        return os.path.join('/media', self.cinema_logo.name)

    def get_upper_banner(self):
        return os.path.join('/media', self.cinema_upper_banner.name)

    def get_image1(self):
        return os.path.join('/media', self.cinema_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.cinema_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.cinema_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.cinema_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.cinema_image5.name)

    def __str__(self):
        return self.cinema_name

    def file_list(self):
        return [self.cinema_logo, self.cinema_upper_banner, self.cinema_image1, self.cinema_image2, self.cinema_image3,
                self.cinema_image4, self.cinema_image5]


class CinemaHall(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE,
                               verbose_name='')  # пустой verbose_name, конфликт с crispy forms
    hall_name = models.CharField(max_length=255, verbose_name='')
    hall_description = models.TextField(verbose_name='Описание зала', blank=True)
    cinema_scheme = models.ImageField(verbose_name='Схема кинотеатра', upload_to='images/hall/logo/')
    hall_upper_banner = models.ImageField('Верхний баннер кинотеатра', upload_to='images/hall/upper_banner/')
    hall_image1 = models.ImageField('Первое изображение', upload_to='images/hall/')
    hall_image2 = models.ImageField('Второе изображение', upload_to='images/hall/')
    hall_image3 = models.ImageField('Третее изображение', upload_to='images/hall/')
    hall_image4 = models.ImageField('Четвёртое изображение', upload_to='images/hall/')
    hall_image5 = models.ImageField('Пятое изображение', upload_to='images/hall/')
    hall_scheme = models.ImageField(verbose_name='Схема зала', upload_to='images/hall/logo/')
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(CinemaHall, self).save(*args, **kwargs)

    def get_scheme(self):
        return os.path.join('/media', self.hall_scheme.name)

    def get_upper_banner(self):
        return os.path.join('/media', self.hall_upper_banner.name)

    def get_image1(self):
        return os.path.join('/media', self.hall_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.hall_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.hall_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.hall_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.hall_image5.name)

    def __str__(self):
        return self.hall_name

    def file_list(self):
        return [self.hall_upper_banner, self.hall_image1, self.hall_image2, self.hall_image3, self.hall_image4,
                self.hall_image5, self.hall_scheme]


class Film(models.Model):
    LANGUAGE = (
        ('Украинский', 'Украинский'),
        ('Английски', 'Английский'),
        ('Русский', 'Русский')
    )
    TYPE = (
        ('Аниме', 'Аниме'),
        ('Мультфильм', 'Мультфильм'),
        ('Фильм', 'Фильм')
    )

    title = models.CharField('Название фильма', max_length=255)
    original_title = models.CharField('Оригинальное название', max_length=255, null=True, blank=True)
    country = models.CharField('Название страны', max_length=255, null=True)
    description = models.TextField('Описание фильма', blank=True)
    director = models.CharField('Продюссер', max_length=255, null=True)
    main_image = models.ImageField(upload_to='images/film_poster')
    image1 = models.ImageField('Первое изображение', upload_to='images/film_images')
    image2 = models.ImageField('Второе изображение', upload_to='images/film_images/')
    image3 = models.ImageField('Третее изображение', upload_to='images/film_images/')
    image4 = models.ImageField('Четвёртое изображение', upload_to='images/film_images/')
    image5 = models.ImageField('Пятое изображение', upload_to='images/film_images/')
    trailer_link = EmbedVideoField('')
    two_d = models.BooleanField('2Д', null=False)
    three_d = models.BooleanField('3Д', null=False)
    i_max = models.BooleanField('I_MAX', null=False)
    duration = models.IntegerField('Длительность фильма (минуты)')
    first_night = models.DateField('Дата премьеры')
    language = models.CharField('', choices=LANGUAGE, max_length=55, null=True)
    type = models.CharField('', choices=TYPE, max_length=55, null=True)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(Film, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_image(self):
        return os.path.join('/media', self.main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.image1.name)

    def get_image2(self):
        return os.path.join('/media', self.image2.name)

    def get_image3(self):
        return os.path.join('/media', self.image3.name)

    def get_image4(self):
        return os.path.join('/media', self.image4.name)

    def get_image5(self):
        return os.path.join('/media', self.image5.name)

    def get_absolute_url(self):
        return f'film/list'

    def file_list(self):
        return [self.main_image, self.image1, self.image2, self.image3, self.image4, self.image5]

    def get_string_duration(self):
        d = self.duration
        r = ""
        h = d // 60
        m = d % 60

        if h > 0:
            r += f"{h} часов"
        if m > 0:
            r += f"{m} минут"
        return r if r else "Не указанно"


class FilmSession(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE, verbose_name='')
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, verbose_name='')
    date = models.DateField('Дата сеанса', null=True)
    time = models.TimeField('Время сеанса', null=True)
    price = models.IntegerField('Стоимость', null=True)
    vip_price = models.IntegerField('Стоимость вип билета', null=True)

    def __str__(self):
        return str(self.film.id)


class News(models.Model):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    news_name = models.CharField(max_length=255, verbose_name='Название новости')
    news_description = models.TextField(verbose_name='Описание новости', blank=True)
    news_main_image = models.ImageField(verbose_name='Логотип новости', upload_to='images/news/logo/')
    news_image1 = models.ImageField(verbose_name='Первое изображение', upload_to='images/news/')
    news_image2 = models.ImageField(verbose_name='Второе изображение', upload_to='images/news/')
    news_image3 = models.ImageField(verbose_name='Третее изображение', upload_to='images/news/')
    news_image4 = models.ImageField(verbose_name='Четвёртое изображение', upload_to='images/news/')
    news_image5 = models.ImageField(verbose_name='Пятое изображение', upload_to='images/news/')
    news_url = models.URLField(verbose_name='Ссылка на видео', null=True)
    news_published_date = models.DateField(verbose_name='Дата публикации новости')
    news_status = models.CharField(verbose_name='', max_length=3,
                                   choices=STATUS)  # пустой вербоус нейм, конфликт с crispy forms
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(News, self).save(*args, **kwargs)


    def __str__(self):
        return self.news_name

    def get_absolute_image(self):
        return os.path.join('/media', self.news_main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.news_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.news_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.news_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.news_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.news_image5.name)

    def get_absolute_url(self):
        return f'news/list'

    def file_list(self):
        return [self.news_main_image, self.news_image1, self.news_image2, self.news_image3, self.news_image4,
                self.news_image5]


class Promotion(models.Model):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    promo_name = models.CharField(max_length=255, verbose_name='Название акции')
    promo_description = models.TextField(verbose_name='Описание акции', blank=True)
    promo_main_image = models.ImageField(verbose_name='Логотип акции', upload_to='images/promotion/logo/')
    promo_image1 = models.ImageField(verbose_name='Первое изображение', upload_to='images/promotion/')
    promo_image2 = models.ImageField(verbose_name='Второе изображение', upload_to='images/promotion/')
    promo_image3 = models.ImageField(verbose_name='Третее изображение', upload_to='images/promotion/')
    promo_image4 = models.ImageField(verbose_name='Четвёртое изображение', upload_to='images/promotion/')
    promo_image5 = models.ImageField(verbose_name='Пятое изображение', upload_to='images/promotion/')
    promo_url = models.URLField(verbose_name='Ссылка на акцию', null=True)
    promo_published_date = models.DateField(verbose_name='Дата публикации акции')
    promo_status = models.CharField(verbose_name='', max_length=3,
                                    choices=STATUS)  # пустой вербоус нейм, конфликт с crispy forms
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def __str__(self):
        return self.promo_name

    def get_absolute_image(self):
        return os.path.join('/media', self.promo_main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.promo_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.promo_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.promo_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.promo_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.promo_image5.name)

    def file_list(self):
        return [self.promo_main_image, self.promo_image1, self.promo_image2, self.promo_image3, self.promo_image4,
                self.promo_image5]


class MainPage(SingletonModel):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    status = models.CharField(verbose_name='', max_length=3, choices=STATUS, null=True)
    tel_number1 = models.CharField(verbose_name='Номер телефона', null=True, max_length=155)
    tel_number2 = models.CharField(verbose_name='Номер телефона', null=True, max_length=155)
    created_date = models.DateField(default=timezone.now)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(MainPage, self).save(*args, **kwargs)


class AboutCinema(SingletonModel):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    status = models.CharField(verbose_name='', max_length=3, choices=STATUS)
    cinema_name = models.CharField(max_length=255, verbose_name='Название сети кинотеатров')
    cinema_description = models.TextField(verbose_name='Описание сети кинотеатров', blank=True)
    cinema_main_image = models.ImageField(verbose_name='Логотип сети кинотеатров', upload_to='images/about/logo/')
    cinema_image1 = models.ImageField(verbose_name='Первое изображение', upload_to='images/about/')
    cinema_image2 = models.ImageField(verbose_name='Второе изображение', upload_to='images/about/')
    cinema_image3 = models.ImageField(verbose_name='Третее изображение', upload_to='images/about/')
    cinema_image4 = models.ImageField(verbose_name='Четвёртое изображение', upload_to='images/about/')
    cinema_image5 = models.ImageField(verbose_name='Пятое изображение', upload_to='images/about/')
    created_date = models.DateField(default=timezone.now)
    status = models.CharField(verbose_name='', max_length=3, choices=STATUS, null=True)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(AboutCinema, self).save(*args, **kwargs)

    def get_absolute_image(self):
        return os.path.join('/media', self.cinema_main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.cinema_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.cinema_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.cinema_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.cinema_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.cinema_image5.name)

    def file_list(self):
        return [self.cinema_main_image, self.cinema_image1, self.cinema_image2, self.cinema_image3, self.cinema_image4,
                self.cinema_image5]

    def __str__(self):
        return self.cinema_name


class CafeBar(SingletonModel):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    cafebar_name = models.CharField(max_length=255, verbose_name='Название кафе-бара')
    cafebar_description = models.TextField(verbose_name='Описание кафе-бара', blank=True)
    cafebar_main_image = models.ImageField(verbose_name='Логотип кафе-бара', upload_to='images/cafe_bar/logo/')
    cafebar_image1 = models.ImageField(verbose_name='Первое изображение', upload_to='images/cafe_bar/')
    cafebar_image2 = models.ImageField(verbose_name='Второе изображение', upload_to='images/cafe_bar/')
    cafebar_image3 = models.ImageField(verbose_name='Третее изображение', upload_to='images/cafe_bar/')
    cafebar_image4 = models.ImageField(verbose_name='Четвёртое изображение', upload_to='images/cafe_bar/')
    cafebar_image5 = models.ImageField(verbose_name='Пятое изображение', upload_to='images/cafe_bar/')
    created_date = models.DateField(default=timezone.now)
    status = models.CharField(verbose_name='', max_length=3, choices=STATUS, null=True)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(CafeBar, self).save(*args, **kwargs)

    def get_absolute_image(self):
        return os.path.join('/media', self.cafebar_main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.cafebar_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.cafebar_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.cafebar_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.cafebar_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.cafebar_image5.name)

    def file_list(self):
        return [self.cafebar_main_image, self.cafebar_image1, self.cafebar_image2, self.cafebar_image3,
                self.cafebar_image4, self.cafebar_image5]

    def __str__(self):
        return self.cafebar_name


class VipHall(SingletonModel):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    status = models.CharField(verbose_name='', max_length=3, choices=STATUS)
    hall_name = models.CharField(max_length=255, verbose_name='Название VIP-зала')
    hall_description = models.TextField(verbose_name='Описание VIP-зала', blank=True)
    hall_main_image = models.ImageField(verbose_name='Логотип VIP-зала', upload_to='images/vip_hall/logo/')
    hall_image1 = models.ImageField(verbose_name='Первое изображение', upload_to='images/vip_hall/')
    hall_image2 = models.ImageField(verbose_name='Второе изображение', upload_to='images/vip_hall/')
    hall_image3 = models.ImageField(verbose_name='Третее изображение', upload_to='images/vip_hall/')
    hall_image4 = models.ImageField(verbose_name='Четвёртое изображение', upload_to='images/vip_hall/')
    hall_image5 = models.ImageField(verbose_name='Пятое изображение', upload_to='images/vip_hall/')
    created_date = models.DateField(default=timezone.now)
    status = models.CharField(verbose_name='', max_length=3, choices=STATUS, null=True)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(VipHall, self).save(*args, **kwargs)

    def get_absolute_image(self):
        return os.path.join('/media', self.hall_main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.hall_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.hall_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.hall_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.hall_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.hall_image5.name)

    def file_list(self):
        return [self.hall_main_image, self.hall_image1, self.hall_image2, self.hall_image3, self.hall_image4,
                self.hall_image5]

    def __str__(self):
        return self.hall_name


class Advertising(SingletonModel):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    status = models.CharField(verbose_name='', max_length=3, choices=STATUS)
    adv_name = models.CharField(max_length=255, verbose_name='Название рекламы')
    adv_description = models.TextField(verbose_name='Описание рекламы', blank=True)
    adv_main_image = models.ImageField(verbose_name='Логотип рекламы', upload_to='images/adv/logo/')
    adv_image1 = models.ImageField(verbose_name='Первое изображение', upload_to='images/adv/')
    adv_image2 = models.ImageField(verbose_name='Второе изображение', upload_to='images/adv/')
    adv_image3 = models.ImageField(verbose_name='Третее изображение', upload_to='images/adv/')
    adv_image4 = models.ImageField(verbose_name='Четвёртое изображение', upload_to='images/adv/')
    adv_image5 = models.ImageField(verbose_name='Пятое изображение', upload_to='images/adv/')
    created_date = models.DateField(default=timezone.now)
    status = models.CharField(verbose_name='', max_length=3, choices=STATUS, null=True)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(Advertising, self).save(*args, **kwargs)

    def get_absolute_image(self):
        return os.path.join('/media', self.adv_main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.adv_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.adv_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.adv_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.adv_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.adv_image5.name)

    def file_list(self):
        return [self.adv_main_image, self.adv_image1, self.adv_image2, self.adv_image3, self.adv_image4,
                self.adv_image5]

    def __str__(self):
        return self.adv_name


class ChildRoom(SingletonModel):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    status = models.CharField(verbose_name='', max_length=3, choices=STATUS)
    room_name = models.CharField(max_length=255, verbose_name='Название детской комнаты')
    room_description = models.TextField(verbose_name='Описание детской комнаты', blank=True)
    room_main_image = models.ImageField(verbose_name='Логотип детской комнаты', upload_to='images/child_room/logo/')
    room_image1 = models.ImageField(verbose_name='Первое изображение', upload_to='images/child_room/')
    room_image2 = models.ImageField(verbose_name='Второе изображение', upload_to='images/child_room/')
    room_image3 = models.ImageField(verbose_name='Третее изображение', upload_to='images/child_room/')
    room_image4 = models.ImageField(verbose_name='Четвёртое изображение', upload_to='images/child_room/')
    room_image5 = models.ImageField(verbose_name='Пятое изображение', upload_to='images/child_room/')
    created_date = models.DateField(default=timezone.now)
    status = models.CharField(verbose_name='', max_length=3, choices=STATUS, null=True)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(ChildRoom, self).save(*args, **kwargs)

    def file_list(self):
        return [self.room_main_image, self.room_image1, self.room_image1, self.room_image2, self.room_image3,
                self.room_image4, self.room_image5]

    def __str__(self):
        return self.room_name

    def get_absolute_image(self):
        return os.path.join('/media', self.room_main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.room_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.room_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.room_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.room_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.room_image5.name)


class Contact(models.Model):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    status = models.CharField(verbose_name='', max_length=3, choices=STATUS, null=True)
    contact_cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, verbose_name='',
                                       null=True)  # пустой verbose_name, конфликт с crispy forms
    contact_address = models.TextField(verbose_name='Адрес кинотеатра', blank=True)
    contact_location = models.CharField(verbose_name='Координаты для карты', max_length=255)
    contact_logo = models.ImageField(verbose_name='Лого', upload_to='images/contact/logo/')
    created_date = models.DateField(default=timezone.now)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(Contact, self).save(*args, **kwargs)

    def get_absolute_image(self):
        return os.path.join('/media', self.contact_logo.name)

    def file_list(self):
        return [self.contact_logo, ]

    def __str__(self):
        return self.contact_location


class MainSlide(models.Model):
    slide_text = models.TextField(verbose_name='Текст слайда')
    slide_image = models.ImageField(verbose_name='Изображение слайда', upload_to='images/main_slide/')
    slide_url = models.URLField(verbose_name='Ссылка слайда')
    slide_timer = models.TextField(verbose_name='Скорость вращения')

    def get_absolute_image(self):
        return os.path.join('/media', self.slide_image.name)

    def file_list(self):
        return [self.slide_image, ]

    def __str__(self):
        return self.slide_url


class NewsPromoSlide(models.Model):
    slide_text = models.TextField(verbose_name='Текст слайда')
    slide_image = models.ImageField(verbose_name='Изображение слайда', upload_to='images/news_promo/')
    slide_url = models.URLField(verbose_name='Ссылка слайда')
    slide_timer = models.IntegerField(verbose_name='Скорость вращения')

    def file_list(self):
        return [self.slide_image, ]

    def __str__(self):
        return self.slide_url

    def get_absolute_image(self):
        return os.path.join('/media', self.slide_image.name)


class BackgroundBanner(SingletonModel):
    banner_image = models.ImageField(verbose_name='Изображение фона', upload_to='images/background/')

    def file_list(self):
        return [self.banner_image, ]

    def __str__(self):
        return self.banner_image

    def get_absolute_image(self):
        return os.path.join('/media/', self.banner_image.name)


class MobileApp(SingletonModel):
    STATUS = (
        ('ON', 'Active'),
        ('OFF', 'Inactive'),
    )

    status = models.CharField(verbose_name='', max_length=3, choices=STATUS, null=True)
    app_name = models.CharField(max_length=255, verbose_name='Название мобильного приложения')
    app_description = models.TextField(verbose_name='Описание мобильного приложения', blank=True)
    app_main_image = models.ImageField(verbose_name='Логотип мобильного приложения',
                                       upload_to='images/mobile_app/logo/')
    app_image1 = models.ImageField(verbose_name='Первое изображение', upload_to='images/mobile_app/')
    app_image2 = models.ImageField(verbose_name='Второе изображение', upload_to='images/mobile_app/')
    app_image3 = models.ImageField(verbose_name='Третее изображение', upload_to='images/mobile_app/')
    app_image4 = models.ImageField(verbose_name='Четвёртое изображение', upload_to='images/mobile_app/')
    app_image5 = models.ImageField(verbose_name='Пятое изображение', upload_to='images/mobile_app/')
    app_google = models.URLField(verbose_name='Ссылка на Android-приложение', null=True)
    app_apple = models.URLField(verbose_name='Ссылка на IOS-приложение', null=True)
    created_date = models.DateField(default=timezone.now)
    seo = models.ForeignKey(SEO, on_delete=models.CASCADE, verbose_name='SEO блок', null=True)

    def save(self, *args, **kwargs):
        if not self.seo:
            self.seo = SEO.objects.create()
        super(MobileApp, self).save(*args, **kwargs)

    def get_absolute_image(self):
        return os.path.join('/media', self.app_main_image.name)

    def get_image1(self):
        return os.path.join('/media', self.app_image1.name)

    def get_image2(self):
        return os.path.join('/media', self.app_image2.name)

    def get_image3(self):
        return os.path.join('/media', self.app_image3.name)

    def get_image4(self):
        return os.path.join('/media', self.app_image4.name)

    def get_image5(self):
        return os.path.join('/media', self.app_image5.name)

    def file_list(self):
        return [self.app_main_image, self.app_image1, self.app_image1, self.app_image2, self.app_image3,
                self.app_image4, self.app_image5]

    def __str__(self):
        return self.app_name


class ContextualAdvertising(SingletonModel):
    link = models.URLField('Ссылка рекламы', null=True)
    horizontal_adv = models.ImageField('Горизонтальная реклама', upload_to='images/ContextualAdvertising/')
    vertical_adv = models.ImageField('Вертикальная реклама', upload_to='images/ContextualAdvertising/')

    def get_horizontal_img(self):
        return os.path.join('/media', self.horizontal_adv.name)

    def get_vertical_img(self):
        return os.path.join('/media', self.vertical_adv.name)

    def __str__(self):
        return self.link