def view_cv(request):
    cv = get_object_or_404(CV, user=request.user)
    experiences = Experience.objects.filter(cv=cv).order_by('-start_date')
    educations = Education.objects.filter(cv=cv).order_by('-start_date')
    
    template = request.GET.get('template', 'default')
    
    context = {
        'cv': cv,
        'experiences': experiences,
        'educations': educations,
        'template': template
    }
    
    return render(request, 'cv/view_cv.html', context) 