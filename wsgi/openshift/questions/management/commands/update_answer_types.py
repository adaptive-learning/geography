
from django.core.management.base import NoArgsCommand

from questions.models import Answer, QuestionTypeFactory


class Command(NoArgsCommand):
    help = u"""Update confused states from answers"""

    def handle_noargs(self, **options):
        answers = Answer.objects.all()
        for a in answers:
            a.type = QuestionTypeFactory.get_instance_by_id(a.type).nid
            a.save()
