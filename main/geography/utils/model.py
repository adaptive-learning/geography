# -*- coding: utf-8 -*-
from django.utils.translation import pgettext, ugettext as _
from geography.models import Answer, Place, Value, DatabaseEnvironment, Test
from random import choice, shuffle
import logging

LOGGER = logging.getLogger(__name__)


class Question():
    options = []

    def __init__(self, place, options, map_place, ab_values, test_id):
        self.place = place
        self.map_place = map_place
        self.ab_values = ab_values
        self.options = options
        self.test_id = test_id
        if len(options) > 0:
            self.qtype = QuestionType(
                choice([Answer.FIND_ON_MAP, Answer.PICK_NAME]),
                self.place.type,
                len(options) + 1)
        else:
            self.qtype = QuestionType(Answer.FIND_ON_MAP, self.place.type, 0)

    def to_serializable(self):
        ret = self.qtype.to_serializable()
        ret['asked_code'] = self.place.code
        ret['map_code'] = self.map_place.place.code
        ret['place'] = self.place.name
        ret['ab_values'] = [v.value for v in self.ab_values]
        if self.test_id:
            ret['test_id'] = self.test_id
        if len(self.options) > 0:
            ret["options"] = sorted(
                map(
                    lambda o: dict([('code', o.code), ('name', o.name)]),
                    [self.place] + self.options),
                key=lambda x: x['name'])
        return ret


class QuestionService:

    def __init__(self, user, map_place, ab_env, target_probability=0.75, history_length=10):
        self.user = user
        self.map_place = map_place
        self.target_probability = target_probability
        self.history_length = history_length
        self.ab_env = ab_env

    def get_questions(self, n, place_types):
        test_candidates = Test.objects.get_test_places(
            self.user.id, self.map_place.place.id, place_types, n)
        candidates = []
        if test_candidates is not None and len(test_candidates) > 0:
            candidate_places, test_ids = zip(*test_candidates)
            candidates = zip(zip(candidate_places, [[] for i in test_candidates]), test_ids)
        shuffle(candidates)
        LOGGER.debug('user {0}: testing questions are {1}'.format(self.user, str(candidates)))
        candidates += zip(Place.objects.get_places_to_ask(
            self.user,
            self.map_place,
            n - len(candidates),
            place_types,
            DatabaseEnvironment(),
            self.ab_env), [None for i in range(n - len(candidates))])
        return [
            Question(
                place,
                options,
                self.map_place,
                self.ab_env.get_affecting_values(Place.AB_REASON_RECOMMENDATION),
                test_id).to_serializable()
            for ((place, options), test_id) in candidates]

    def answer(self, a, ip_address, language_code):
        place_asked = Place.objects.get(code=a["asked_code"])
        place_map = Place.objects.get(code=a["map_code"])
        try:
            if "answered_code" in a and a["answered_code"] != "":
                place_answered = Place.objects.get(code=a["answered_code"])
            else:
                place_answered = None
        except Place.DoesNotExist:
            place_answered = None
            code = a["answer_code"] if "answer_code" in a else None
            LOGGER.error("Place with code '{0}' does not exist.".format(code))

        answer_dict = {
            'user': self.user.id,
            'place_asked': place_asked.id,
            'place_answered': place_answered.id if place_answered else None,
            'place_map': place_map.id,
            'type': int(str(a["type"])[0]),
            'response_time': a["response_time"],
            'number_of_options': int(str(a["type"][1:])),
            'ip_address': ip_address if ip_address else None,
            'language_code': language_code,
        }
        if "options" in a:
            options = Place.objects.filter(
                code__in=[o["code"] for o in a["options"]],
            )
            answer_dict['options'] = [o.id for o in options]
        else:
            answer_dict['options'] = []
        if 'ab_values' in a:
            ab_values = Value.objects.filter(
                value__in=[v for v in a['ab_values']])
            answer_dict['ab_values'] = [v.id for v in ab_values]
        else:
            answer_dict['ab_values'] = []
        if 'test_id' in a:
            answer_dict['test_id'] = a['test_id']
        Answer.objects.save_with_listeners(answer_dict)


class QuestionType(object):

    @property
    def PLACE_HIGHLIGHTED(self):
        """
        These have to be functions because of i18n.
        They have to be evaluated after a specific language has been set.
        """
        return {
            Place.UNKNOWN: None,
            Place.STATE: pgettext('state', u'zvýrazněný'),
            Place.CITY: pgettext('city', u'zvýrazněné'),
            Place.WORLD: None,
            Place.CONTINENT: None,
            Place.RIVER: pgettext('river', u'zvýrazněná'),
            Place.LAKE: pgettext('lake', u'zvýrazněné'),
            Place.REGION_CZ: pgettext('region_cz', u'zvýrazněný'),
            Place.BUNDESLAND: pgettext('bundesland', u'zvýrazněná'),
            Place.PROVINCE: pgettext('province', u'zvýrazněná'),
            Place.REGION_IT: pgettext('region_it', u'zvýrazněná'),
            Place.REGION: pgettext('region', u'zvýrazněný'),
            Place.AUTONOMOUS_COMUNITY: pgettext('autonomous_comunity', u'zvýrazněná'),
            Place.MOUNTAINS: pgettext('mountains', u'zvýrazněné'),
            Place.ISLAND: pgettext('island', u'zvýrazněný'),
        }

    @property
    def PLACE_TYPE_SINGULAR(self):
        return {
            Place.UNKNOWN: _('unknown'),
            Place.STATE: _(u'stát'),
            Place.CITY: _(u'město'),
            Place.WORLD: None,
            Place.CONTINENT: None,
            Place.RIVER: _(u'řeka'),
            Place.LAKE: _(u'jezero'),
            Place.REGION_CZ: _(u'kraj'),
            Place.BUNDESLAND: _(u'spolková země'),
            Place.PROVINCE: _(u'provincie'),
            Place.REGION_IT: _(u'oblast'),
            Place.REGION: _(u'region'),
            Place.AUTONOMOUS_COMUNITY: _(u'autonomní společenství'),
            Place.MOUNTAINS: pgettext('singular', u'pohoří'),
            Place.ISLAND: _(u'ostrov'),
        }

    @property
    def PLACE_TYPE_SINGULAR_CHOICE(self):
        return {
            Place.BUNDESLAND: _(u'spolkovou zemi'),
            Place.PROVINCE: _(u'provincii'),
            Place.RIVER: _(u'řeku'),
        }

    @property
    def PLACE_TYPE_PLURAL_CHOICE(self):
        return {
            Place.UNKNOWN: _('unknown'),
            Place.STATE: _(u'států'),
            Place.CITY: _(u'měst'),
            Place.WORLD: None,
            Place.CONTINENT: None,
            Place.RIVER: _(u'řek'),
            Place.LAKE: _(u'jezer'),
            Place.REGION_CZ: _(u'regionů'),
            Place.BUNDESLAND: _(u'spolkových zemí'),
            Place.PROVINCE: _(u'provincií'),
            Place.REGION_IT: _(u'oblastí'),
            Place.REGION: _(u'regionů'),
            Place.AUTONOMOUS_COMUNITY: _(u'autonomních společenství'),
            Place.MOUNTAINS: pgettext('plural', u'pohoří'),
            Place.ISLAND: _(u'ostrovů'),
        }

    def __init__(self, type, place_type, number_of_options):
        self.type = type
        self.place_type = place_type
        self.number_of_options = number_of_options

    @property
    def text(self):
        place_singular = self.PLACE_TYPE_SINGULAR[self.place_type]
        place_plural_choice = self.PLACE_TYPE_PLURAL_CHOICE[self.place_type]
        place_singular_choice = self.PLACE_TYPE_SINGULAR_CHOICE.get(
            self.place_type, place_singular)
        highlighted = self.PLACE_HIGHLIGHTED[self.place_type]

        if self.type == Answer.FIND_ON_MAP:
            if self.number_of_options > 0:
                return _(u'Ze zvýrazněných %(place_plural)s na mapě vyber'
                         ) % {'place_plural': place_plural_choice}
            else:
                return _(u'Vyber na mapě %(place_singular)s'
                         ) % {'place_singular': place_singular_choice}
        else:
            return _(u'Jak se jmenuje %(place_singular)s %(highlighted)s na mapě?'
                     ) % {'place_singular': place_singular,
                          'highlighted': highlighted}

    def to_serializable(self):
        return {
            'type': str(self.type) + str(int(self.number_of_options)),
            'text': self.text,
        }

    def __str__(self):
        return "question-type [" + str(self.type) + "], number of options [" + str(self.number_of_options) + "]"
