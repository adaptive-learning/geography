from django.contrib.sites.models import Site
from django.template.loader import render_to_string


def get_reminder_email(goals, user):
    mail_obj = {
        "goals": goals,
        "user": user,
        "domain": "http://" + Site.objects.get_current().domain,
    }
    text_content = render_to_string("emails/goal_reminder.plain.txt", mail_obj)
    html_content = render_to_string("emails/goal_reminder.html", mail_obj)
    return [text_content, html_content]
