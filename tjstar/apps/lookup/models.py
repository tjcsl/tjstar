from django.db import models


class TimeSlot(models.Model):
    block = models.CharField(max_length=1)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.block}: {self.start_time} - {self.end_time}"


class Presentation(models.Model):
    CATEGORY_CHOICES = [
        ('astro', 'Astronomy and Astrophysics'),
        ('bio', 'Biotechnology and Life Sciences'),
        ('chem', 'Chemical Analysis and Nanochemistry'),
        ('cs', 'Computer Systems'), # eww
        ('eng', 'Engineering'),
        ('mbw', 'Mobile and Web Application Development'),
        ('neuro', 'Neuroscience'),
        ('ocean', 'Oceanography and Geophysical Systems'),
        ('qlab', 'Quantum Physics and Optics')
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    authors = models.JSONField(default=list)
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    cross_linked_labs = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='linked_presentations',
        blank=True
    )
    secondary_director = models.CharField(max_length=255, blank=True)
    external_mentor = models.CharField(max_length=255, blank=True)
    external_mentor_institute = models.CharField(max_length=255, blank=True)
    room_number = models.CharField(max_length=50)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)

    def __str__(self):
        return self.title