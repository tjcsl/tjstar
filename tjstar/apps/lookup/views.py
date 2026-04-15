from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Presentation, TimeSlot


def home(request):
    return render(request, 'lookup/home.html')


def presentations(request):
    presentations_list = Presentation.objects.all()
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        presentations_list = presentations_list.filter(
            Q(title__icontains=search_query) |
            Q(abstract__icontains=search_query) |
            Q(authors__icontains=search_query)
        )
    
    # Filter by timeslot
    timeslot_ids = request.GET.getlist('timeslot')
    if timeslot_ids:
        presentations_list = presentations_list.filter(timeslot__id__in=timeslot_ids)
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        presentations_list = presentations_list.filter(category=category)
    
    # Pagination
    paginator = Paginator(presentations_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all timeslots for filter options
    timeslots = TimeSlot.objects.all()
    
    context = {
        'page_obj': page_obj,
        'timeslots': timeslots,
        'search_query': search_query,
        'selected_timeslots': timeslot_ids,
        'selected_category': category,
        'categories': Presentation.CATEGORY_CHOICES,
    }
    
    return render(request, 'lookup/presentations.html', context)