from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Presentation, TimeSlot, LabDirector


def home(request):
    return render(request, 'lookup/home.html')


def presentations(request):
    presentations_list = Presentation.objects.all().order_by('id')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        presentations_list = presentations_list.annotate(
            priority=Case(
                When(room_number__icontains=search_query, then=Value(0)),
                When(title__icontains=search_query, then=Value(1)),
                When(authors__icontains=search_query, then=Value(2)),
                When(abstract__icontains=search_query, then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).filter(
            Q(room_number__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(authors__icontains=search_query) |
            Q(abstract__icontains=search_query)
        ).order_by("priority")
    
    # Filter by timeslot
    timeslot_ids = request.GET.getlist('timeslot')
    if timeslot_ids:
        presentations_list = presentations_list.filter(timeslot__id__in=timeslot_ids)
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        presentations_list = presentations_list.filter(
            Q(category=category) | Q(secondary_lab__icontains=category)
        )
    
    # Filter by director
    director = request.GET.get('director', '')
    if director:
        for word in director.split():
                presentations_list = presentations_list.filter(
                    Q(primary_director__first_name__icontains=word) |
                    Q(primary_director__last_name__icontains=word) |
                    Q(primary_director__title__icontains=word) |
                    Q(secondary_director__icontains=word)
                )
        
        presentations_list = presentations_list.distinct()
    
    # Pagination
    paginator = Paginator(presentations_list, 36)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all timeslots for filter options
    timeslots = TimeSlot.objects.all()
    
    query_params = request.GET.copy()
    query_params.pop('page', None)
    
    context = {
        'query_string': query_params.urlencode(),
        'page_obj': page_obj,
        'timeslots': timeslots,
        'search_query': search_query,
        'selected_timeslots': timeslot_ids,
        'selected_category': category,
        'selected_director': director,
        'categories': Presentation.CATEGORY_CHOICES,
        'lab_directors': [(director.first_name + director.last_name, str(director)) for director in LabDirector.objects.all()]
    }
    
    return render(request, 'lookup/presentations.html', context)