# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.template import loader
from django.conf import settings
import os
from django.core.mail import send_mail
from proso_flashcards.models import Flashcard
from proso_user.models import UserProfile
from django.utils.translation import ugettext as _


class Command(BaseCommand):

    def handle(self, *args, **options):
        questions = self.get_questions()
        to_list = self.get_subscribers()
        for to in to_list:
            self.send_mail(to, questions)
        print 'Mail sent to %d users' % len(to_list)

    def send_mail(self, to, questions):
        data = {
            'domain': settings.LANGUAGE_DOMAINS[settings.LANGUAGE_CODE],
            'questions': questions,
            'mail': to,
        }
        html_message = loader.render_to_string(
            os.path.join(settings.BASE_DIR,
                         'geography/templates/reminder_email.html'), data)
        message = loader.render_to_string(
            os.path.join(settings.BASE_DIR,
                         'geography/templates/reminder_email.txt'), data)
        subject = _(u'Víš kde leží') + ' ' + questions[0].term.name + '?'
        from_email = 'SlepeMapy.cz <info@slepemapy.cz>'
        send_mail(subject, message, from_email, (to,),
                  fail_silently=True, html_message=html_message)

    def get_subscribers(self):
        profiles = UserProfile.objects.filter(
            send_emails=True).exclude(user__email='').select_related('user')
        return [p.user.email for p in profiles]

    def get_questions(self):
        flashcards = Flashcard.objects.filter(
            lang=settings.LANGUAGE_CODE).order_by('?')[:5]
        return flashcards
