from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
import datetime
from ...models import Presentation, TimeSlot


class Command(BaseCommand):
    help = 'Populate database with test data for presentations'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        self.stdout.write('Creating TimeSlots...')
        time_slots_data = [
            {'block': 'A', 'start_time': '09:00', 'end_time': '10:00'},
            {'block': 'B', 'start_time': '10:00', 'end_time': '11:00'},
            {'block': 'C', 'start_time': '11:00', 'end_time': '12:00'},
            {'block': 'D', 'start_time': '13:00', 'end_time': '14:00'},
        ]
        
        for ts_data in time_slots_data:
            TimeSlot.objects.get_or_create(
                block=ts_data['block'],
                defaults={
                    'start_time': datetime.time.fromisoformat(ts_data['start_time']),
                    'end_time': datetime.time.fromisoformat(ts_data['end_time']),
                }
            )
        
        self.stdout.write('TimeSlots created.')

        category_templates = {
            'astro': {
                'titles': [
                    'Discovery of {} exoplanet system',
                    'Analysis of {} star formation',
                    'Gravitational lensing observations of {}',
                    'Black hole dynamics in {}',
                    'Cosmological implications of {} observations',
                    'Spectroscopic study of {}',
                    'Pulsar timing analysis in {}',
                    'Supernova remnants in {}',
                ]
            },
            'bio': {
                'titles': [
                    'Novel {} enzyme in {} organisms',
                    'CRISPR-based treatment for {} disease',
                    'Genetic analysis of {} species adaptation',
                    'Protein folding dynamics in {}',
                    'Viral vector development for {} therapy',
                    'Microbiome analysis of {} environment',
                    'Gene expression patterns in {}',
                ]
            },
            'chem': {
                'titles': [
                    'Synthesis of {} nanoparticles with {} properties',
                    'Catalytic mechanism of {} reaction',
                    'Chemical analysis of {} compounds',
                    'Electrochemical characterization of {}',
                    'Quantum chemical study of {}',
                    'Surface chemistry of {} nanomaterials',
                ]
            },
            'cs': {
                'titles': [
                    'Novel {} algorithm for {} optimization',
                    'Machine learning approach to {} prediction',
                    'Distributed {} system architecture',
                    'Cybersecurity protocol for {} networks',
                    'Blockchain-based {} solution',
                    'Cloud computing optimization using {}',
                ]
            },
            'eng': {
                'titles': [
                    'Design and analysis of {} structure',
                    'Optimization of {} system efficiency',
                    'Material characterization for {} applications',
                    'Mechanical testing of {} components',
                    'Thermal analysis of {} devices',
                ]
            },
            'mbw': {
                'titles': [
                    'Development of {} mobile application',
                    'Web framework for {} services',
                    '{}responsive design patterns',
                    'API optimization for {} platform',
                    'User interface design for {} application',
                ]
            },
            'neuro': {
                'titles': [
                    'Neural mechanisms of {} in {}',
                    'Brain imaging study of {} disorder',
                    'Synaptic plasticity in {} pathway',
                    'Neurochemical analysis of {}',
                    'Behavioral consequences of {} intervention',
                ]
            },
            'ocean': {
                'titles': [
                    'Oceanographic study of {} current',
                    'Marine ecosystem analysis in {} region',
                    'Sediment characterization from {} region',
                    'Water chemistry analysis of {} system',
                    'Geological features of {} seafloor',
                ]
            },
            'qlab': {
                'titles': [
                    'Quantum entanglement in {} system',
                    'Photonic {} implementation',
                    'Optical properties of {} material',
                    'Quantum interference in {} setup',
                    'Laser-based study of {}',
                ]
            }
        }

        # Generate presentations for each category
        categories = [code for code, _ in Presentation.CATEGORY_CHOICES]
        timeslots = list(TimeSlot.objects.all())

        self.stdout.write(f'Generating presentations for {len(categories)} categories...')

        for category_code in categories:
            self.stdout.write(f'Processing category: {category_code}')
            
            templates = category_templates.get(category_code, category_templates['cs'])
            
            for i in range(30):
                num_authors = random.randint(1, 4)
                authors = [self.fake.name() for _ in range(num_authors)]

                title_template = random.choice(templates['titles'])
                title = title_template.format(
                    self.fake.word(),
                    self.fake.word() if '{}' in title_template[title_template.index('{}')+2:] else ''
                ).strip()

                
                abstract = self.fake.paragraph(nb_sentences=5)

                # Generate other fields
                external_mentor = self.fake.name()
                secondary_director = self.fake.name()
                external_mentor_institute = self.fake.company()
                room_number = str(random.randint(100, 500))
                timeslot = random.choice(timeslots)

                # Create presentation
                Presentation.objects.create(
                    authors=authors,
                    title=title,
                    abstract=abstract,
                    category=category_code,
                    external_mentor=external_mentor,
                    secondary_director=secondary_director,
                    external_mentor_institute=external_mentor_institute,
                    room_number=room_number,
                    timeslot=timeslot,
                )

            self.stdout.write(self.style.SUCCESS(f'Created 30 presentations for {category_code}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created 270 presentations in total!'))
