import gettext
import json
import logging

from django.core.management import call_command
from proso_models.models import Item
from shutil import copyfile

import os

from collections import defaultdict
from django.conf import settings
from django.core.management.base import BaseCommand

from proso_flashcards.models import Context, Category


LOGGER = logging.getLogger('django.request')


class Command(BaseCommand):
    help = "Generate concepts to JSON file"
    default_lang = "cs"
    place_type_names = {
        'state': 'Státy',
        'state-by-city': 'Státy skrze hlavní města',
        'region': 'Regiony',
        'province': 'Provincie',
        'region_cz': 'Kraje',
        'region_it': 'Oblasti',
        'autonomous_comunity': 'Autonomní společenství',
        'bundesland': 'Spolkové země',
        'city': 'Města',
        'city-by-state': 'Hlavní města skrze státy',
        'river': 'Řeky',
        'reservoir': 'Vodní nádrže',
        'lake': 'Jezera',
        'sea': 'Moře',
        'mountains': 'Pohoří',
        'surface': 'Povrch',
        'island': 'Ostrovy',
        'district': 'Okresy',
    }

    def handle(self, *args, **options):
        def _get_lang(obj, lang):
            if lang in obj:
                return obj[lang]
            return obj[self.default_lang]

        domains = settings.LANGUAGE_DOMAINS
        langs = domains.keys()
        self.prepare_mo_files(langs)
        data = {
            "concepts": [],
            "action_names": {
                "practice": {},
                "view": {},
            },
            "tags": {
                "context": {
                    "names": {lang: "Oblast" for lang in langs},
                    "values": defaultdict(lambda: {})
                },
                "type": {
                    "names": {lang: "Typ místa" for lang in langs},
                    "values": defaultdict(lambda: {})
                },
            }
        }
        # TODO - add translations of tag names

        contexts = defaultdict(lambda: {})
        for context in Context.objects.all().values("identifier", "name", "lang"):
            contexts[context["identifier"]][context["lang"]] = context["name"]
            data["tags"]["context"]["values"][context["identifier"]][context["lang"]] = context["name"]
        types = Category.objects.filter(type='flashcard_type').values_list("identifier", flat=True).distinct()

        for lang in langs:
            translation = gettext.translation('djangojs', os.path.join(settings.BASE_DIR, "conf", "locale"), [lang])
            data["action_names"]["practice"][lang] = translation.gettext("Procvičovat")
            data["action_names"]["view"][lang] = translation.gettext("Přehled map")

        for context, lang_map in contexts.items():
            for type in types:
                languages = []
                for lang in langs:
                    try:
                        if len(Item.objects.filter_all_reachable_leaves(
                                [["context/"+context, "category/"+type]], lang)) > 0:
                            languages.append(lang)
                    except Exception:
                        pass
                if len(languages) == 0:
                    continue
                concept = {
                    "query": '[["context/{}", "category/{}"]]'.format(context, type),
                    "tags": ["type:{}".format(type), "context:{}".format(context)],
                    "names": {},
                    "actions": {
                        "practice": {},
                        "view": {},
                    }
                }
                for lang in languages:
                    translation = gettext.translation('djangojs', os.path.join(settings.BASE_DIR, "conf", "locale"), [lang])
                    name = translation.gettext(self.place_type_names[type])
                    concept["names"][lang] = "{} - {}".format(_get_lang(lang_map, lang), name)
                    data["tags"]["type"]["values"][type][lang] = name
                    concept["actions"]["practice"][lang] = "http://{}/practice/{}/{}".format(domains[lang], context, type)
                    concept["actions"]["view"][lang] = "http://{}/view/{}/{}".format(domains[lang], context, type)

                data["concepts"].append(concept)

        json.dump(data, open(os.path.join(settings.BASE_DIR, "data", "concepts.json"), "w"), indent=4, ensure_ascii=False)
        self.clean_up(langs)

    def prepare_mo_files(self, languages):
        for lang in languages:
            copyfile(os.path.join(settings.BASE_DIR, "geography", "static", "po", "{}.po".format(lang)),
                     os.path.join(settings.BASE_DIR, "conf", "locale", lang, "LC_MESSAGES", "djangojs.po"))
        call_command('compilemessages')

    def clean_up(self, languages):
        for lang in languages:
            os.remove(os.path.join(settings.BASE_DIR, "conf", "locale", lang, "LC_MESSAGES", "djangojs.po"))
            os.remove(os.path.join(settings.BASE_DIR, "conf", "locale", lang, "LC_MESSAGES", "djangojs.mo"))
