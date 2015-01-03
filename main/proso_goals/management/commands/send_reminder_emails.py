# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from proso_goals.models import Goal
from django.core.mail import EmailMultiAlternatives
from logging import getLogger
from proso_goals.utils import get_reminder_email
from django.contrib.sites.models import Site
from geography.models.user import UserProfile, get_lang_from_last_answer
from django.utils import translation
from django.utils.translation import ugettext as _


LOGGER = getLogger(__name__)


class Command(BaseCommand):
    help = u"""Send emails to users who have set goals and are behind schedule"""

    def handle(self, *args, **options):
        send_reminder_emails()


def send_reminder_emails():
    goals = Goal.objects.goals_behind_schedule()
    goals_by_user = {}
    for g in goals:
        if g.user not in goals_by_user:
            goals_by_user[g.user] = []
        language_code = get_lang_from_last_answer(g.user)
        if language_code is not None:
            translation.activate(language_code)
        goals_by_user[g.user].append(g.to_serializable())
    for user in goals_by_user:
        send_emails = UserProfile.objects.get_profile(user).send_emails
        if user.email is not None and send_emails:
            send_reminder_email(goals_by_user[user], user)


def send_reminder_email(goals, user):
    language_code = get_lang_from_last_answer(user)
    if language_code is not None:
        translation.activate(language_code)
    [text_content, html_content] = get_reminder_email(goals, user)
    print text_content
    domain = Site.objects.get_current().domain
    mail = EmailMultiAlternatives(
        _(u'Je čas procvičovat slepé mapy'),
        text_content,
        'no-reply@' + domain,
        [user.email],
    )
    mail.attach_alternative(html_content, "text/html")
    mail.send()
    LOGGER.debug("email sent %s\n", text_content)
