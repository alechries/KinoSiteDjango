from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .. import models, forms as g_forms, utils
import datetime


def index_view(request):
    now = datetime.date.today()
    full_date_now = datetime.date.today()
    background_banner = models.BackgroundBanner.get_solo()
    films_today = models.Film.objects.filter(first_night__lte=now)
    print(films_today)
    future_film = models.Film.objects.filter(first_night__gt=now)
    print(future_film)
    return render(request, 'public/index.html', {'background_banner': background_banner,
                                                 'films_today': films_today,
                                                 'future_film': future_film,
                                                 'date_now': full_date_now,
                                                 })


def account_cabinet_view(request):
    user = request.user
    if user.is_authenticated:
        return utils.form_template(
            request=request,
            instance=user,
            form_class=g_forms.UserForm,
            redirect_url_name='account_cabinet',
            template_file_name='public/account/cabinet.html',
            context={'user_pk': user.id}
        )
    else:
        return redirect('account_login')


def account_login_view(request):
    if request.method == 'POST':
        form = g_forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request,
                                username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('public_views.index')
                else:
                    _message = 'User is not active'
            else:
                _message = 'User does not exist'
        else:
            _message = 'Data is incorrect'
    else:
        _message = 'Please, Sign in'
    return render(request, 'public/account/login.html', {'form': g_forms.LoginForm(), 'message': _message})


def account_logout_view(request):
    logout(request)
    return redirect('index')


def account_registration_view(request):
    form = g_forms.RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        login(request, user)  # , backend='django.contrib.auth.backends.ModelBackend'
        form.save()
        return redirect('public_views.index')
    return render(request, 'public/account/registration.html', context={'form': g_forms.RegisterForm()})


def posters_films_list_view(request):
    films = models.Film.objects.all().order_by('first_night')
    background_banner = models.BackgroundBanner.get_solo()
    return render(request, 'public/posters/films_list.html', {'films': films,
                                                              'background_banner': background_banner,
                                                              })


def posters_films_details_view(request, pk):
    film = get_object_or_404(models.Film, pk=pk)
    sessions = models.FilmSession.objects.filter(film=film)

    print(sessions)
    background_banner = models.BackgroundBanner.get_solo()
    return render(request, 'public/posters/film_details.html', {'film': film,
                                                                'background_banner': background_banner,
                                                                'sessions': sessions
                                                                })


def timetable_films_sessions_list_view(request):
    return render(request, 'public/timetable/films-sessions-cinema_list.html')


def timetable_reservation_view(request, pk):
    return render(request, 'public/timetable/reservation.html')


def cinema_list_view(request):
    cinemas = models.Cinema.objects.all()
    background_banner = models.BackgroundBanner.get_solo()
    return render(request, 'public/cinema/cinema_list.html',{'cinemas': cinemas,
                                                             'background_banner': background_banner,
                                                             })


def cinema_details_view(request, pk):
    return render(request, 'public/cinema/details.html')


def cinema_hall_details_view(request, pk):
    return render(request, 'public/cinema/hall_details.html')


def promotion_list_view(request):
    promo_banners = models.NewsPromoSlide.objects.all()
    promotions = models.Promotion.objects.filter(promo_status='ON')
    background_banner = models.BackgroundBanner.get_solo()
    return render(request, 'public/promotion/promotions_list.html', {'promotions': promotions,
                                                                     'promo_banners': promo_banners,
                                                                     'background_banner': background_banner})


def promotion_details_view(request, pk):
    return render(request, 'public/promotion/details.html')


def about_cinema_view(request):
    return render(request, 'public/about/cinema.html')


def about_news_view(request):
    return render(request, 'public/about/news.html')


def about_cafe_bar_view(request):
    background_banner = models.BackgroundBanner.get_solo()
    cafe = models.CafeBar.get_solo()
    return render(request, 'public/about/cafe-bar.html', {'cafe': cafe,
                                                          'background_banner': background_banner,
                                                          })


def about_vip_hall_view(request):
    background_banner = models.BackgroundBanner.get_solo()
    vip_hall = models.VipHall.get_solo()
    return render(request, 'public/about/vip-hall.html', {'vip_hall': vip_hall,
                                                          'background_banner': background_banner,
                                                          })


def about_advertising_view(request):
    background_banner = models.BackgroundBanner.get_solo()
    adv = models.Advertising.get_solo()
    return render(request, 'public/about/advertising.html', {'background_banner': background_banner,
                                                             'adv': adv,
                                                             })


def about_mobile_app_view(request):
    app = models.MobileApp.get_solo()
    background_banner = models.BackgroundBanner.get_solo()
    return render(request, 'public/about/mobile-app.html', {'background_banner': background_banner,
                                                            'app': app})


def about_child_room_view(request):
    background_banner = models.BackgroundBanner.get_solo()
    child_room = models.ChildRoom.get_solo()
    return render(request, 'public/about/vip-hall.html', {'child_room': child_room,
                                                          'background_banner': background_banner,
                                                          })

    return render(request, 'public/about/child-room.html')


def about_contacts_view(request):
    background_banner = models.BackgroundBanner.get_solo()
    contacts = models.Contact.objects.all()
    return render(request, 'public/about/contacts.html', {'background_banner': background_banner,
                                                          'contacts': contacts,
                                                          })