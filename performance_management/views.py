from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import PerformanceReview
from .forms import PerformanceReviewForm, PerformanceScoreFormSet


def review_list(request):
    reviews = PerformanceReview.objects.all().order_by('-created_at')
    return render(request, 'performance_management/review_list.html', {'reviews': reviews})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PerformanceReview
from .forms import PerformanceReviewForm, PerformanceScoreFormSet


# Add a review
def review_add(request):
    if request.method == 'POST':
        review_form = PerformanceReviewForm(request.POST)
        formset = PerformanceScoreFormSet(request.POST)

        if review_form.is_valid() and formset.is_valid():
            review = review_form.save()
            formset.instance = review
            formset.save()
            messages.success(request, "Performance review saved successfully!")
            return redirect('review_list')
    else:
        review_form = PerformanceReviewForm()
        formset = PerformanceScoreFormSet()

    return render(request, 'performance_management/review_form.html', {
        'review_form': review_form,
        'formset': formset,
        'readonly': False,
    })


# Edit a review
def review_edit(request, pk):
    review = get_object_or_404(PerformanceReview, pk=pk)
    if request.method == 'POST':
        review_form = PerformanceReviewForm(request.POST, instance=review)
        formset = PerformanceScoreFormSet(request.POST, instance=review)

        if review_form.is_valid() and formset.is_valid():
            review = review_form.save(commit=False)
            review.save()

            # Ensure formset is linked to this review
            formset.instance = review
            formset.save()

            messages.success(request, "Performance review updated successfully!")
            return redirect('review_list')
    else:
        review_form = PerformanceReviewForm(instance=review)
        formset = PerformanceScoreFormSet(instance=review)

    return render(request, 'performance_management/review_form.html', {
        'review_form': review_form,
        'formset': formset,
        'readonly': False,
    })


# View review details (read-only)
def review_view(request, pk):
    review = get_object_or_404(PerformanceReview, pk=pk)
    review_form = PerformanceReviewForm(instance=review)
    formset = PerformanceScoreFormSet(instance=review)

    # Make fields readonly
    for field in review_form.fields.values():
        field.disabled = True
    for form in formset.forms:
        for field in form.fields.values():
            field.disabled = True

    return render(request, 'performance_management/review_form.html', {
        'review_form': review_form,
        'formset': formset,
        'readonly': True,
    })


# Delete a review
def review_delete(request, pk):
    review = get_object_or_404(PerformanceReview, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Performance review deleted successfully!")
    return redirect('review_list')
