from django.urls import path
from .dashboard_views import performance_dashboard
from .forms import PerformanceReviewForm
from django.shortcuts import render, redirect
from . import views

def schedule_review(request):
    from .models import PerformanceReview
    from .forms import PerformanceReviewForm
    from django.shortcuts import render, redirect
    import datetime
    initial = {'review_date': datetime.date.today()}
    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST, initial=initial)
        if form.is_valid():
            form.save()
            return redirect('performance_dashboard')
    else:
        form = PerformanceReviewForm(initial=initial)
    return render(request, 'performance_management/schedule_review_form.html', {'form': form, 'title': 'Schedule a Review'})

def new_review(request):
    from .models import PerformanceReview
    from .forms import PerformanceReviewForm
    from django.shortcuts import render, redirect
    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('performance_dashboard')
    else:
        form = PerformanceReviewForm()
    return render(request, 'performance_management/schedule_review_form.html', {'form': form, 'title': 'Submit Review'})

urlpatterns = [
    path('dashboard/', performance_dashboard, name='performance_dashboard'),
    path('schedule_review/', schedule_review, name='schedule_review'),
    path('new_review/', new_review, name='new_review'),


    


    path('reviews/', views.review_list, name='review_list'),
    path('reviews/add/', views.review_add, name='review_add'),
    path('reviews/<int:pk>/edit/', views.review_edit, name='review_edit'),
    path('reviews/<int:pk>/view/', views.review_view, name='review_view'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),



]
