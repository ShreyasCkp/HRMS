from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PerformanceReview, PerformanceScore
from employee_management.models import Employee, Department
from django.db.models import Avg, Count, F


def performance_dashboard(request):
    # All reviews with prefetch for scores
    reviews = PerformanceReview.objects.prefetch_related('scores', 'scores__kpi').all()

    # Average performance = avg(score / kpi.max_score * 100)
    total_percentage = 0
    count_scores = 0
    for s in PerformanceScore.objects.select_related('kpi'):
        if s.kpi.max_score:
            total_percentage += (s.score / s.kpi.max_score) * 100
            count_scores += 1
    avg_performance = round(total_percentage / count_scores, 2) if count_scores else 0

    # Top performers = reviews with rating "Excellent"
    top_performance = sum(1 for review in reviews if review.rating() == "Excellent")

    # Goals achieved = % of scores >= kpi.goal_threshold
    total_scores = PerformanceScore.objects.count()
    goals_achieved_count = PerformanceScore.objects.filter(score__gte=F('kpi__goal_threshold')).count()
    goals_achieved = round((goals_achieved_count / total_scores) * 100, 2) if total_scores else 0

    # Reviews due = reviews with no scores assigned
    reviews_due = PerformanceReview.objects.annotate(score_count=Count('scores')).filter(score_count=0).count()

    # Department-wise performance
    department_performance = []
    for dept in Department.objects.all():
        dept_scores = PerformanceScore.objects.filter(review__employee__department=dept).select_related('kpi')
        total_pct = sum((s.score / s.kpi.max_score) * 100 for s in dept_scores)
        count = dept_scores.count()
        avg = round(total_pct / count, 2) if count else 0
        department_performance.append({'name': dept.name, 'performance': avg})

    return render(request, 'performance_dashboard.html', {
        'avg_performance': avg_performance,
        'top_performance': top_performance,
        'goals_achieved': goals_achieved,
        'reviews_due': reviews_due,
        'reviews': reviews,
        'department_performance': department_performance,
    })
