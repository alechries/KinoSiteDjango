from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from . import forms
from .. import forms as g_forms
from django.core.mail import send_mail
from .. import services, models, utils, auth
from os import remove as remove_file
from datetime import date
from django.db.models import Q


def admin_index_view(request):
    date_now = date.today()
    context = {
        'films_will_count': services.Count.film_count_gt_date(date_now),
        'films_was_count': services.Count.film_count_lte_date(date_now),
        'cinema_count': services.Count.cinema_count(),
        'cinema_hall_count': services.Count.cinema_hall_count(),
        'news_will_count': services.Count.news_count_gt_date(date_now),
        'news_was_count': services.Count.news_count_lte_date(date_now),
        'promo_count': services.Count.promotion_count(),
        'user_count': services.Count.user_count(),
    }
    return render(request, 'adminLte/index.html', context)


def account_login_view(request):
    if request.method == 'POST':
        form = g_forms.LoginForm(request.POST)
        if form.is_valid():
            user = auth.EmailAuthBackend.authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('admin_index')
                else:
                    _message = 'User is not active'
            else:
                _message = 'User does not exist'
        else:
            _message = 'Data is incorrect'
    else:
        _message = 'Please, Sign in'
    return render(request, 'adminLte/account/login.html', {'form': g_forms.LoginForm(), 'message': _message})


def account_logout_view(request):
    logout(request)
    return redirect('admin_index')


def banner_view(request):
    main_slide = models.MainSlide.objects.all()
    news_promo = models.NewsPromoSlide.objects.all()
    background_banner = models.BackgroundBanner.get_solo()
    return render(request, 'adminLte/banner/banner_list.html', {'main_slide': main_slide, 'news_promo': news_promo, 'background_banner': background_banner})


def session_form_view(request, pk=None):
    session = get_object_or_404(models.FilmSession, pk=pk) if pk else None
    return utils.form_template(
        request=request,
        instance=session,
        form_class=forms.SessionForm,
        redirect_url_name='admin_film_list',
        template_file_name='adminLte/film/session_form.html',
    )


def session_delete_view(request, pk):
    services.Delete.model_object(models.FilmSession, pk)
    return redirect('admin_film_list')


def film_edit_form_view(request, pk=None):
    film = get_object_or_404(models.Film, pk=pk) if pk else None

    session = models.FilmSession.objects.filter(film=film)
    media_context = {}
    instance_seo_id = None
    if film:
        if film.seo:
            instance_seo_id = film.seo.id
        media_context = {'main_image': models.Film.get_absolute_image(film),
                         'image1': models.Film.get_image1(film),
                         'image2': models.Film.get_image2(film),
                         'image3': models.Film.get_image3(film),
                         'image4': models.Film.get_image4(film),
                         'image5': models.Film.get_image5(film), }
    return utils.form_template(
            request=request,
            instance=film,
            form_class=forms.FilmForm,
            redirect_url_name='admin_film_list',
            template_file_name='adminLte/film/film_form.html',
            context={'session': session, 'instance_seo_id': instance_seo_id},
            media_context=media_context
        )


def film_list_view(request):
    films = services.Get.model_list(models.Film)
    return utils.content_page(request=request,
                                 posts_key='film',
                                 posts=films,
                                 limit=8,
                                 template='adminLte/film/film_list.html',
                                 )


def film_delete_view(request, pk):
    services.Delete.model_object(models.Film, pk)
    return redirect('admin_film_list')


def cinema_list_view(request):
    cinemas = services.Get.model_list(models.Cinema)
    return render(request, 'adminLte/cinema/cinema_list.html', {'cinemas': cinemas})


def cinema_form_view(request, pk=None):
    cinema = get_object_or_404(models.Cinema, pk=pk) if pk else None
    media_context = {}
    halls = models.CinemaHall.objects.filter(cinema=cinema)
    instance_seo_id = None
    if cinema:
        if cinema.seo:
            instance_seo_id = cinema.seo.id
        media_context = {'logo': models.Cinema.get_logo_image(cinema),
                         'upper_banner': models.Cinema.get_upper_banner(cinema),
                         'image1': models.Cinema.get_image1(cinema),
                         'image2': models.Cinema.get_image2(cinema),
                         'image3': models.Cinema.get_image3(cinema),
                         'image4': models.Cinema.get_image4(cinema),
                         'image5': models.Cinema.get_image5(cinema),
                         }
    return utils.form_template(
        request=request,
        instance=cinema,
        context={'halls': halls, 'instance_seo_id': instance_seo_id},
        form_class=forms.CinemaForm,
        redirect_url_name='admin_cinema_list',
        template_file_name='adminLte/cinema/cinema_form.html',
        media_context=media_context,
    )


def cinema_delete_view(request, pk):
    services.Delete.model_object(models.Cinema, pk)
    return redirect('admin_cinema_list')


def hall_form_view(request, pk=None):
    cinema_hall = get_object_or_404(models.CinemaHall, pk=pk) if pk else None
    media_context = {}
    instance_seo_id = None
    if cinema_hall:
        if cinema_hall.seo:
            instance_seo_id = cinema_hall.seo.id
        media_context = {'scheme': models.CinemaHall.get_scheme(cinema_hall),
                         'upper_banner': models.CinemaHall.get_upper_banner(cinema_hall),
                         'image1': models.CinemaHall.get_image1(cinema_hall),
                         'image2': models.CinemaHall.get_image2(cinema_hall),
                         'image3': models.CinemaHall.get_image3(cinema_hall),
                         'image4': models.CinemaHall.get_image4(cinema_hall),
                         'image5': models.CinemaHall.get_image5(cinema_hall),
                         }
    return utils.form_template(
        request=request,
        instance=cinema_hall,
        form_class=forms.CinemaHallForm,
        redirect_url_name='admin_cinema_list',
        template_file_name='adminLte/cinema/hall_form.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id}
    )


def hall_delete_view(request, pk):
    services.Delete.model_object(models.CinemaHall, pk)
    return redirect('admin_cinema_list')


def news_form_view(request, pk=None):
    news = get_object_or_404(models.News, pk=pk) if pk else None
    media_context = {}
    instance_seo_id = None
    if news:
        if news.seo:
            instance_seo_id = news.seo.id
        media_context = {'main_image': models.News.get_absolute_image(news),
                         'image1': models.News.get_image1(news),
                         'image2': models.News.get_image2(news),
                         'image3': models.News.get_image3(news),
                         'image4': models.News.get_image4(news),
                         'image5': models.News.get_image5(news),
                         }
    return utils.form_template(
        request=request,
        instance=news,
        form_class=forms.NewsForm,
        redirect_url_name='admin_news_list',
        template_file_name='adminLte/news/news_form.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id}
    )


def news_list_view(request):
    news = services.Get.model_list(models.News)
    return render(request, 'adminLte/news/news_list.html', {'news': news})


def news_delete_view(request, pk):
    services.Delete.model_object(models.News, pk)
    return redirect('admin_news_list')


def promotion_list_view(request):
    promotions = services.Get.model_list(models.Promotion)
    return render(request, 'adminLte/promotion/promotion_list.html', {'promotions': promotions})


def promotion_form_view(request, pk=None):
    promotion = get_object_or_404(models.Promotion, pk=pk) if pk else None
    media_context = {}
    instance_seo_id = None
    if promotion:
        if promotion.seo:
            instance_seo_id = promotion.seo.id
        media_context = {'main_image': models.Promotion.get_absolute_image(promotion),
                         'image1': models.Promotion.get_image1(promotion),
                         'image2': models.Promotion.get_image2(promotion),
                         'image3': models.Promotion.get_image3(promotion),
                         'image4': models.Promotion.get_image4(promotion),
                         'image5': models.Promotion.get_image5(promotion),
                         }
    return utils.form_template(
        request=request,
        instance=promotion,
        form_class=forms.PromotionForm,
        redirect_url_name='admin_promotion_list',
        template_file_name='adminLte/promotion/promotion_form.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id}
    )


def promotion_delete_view(request, pk):
    services.Delete.model_object(models.Promotion, pk)
    return redirect('admin_promotion_list')


def pages_list_view(request):
    context = {
        'main_page': models.MainPage.get_solo(),
        'about_cinema': models.AboutCinema.get_solo(),
        'cafe_bar': models.CafeBar.get_solo(),
        'vip_hall': models.VipHall.get_solo(),
        'advertising': models.Advertising.get_solo(),
        'child_room': models.ChildRoom.get_solo(),
    }
    return render(request, 'adminLte/pages/pages_list.html', context)


def main_pages_view(request):
    solo: models.MainPage = models.MainPage.get_solo()
    instance_seo_id = None
    if solo:
        if solo.seo:
            instance_seo_id = solo.seo.id


    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.MainPageForm,
        redirect_url_name='admin_pages_list',
        template_file_name='adminLte/pages/main_page.html',
        context={'instance_seo_id': instance_seo_id}
    )


def about_cinema_view(request):
    solo: models.AboutCinema = models.AboutCinema.get_solo()
    instance_seo_id = None
    media_context = {}
    if solo:
        if solo.seo:
            instance_seo_id = solo.seo.id
        media_context = {'main_image': models.AboutCinema.get_absolute_image(solo),
                         'image1': models.AboutCinema.get_image1(solo),
                         'image2': models.AboutCinema.get_image2(solo),
                         'image3': models.AboutCinema.get_image3(solo),
                         'image4': models.AboutCinema.get_image4(solo),
                         'image5': models.AboutCinema.get_image5(solo),
                         }

    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.AboutCinemaForm,
        redirect_url_name='admin_pages_list',
        template_file_name='adminLte/pages/about_cinema.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id,
                 }
    )


def cafe_bar_view(request):
    solo: models.CafeBar = models.CafeBar.get_solo()
    instance_seo_id = None
    media_context = {}
    if solo:
        if solo.seo:
            instance_seo_id = solo.seo.id
        media_context = {'main_image': models.CafeBar.get_absolute_image(solo),
                         'image1': models.CafeBar.get_image1(solo),
                         'image2': models.CafeBar.get_image2(solo),
                         'image3': models.CafeBar.get_image3(solo),
                         'image4': models.CafeBar.get_image4(solo),
                         'image5': models.CafeBar.get_image5(solo),
                         }

    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.CafeBarForm,
        redirect_url_name='admin_pages_list',
        template_file_name='adminLte/pages/cafe_bar.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id}
    )


def vip_hall_view(request):
    solo: models.VipHall = models.VipHall.get_solo()
    instance_seo_id = None
    media_context = {}
    if solo:
        if solo.seo:
            instance_seo_id = solo.seo.id
        media_context = {'main_image': models.VipHall.get_absolute_image(solo),
                         'image1': models.VipHall.get_image1(solo),
                         'image2': models.VipHall.get_image2(solo),
                         'image3': models.VipHall.get_image3(solo),
                         'image4': models.VipHall.get_image4(solo),
                         'image5': models.VipHall.get_image5(solo),
                         }

    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.VipHallForm,
        redirect_url_name='admin_pages_list',
        template_file_name='adminLte/pages/vip_room.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id}
    )


def ads_view(request):
    solo: models.Advertising = models.Advertising.get_solo()
    instance_seo_id = None
    media_context = {}
    if solo:
        if solo.seo:
            instance_seo_id = solo.seo.id
        media_context = {'main_image': models.Advertising.get_absolute_image(solo),
                         'image1': models.Advertising.get_image1(solo),
                         'image2': models.Advertising.get_image2(solo),
                         'image3': models.Advertising.get_image3(solo),
                         'image4': models.Advertising.get_image4(solo),
                         'image5': models.Advertising.get_image5(solo),
                         }

    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.AdvertisingForm,
        redirect_url_name='admin_pages_list',
        media_context=media_context,
        template_file_name='adminLte/pages/ads.html',
        context={'instance_seo_id': instance_seo_id}
    )


def child_room_view(request):
    solo: models.ChildRoom = models.ChildRoom.get_solo()
    instance_seo_id = None
    media_context = {}
    if solo:
        if solo.seo:
            instance_seo_id = solo.seo.id
        media_context = {'main_image': models.ChildRoom.get_absolute_image(solo),
                         'image1': models.ChildRoom.get_image1(solo),
                         'image2': models.ChildRoom.get_image2(solo),
                         'image3': models.ChildRoom.get_image3(solo),
                         'image4': models.ChildRoom.get_image4(solo),
                         'image5': models.ChildRoom.get_image5(solo),
                         }

    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.ChildRoomForm,
        redirect_url_name='admin_pages_list',
        template_file_name='adminLte/pages/child_room.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id}
    )


def mobile_app_view(request):
    solo: models.MobileApp = models.MobileApp.get_solo()
    instance_seo_id = None
    media_context = {}
    if solo:
        if solo.seo:
            instance_seo_id = solo.seo.id
        media_context = {'main_image': models.MobileApp.get_absolute_image(solo),
                         'image1': models.MobileApp.get_image1(solo),
                         'image2': models.MobileApp.get_image2(solo),
                         'image3': models.MobileApp.get_image3(solo),
                         'image4': models.MobileApp.get_image4(solo),
                         'image5': models.MobileApp.get_image5(solo),
                         }

    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.MobileAppForm,
        redirect_url_name='admin_pages_list',
        template_file_name='adminLte/pages/mobile_app.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id}
    )


def contact_list_view(request):
    contacts = services.Get.model_list(models.Contact)
    return render(request, 'adminLte/pages/contact_list.html', {'contacts': contacts})


def contact_form_view(request, pk=None):
    contact = get_object_or_404(models.Contact, pk=pk) if pk else None
    instance_seo_id = None
    media_context = {}
    if contact:
        if contact.seo:
            instance_seo_id = contact.seo.id
        media_context = {'main_image': models.Contact.get_absolute_image(contact)}

    return utils.form_template(
        request=request,
        instance=contact,
        form_class=forms.ContactForm,
        redirect_url_name='admin_index',
        template_file_name='adminLte/pages/contact_form.html',
        media_context=media_context,
        context={'instance_seo_id': instance_seo_id}
    )


def contact_delete_view(request, pk):
    services.Delete.model_object(models.Contact, pk)
    return redirect('admin_contact_list')


def users_list_view(request):
    users = services.Get.model_list(models.User)
    return utils.content_page(request=request,
                                 posts_key='users',
                                 posts=users,
                                 limit=6,
                                 template='adminLte/users/users_list.html',
                                 )


def user_search_view(request):
    search_query = request.GET.get('search','')
    if search_query:
        user = models.User.objects.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query))
    else:
        user = models.User.objects.all()

    return render(request, 'adminLte/users/users_list.html', {'users': user})


def user_form_view(request, pk=None):
    user = get_object_or_404(models.User, pk=pk) if pk else None
    return utils.form_template(
            request=request,
            instance=user,
            form_class=g_forms.UserForm,
            redirect_url_name='admin_users_list',
            template_file_name='adminLte/users/user_form.html',
            context={'user_pk': pk}
        )


def user_change_password_view(request, pk):
    form = g_forms.UserPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = services.Get.model_object(models.User, pk)
        password = form.cleaned_data['password']
        services.Change.user_password(user, password)
        return redirect('admin_user_edit', pk=user.pk)
    return render(request, 'adminLte/users/user_change_password.html', context={'form': form})


def user_delete_view(request, pk):
    services.Delete.model_object(models.User, pk)
    return redirect('admin_users_list')


def user_choose_view(request):
    return render(request, 'adminLte/mailing/user_choose.html')


def mailing_view(request):
    if request.method == "POST":
        user = models.User.objects.values('email')
        for el in user:
            user_email = el['email']
            send_mail('Subject here', 'Here is the message.', 'dimadjangosendemail@gmail.com',
            [user_email])

    return render(request, 'adminLte/mailing/mailing.html')


def main_slide_form_view(request, pk=None):
    main_slide = get_object_or_404(models.MainSlide, pk=pk) if pk else None
    media_context = {}
    if main_slide:
        media_context = {'slide_image': models.MainSlide.get_absolute_image(main_slide)}
    return utils.form_template(
        request=request,
        instance=main_slide,
        form_class=forms.MainSlideForm,
        redirect_url_name='admin_banner_list',
        template_file_name='adminLte/banner/main_slide_form.html',
        media_context=media_context

    )


def main_slide_delete_view(request, pk):
    services.Delete.model_object(models.MainSlide, pk)
    return redirect('admin_banner_list')


def news_promo_slide_form_view(request, pk=None):
    promo_slide = get_object_or_404(models.NewsPromoSlide, pk=pk) if pk else None
    media_context = {}
    if promo_slide:
        media_context = {'slide_image': models.NewsPromoSlide.get_absolute_image(promo_slide)}
    return utils.form_template(
        request=request,
        instance=promo_slide,
        form_class=forms.NewsPromoSlideForm,
        redirect_url_name='admin_banner_list',
        template_file_name='adminLte/banner/news_promo_slide_form.html',
        media_context=media_context
    )


def news_promo_slide_delete_view(request, pk):
    services.Delete.model_object(models.NewsPromoSlide, pk)
    return redirect('admin_banner_list')


def background_banner_form_view(request):
    solo: models.BackgroundBanner = models.BackgroundBanner.get_solo()
    media_context = {'main_slide': models.BackgroundBanner.get_absolute_image(solo)}
    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.BackgroundBannerForm,
        redirect_url_name='admin_banner_list',
        template_file_name='adminLte/banner/background_banner_form.html',
        media_context=media_context
    )


def seo_form_view_decorator(redirect_to):
    def seo_form_view(request, pk):
        seo = get_object_or_404(models.SEO, pk=pk) if pk else None
        return utils.form_template(
            request=request,
            instance=(seo if seo else models.SEO),
            form_class=forms.SEOForm,
            redirect_url_name=redirect_to,
            template_file_name='adminLte/seo_form.html',
        )
    return seo_form_view

def contextual_advertising_form_view(request):
    solo: models.ContextualAdvertising = models.ContextualAdvertising.get_solo()
    media_context = {'horizontal_adv': models.ContextualAdvertising.get_horizontal_img(solo)}
    return utils.form_template(
        request=request,
        instance=solo,
        form_class=forms.ContextualAdvertisingForm,
        redirect_url_name='admin_banner_list',
        template_file_name='adminLte/banner/contextual_adv_view.html',
        media_context=media_context
    )