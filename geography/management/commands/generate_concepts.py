import gettext
import json

from django.core.management import call_command
from shutil import copyfile

import os

from collections import defaultdict
from django.conf import settings
from django.core.management.base import BaseCommand

from proso_flashcards.models import Context, Term, Flashcard


class Command(BaseCommand):
    help = "Generate concepts to JSON file"
    default_lang = "cs"
    place_type_names = {
        'state' : 'Státy',
        'state-by-city' : 'Státy skrze hlavní města',
        'region' : 'Regiony',
        'province' : 'Provincie',
        'region_cz' : 'Kraje',
        'region_it' : 'Oblasti',
        'autonomous_Comunity' : 'Autonomní společenství',
        'bundesland' : 'Spolkové země',
        'city' : 'Města',
        'city-by-state' : 'Hlavní města skrze státy',
        'river' : 'Řeky',
        'reservoir' : 'Vodní nádrže',
        'lake' : 'Jezera',
        'sea' : 'Moře',
        'mountains' : 'Pohoří',
        'surface' : 'Povrch',
        'island' : 'Ostrovy',
    }

    def handle(self, *args, **options):
        def _get_lang(obj, lang):
            if lang in obj:
                return obj[lang]
            return obj[self.default_lang]

        data = {"concepts": [], "action_names": {
            "practice": {},
            "view": {},
        }}

        contexts = defaultdict(lambda: {})
        for context in Context.objects.all().values("identifier", "name", "lang"):
            contexts[context["identifier"]][context["lang"]] = context["name"]
        types = Term.objects.all().values_list("type", flat=True).distinct()
        domains = settings.LANGUAGE_DOMAINS

        self.prepare_mo_files(domains.keys())

        for lang in domains.keys():
            translation = gettext.translation('djangojs', "conf/locale/", [lang])
            data["action_names"]["practice"][lang] = translation.gettext("Procvičovat")
            data["action_names"]["view"][lang] = translation.gettext("Přehled map")

        for context, lang_map in contexts.items():
            for type in types:
                languages = []
                for lang in domains.keys():
                    if len(Flashcard.objects.filtered_ids([], [context], [type], [], lang)[0]) > 0:
                        languages.append(lang)
                if len(languages) == 0:
                    continue
                concept = {
                    "query": 'contexts=["{}"]&categories=[]&types=["{}"]'.format(context, type),
                    "tags": ["type:{}".format(type), "context:{}".format(context)],
                    "names": {},
                    "actions": {
                        "practice": {},
                        "view": {},
                    }
                }
                for lang in languages:
                    translation = gettext.translation('djangojs', "conf/locale/", [lang])
                    concept["names"][lang] = "{} - {}".format(_get_lang(lang_map, lang), translation.gettext(self.place_type_names[type]))
                    concept["actions"]["practice"][lang] = "http://{}/practice/{}/{}".format(domains[lang], context, type)
                    concept["actions"]["view"][lang] = "http://{}/view/{}/{}".format(domains[lang], context, type)

                data["concepts"].append(concept)

        json.dump(data, open(os.path.join(settings.BASE_DIR, "data", "concepts.json"), "w"), indent=4, ensure_ascii=False)
        self.clean_up(domains.keys())

    def prepare_mo_files(self, languages):
        for lang in languages:
            copyfile(os.path.join(settings.BASE_DIR, "geography", "static", "po", "{}.po".format(lang)),
                     os.path.join(settings.BASE_DIR, "conf", "locale", lang, "LC_MESSAGES", "djangojs.po"))
        call_command('compilemessages')

    def clean_up(self, languages):
        for lang in languages:
            os.remove(os.path.join(settings.BASE_DIR, "conf", "locale", lang, "LC_MESSAGES", "djangojs.po"))
            os.remove(os.path.join(settings.BASE_DIR, "conf", "locale", lang, "LC_MESSAGES", "djangojs.mo"))
