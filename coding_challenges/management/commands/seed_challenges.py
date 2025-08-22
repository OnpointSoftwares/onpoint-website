import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from coding_challenges.models import Tag, Challenge, Badge

TAGS = [
    "arrays", "strings", "math", "dp", "graph", "sorting",
    "recursion", "greedy", "bitwise", "trees", "hashmap", "two-pointers",
]

BADGES = [
    {"name": "Bronze Coder", "points": 50, "icon": "award"},
    {"name": "Silver Coder", "points": 200, "icon": "award"},
    {"name": "Gold Coder", "points": 500, "icon": "award"},
    {"name": "Platinum Coder", "points": 1000, "icon": "award"},
]

EXAMPLES = [
    (
        "Sum of Two Numbers",
        "Given two integers a and b, return their sum.",
        "2 3",
        "5",
    ),
    (
        "Reverse String",
        "Given a string s, return it reversed.",
        "hello",
        "olleh",
    ),
    (
        "Max of Array",
        "Given n and an array of n integers, output the maximum value.",
        "5\n1 3 9 2 7",
        "9",
    ),
]

class Command(BaseCommand):
    help = "Seed tags, badges, and 100 sample coding challenges"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Number of challenges to create')
        parser.add_argument('--flush', action='store_true', help='Delete existing challenges before seeding')

    def handle(self, *args, **options):
        count = options['count']
        flush = options['flush']

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding Coding Challenges...'))

        # Tags
        tag_objs = []
        for t in TAGS:
            tag, _ = Tag.objects.get_or_create(name=t)
            tag_objs.append(tag)
        self.stdout.write(self.style.SUCCESS(f"Tags ready: {len(tag_objs)}"))

        # Badges
        for b in BADGES:
            Badge.objects.get_or_create(
                name=b["name"],
                defaults={"points_threshold": b["points"], "icon": b["icon"], "description": f"Reach {b['points']} points"},
            )
        self.stdout.write(self.style.SUCCESS("Badges ready"))

        # Challenges
        if flush:
            Challenge.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing challenges deleted."))

        difficulties = ['easy', 'medium', 'hard']
        created = 0
        for i in range(1, count + 1):
            # rotate through sample example templates
            ex = EXAMPLES[(i - 1) % len(EXAMPLES)]
            title_base = ex[0]
            title = f"{title_base} #{i}"
            problem = ex[1]
            example_in = ex[2]
            example_out = ex[3]

            challenge, made = Challenge.objects.get_or_create(
                title=title,
                defaults={
                    'problem_statement': problem,
                    'difficulty': random.choices(difficulties, weights=[5, 3, 2])[0],
                    'example_input': example_in,
                    'example_output': example_out,
                    'time_limit_ms': random.choice([1000, 1500, 2000, 2500]),
                    'memory_limit_kb': random.choice([131072, 262144, 524288]),
                    'allowed_languages': ['python', 'cpp', 'java', 'javascript'],
                    'created_at': timezone.now(),
                }
            )
            if made:
                # assign 1-3 random tags
                k = random.randint(1, 3)
                challenge.tags.set(random.sample(tag_objs, k))
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Challenges created: {created}, total in DB: {Challenge.objects.count()}"))

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
