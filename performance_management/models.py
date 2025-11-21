from django.db import models
from masters.models import PerformanceKPI
from employee_management.models import Employee

class PerformanceReview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    review_period = models.CharField(max_length=20)  # e.g. "Q1 2025"
    feedback = models.TextField(blank=True)
    reviewed_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_score(self):
        scores = self.scores.all()
        if scores.exists():
            return round(sum(s.score for s in scores) / scores.count(), 2)
        return None
    

    def rating(self):
        """
        Calculate rating based on % of average score against max_score
        """
        scores = self.scores.all()
        if not scores.exists():
            return "Not Rated"

        total_score = sum(s.score for s in scores)
        total_max = sum(s.kpi.max_score for s in scores)

        if total_max == 0:
            return "Not Rated"

        percent = (total_score / total_max) * 100

        if percent >= 90:
            return "Excellent"
        elif percent >= 75:
            return "Good"
        elif percent >= 50:
            return "Average"
        else:
            return "Poor"

    def __str__(self):
        return f"{self.employee} - {self.review_period} by {self.reviewed_by}"


class PerformanceScore(models.Model):
    review = models.ForeignKey(
        PerformanceReview,
        on_delete=models.CASCADE,
        related_name="scores"
    )
    kpi = models.ForeignKey(PerformanceKPI, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.review.employee} - {self.kpi.name} ({self.score})"
