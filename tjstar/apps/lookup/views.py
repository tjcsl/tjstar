from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Presentation, TimeSlot


def home(request):
    return render(request, 'lookup/home.html')


def schedule(request):
    schedule_items = [
        {
            'time': '8:40 - 9:50 AM',
            'title': 'Keynote Address',
            'description': 'TJ 2001 Graduate and Baltimore Orioles President Mike Elias',
        },
        {
            'time': '10:00 - 10:45 AM',
            'title': 'Block A',
            'description': '',
        },
        {
            'time': '10:55 - 11:40 AM',
            'title': 'Block B',
            'description': '',
        },
        {
            'time': '11:50 - 12:35 PM',
            'title': 'Block C',
            'description': '',
        },
        {
            'time': '12:35 - 1:25 PM',
            'title': 'Lunch',
            'description': '',
        },
    ]

    return render(request, 'lookup/schedule.html', {'schedule_items': schedule_items})


def presentations(request):
    presentations_list = Presentation.objects.all().order_by('id')
    
    search_query = request.GET.get('q', '')
    if search_query:
        presentations_list = presentations_list.filter(
            Q(title__icontains=search_query) |
            Q(abstract__icontains=search_query) |
            Q(authors__icontains=search_query)
        )
    
    timeslot_ids = request.GET.getlist('timeslot')
    selected_timeslot_ids = []
    if timeslot_ids:
        selected_timeslot_ids = [int(timeslot_id) for timeslot_id in timeslot_ids if timeslot_id.isdigit()]
        presentations_list = presentations_list.filter(timeslot__id__in=timeslot_ids)
    
    category = request.GET.get('category', '')
    if category:
        presentations_list = presentations_list.filter(category=category)
    
    director = request.GET.get('director', '')
    if director:
        presentations_list = presentations_list.filter(secondary_director=director)
    
    paginator = Paginator(presentations_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    timeslots = TimeSlot.objects.all()
    timeslot_page_size = 4
    timeslot_page = int(request.GET.get('timeslot_page', '1'))
    timeslot_page_count = max(1, (timeslots.count() + timeslot_page_size - 1) // timeslot_page_size)
    timeslot_page = max(1, min(timeslot_page, timeslot_page_count))
    timeslot_start = (timeslot_page - 1) * timeslot_page_size
    timeslot_end = timeslot_start + timeslot_page_size
    visible_timeslots = timeslots[timeslot_start:timeslot_end]
    
    # Get distinct lab directors
    all_directors = Presentation.objects.filter(secondary_director__gt='').values_list('secondary_director', flat=True).distinct().order_by('secondary_director')
    
    context = {
        'page_obj': page_obj,
        'timeslots': timeslots,
        'visible_timeslots': visible_timeslots,
        'timeslot_page': timeslot_page,
        'timeslot_page_count': timeslot_page_count,
        'search_query': search_query,
        'selected_timeslots': selected_timeslot_ids,
        'selected_category': category,
        'selected_director': director,
        'categories': Presentation.CATEGORY_CHOICES,
        'directors': all_directors,
    }
    
    return render(request, 'lookup/presentations.html', context)