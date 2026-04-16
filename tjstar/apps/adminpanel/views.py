import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from tjstar.apps.lookup.models import Presentation, TimeSlot


@login_required
def adminpanel(request):
    admingroup = Group.objects.filter(name='admins').first()
    if not admingroup or not request.user in admingroup.user_set.all():
        return render(request, 'adminpanel/not_admin.html')
    
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'No file uploaded.')
            return render(request, 'adminpanel/index.html')
        
        csv_file = request.FILES['csv_file']
        
        try:
            file_content = csv_file.read().decode('utf-8')
            reader = csv.reader(file_content.splitlines())
            
            rows = list(reader)
            
            if len(rows) == 0:
                messages.error(request, 'CSV file is empty.')
                return render(request, 'adminpanel/index.html')
            
            presentations_to_create = []
            for row_num, row in enumerate(rows, 1):
                """
                Expected columns: category, students, project title, abstract, 
                secondary director (optional), external mentor (optional), external mentor institute (optional),
                room number, time slot (single letter)
                """
                
                
                if len(row) != 9:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Expected 9 columns, got {len(row)}.'}
                    )
                
                category_str, authors_str, title, abstract, secondary_director, external_mentor, \
                    external_mentor_institute, room_number, timeslot_char = row
                
                # Validate category
                if not category_str.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Category cannot be empty.'}
                    )
                category_str = category_str.strip()
                valid_categories = [choice[0] for choice in Presentation.CATEGORY_CHOICES]
                if category_str not in valid_categories:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Invalid category "{category_str}". Must be one of: {", ".join(valid_categories)}'}
                    )
                
                # Validate and parse authors (comma-separated)
                if not authors_str.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Authors field cannot be empty.'}
                    )
                authors = [author.strip() for author in authors_str.split(',')]
                
                # Validate title
                if not title.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Project title cannot be empty.'}
                    )
                
                # Validate abstract
                if not abstract.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Abstract cannot be empty.'}
                    )
                
                # Secondary director is optional
                secondary_director = secondary_director.strip()
                
                # External mentor is optional
                external_mentor = external_mentor.strip()
                
                # External mentor institute is optional
                external_mentor_institute = external_mentor_institute.strip()
                
                # Validate room number
                if not room_number.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Room number cannot be empty.'}
                    )
                
                # Validate timeslot (single letter)
                if not timeslot_char.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Time slot cannot be empty.'}
                    )
                
                timeslot_char = timeslot_char.strip().upper()
                if len(timeslot_char) != 1:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Time slot must be a single letter, got "{timeslot_char}".'}
                    )
                
                # Find timeslot
                timeslot = TimeSlot.objects.filter(block=timeslot_char).first()
                if not timeslot:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Time slot "{timeslot_char}" does not exist.'}
                    )
                
                presentations_to_create.append({
                    'category': category_str,
                    'authors': authors,
                    'title': title.strip(),
                    'abstract': abstract.strip(),
                    'secondary_director': secondary_director,
                    'external_mentor': external_mentor,
                    'external_mentor_institute': external_mentor_institute,
                    'room_number': room_number.strip(),
                    'timeslot': timeslot,
                })
            
            # All validations passed, create presentations
            for pres_data in presentations_to_create:
                Presentation.objects.create(
                    category=pres_data['category'],
                    authors=pres_data['authors'],
                    title=pres_data['title'],
                    abstract=pres_data['abstract'],
                    secondary_director=pres_data['secondary_director'],
                    external_mentor=pres_data['external_mentor'],
                    external_mentor_institute=pres_data['external_mentor_institute'],
                    room_number=pres_data['room_number'],
                    timeslot=pres_data['timeslot']
                )
            
            messages.success(request, f'Successfully imported {len(presentations_to_create)} presentation(s).')
            return render(request, 'adminpanel/index.html')
        
        except Exception as e:
            return render(
                request,
                'adminpanel/error.html',
                {'error': f'Error processing file: {str(e)}'}
            )
    
    return render(request, 'adminpanel/index.html')
