import csv
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from tjstar.apps.lookup.models import Presentation, TimeSlot, LabDirector


@login_required
def adminpanel(request):
    if not request.user.groups.filter(name='admins').exists():
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

            if not rows:
                messages.error(request, 'CSV file is empty.')
                return render(request, 'adminpanel/index.html')

            if rows[0][0].lower() == "category":
                rows = rows[1:]

            presentations_to_create = []

            for row_num, row in enumerate(rows, start=1):
                if len(row) != 13:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Expected 13 columns, got {len(row)}.'}
                    )

                (
                    category_str,
                    authors_str,
                    title,
                    abstract,
                    primary_director,
                    secondary_lab,
                    secondary_director,
                    external_mentor,
                    external_mentor_institute,
                    room_number,
                    timeslot_char,
                    start_time,
                    end_time
                ) = row


                category_str = category_str.strip()
                valid_categories = [choice[0] for choice in Presentation.CATEGORY_CHOICES]

                if category_str not in valid_categories:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {
                            'error': f'Row {row_num}: Invalid category "{category_str}". '
                                     f'Must be one of: {", ".join(valid_categories)}'
                        }
                    )

                if not authors_str.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Students field cannot be empty.'}
                    )

                authors = [a.strip() for a in authors_str.split(',') if a.strip()]


                if not title.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Project title cannot be empty.'}
                    )

                # if not abstract.strip():
                #     return render(
                #         request,
                #         'adminpanel/error.html',
                #         {'error': f'Row {row_num}: Abstract cannot be empty.'}
                #     )

                if not room_number.strip():
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Room cannot be empty.'}
                    )


                timeslot_char = timeslot_char.strip().upper()

                if len(timeslot_char) != 1:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: TimeSlotID must be a single letter.'}
                    )

                timeslot = TimeSlot.objects.filter(block=timeslot_char).first()

                if not timeslot:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Time slot "{timeslot_char}" does not exist.'}
                    )
                    
                start_time_obj = datetime.strptime(start_time, '%H:%M %p').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M %p').time()
                
                if len(primary_director.split()) not in [2, 3]:
                    return render(
                        request,
                        'adminpanel/error.html',
                        {'error': f'Row {row_num}: Primary director "{primary_director}" is in an invalid format.'}
                    )
                
                primary_director_strs = primary_director.split()
                
                if len(primary_director_strs) == 2:
                    primary_director_obj, created = LabDirector.objects.get_or_create(
                        first_name=primary_director_strs[0],
                        last_name=primary_director_strs[1],
                    )
                else:
                    primary_director_obj, created = LabDirector.objects.get_or_create(
                        first_name=primary_director_strs[1],
                        last_name=primary_director_strs[2],
                        title=primary_director_strs[0],
                    )

                presentations_to_create.append(
                    Presentation(
                        category=category_str,
                        authors=authors,
                        title=title.strip(),
                        abstract=abstract.strip(),
                        primary_director=primary_director_obj,
                        secondary_lab=secondary_lab.strip(),
                        secondary_director=secondary_director.strip(),
                        external_mentor=external_mentor.strip(),
                        external_mentor_institute=external_mentor_institute.strip(),
                        room_number=room_number.strip(),
                        timeslot=timeslot,
                        start_time=start_time_obj,
                        end_time=end_time_obj
                    )
                )

            with transaction.atomic():
                Presentation.objects.bulk_create(presentations_to_create)

            messages.success(
                request,
                f'Successfully imported {len(presentations_to_create)} presentation(s).'
            )

            return render(request, 'adminpanel/index.html')

        except Exception as e:
            return render(
                request,
                'adminpanel/error.html',
                {'error': f'Error processing file: {str(e)}'}
            )

    return render(request, 'adminpanel/index.html')