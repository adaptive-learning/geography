# -*- coding: utf-8 -*-
from geography.models import Answer, Place, Value
from random import choice
from math import floor
import logging

LOGGER = logging.getLogger(__name__)


class Question():
    options = []

    def __init__(self, place, number_of_options, map_place, ab_values):
        self.place = place
        self.map_place = map_place
        self.ab_values = ab_values
        if number_of_options > 1:
            self.qtype = QuestionType(
                choice([Answer.FIND_ON_MAP, Answer.PICK_NAME]),
                self.place.type,
                number_of_options)
        else:
            self.qtype = QuestionType(Answer.FIND_ON_MAP, self.place.type, 0)
        if number_of_options > 1:
            self.options = self.get_options(self.qtype.number_of_options)

    def to_serializable(self):
        ret = self.qtype.to_serializable()
        ret['asked_code'] = self.place.code
        ret['map_code'] = self.map_place.place.code
        ret['place'] = self.place.name
        ret['ab_values'] = [v.value for v in self.ab_values]
        if (self.options != []):
            ret["options"] = self.options
        return ret

    def get_options(self, n):
        ps = [self.place]
        ps += self.place.confusing_places(self.map_place, n - 1)
        options = [p.to_serializable() for p in ps]
        options.sort(key=lambda tup: tup["name"])
        return options


class QuestionService:

    def __init__(self, user, map_place, ab_env, target_probability=0.75, history_length=10):
        self.user = user
        self.map_place = map_place
        self.target_probability = target_probability
        self.history_length = history_length
        self.ab_env = ab_env

    def get_questions(self, n, place_types):
        target_probability = self.adjust_target_probability()
        candidates = Place.objects.get_places_to_ask(
            self.user,
            self.map_place,
            target_probability,
            n,
            place_types,
            self.ab_env)
        candidates = map(
            lambda (place, raw): (place, self.number_of_options(raw['predicted_probability'], 0.75, raw['number_of_answers'])),
            candidates)
        LOGGER.debug(
            "user %s, question candidates with number of options for map %s are %s",
            str(self.user),
            str(self.map_place),
            str(candidates))
        return [
            Question(
                place,
                options,
                self.map_place,
                self.ab_env.get_affecting_values(Place.AB_REASON_RECOMMENDATION)).to_serializable()
            for (place, options) in candidates]

    def adjust_target_probability(self):
        success_rate = Answer.objects.get_success_rate(self.user, self.history_length)
        norm = 1 - self.target_probability if success_rate > self.target_probability else self.target_probability
        correction = ((self.target_probability - success_rate) / norm) * (1 - norm)
        return self.target_probability + correction

    def number_of_options(self, prob_real, prob_expected, number_of_answers):
        round_fun = round if number_of_answers else floor
        g = min(0.5, max(0, prob_expected - prob_real) / max(1 - prob_real, 0.0001))
        k = round_fun(1.0 / g) if g != 0 else 1
        return 1 if k > 6 else k

    def answer(self, a, ip_address):
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
        Answer.objects.save_with_listeners(answer_dict)


class QuestionType(object):

    GENUS_MASCULINE = 0
    GENUS_FEMININE = 1
    GENUS_NEUTER = 2

    PLACE_TYPE_GENUS = {
        Place.UNKNOWN: None,
        Place.STATE: GENUS_MASCULINE,
        Place.CITY: GENUS_NEUTER,
        Place.WORLD: GENUS_MASCULINE,
        Place.CONTINENT: GENUS_MASCULINE,
        Place.RIVER: GENUS_FEMININE,
        Place.LAKE: GENUS_NEUTER,
        Place.REGION_CZ: GENUS_MASCULINE,
        Place.BUNDESLAND: GENUS_FEMININE,
        Place.PROVINCE: GENUS_FEMININE,
        Place.REGION_IT: GENUS_FEMININE,
        Place.REGION: GENUS_MASCULINE,
        Place.AUTONOMOUS_COMUNITY: GENUS_NEUTER,
        Place.MOUNTAINS: GENUS_NEUTER,
        Place.ISLAND: GENUS_MASCULINE,
    }

    PLACE_TYPE_SINGULAR = {
        Place.UNKNOWN: 'unknown',
        Place.STATE: u'stát',
        Place.CITY: u'město',
        Place.WORLD: u'svět',
        Place.CONTINENT: u'kontinent',
        Place.RIVER: u'řeka',
        Place.LAKE: u'jezero',
        Place.REGION_CZ: u'kraj',
        Place.BUNDESLAND: u'spolková země',
        Place.PROVINCE: u'provincie',
        Place.REGION_IT: u'oblast',
        Place.REGION: u'region',
        Place.AUTONOMOUS_COMUNITY: u'autonomní společenství',
        Place.MOUNTAINS: u'pohoří',
        Place.ISLAND: u'ostrov',
    }
    PLACE_TYPE_SINGULAR_CHOICE = {
        Place.BUNDESLAND: u'spolkovou zemi',
        Place.PROVINCE: u'provincii',
        Place.RIVER: u'řeku',
    }
    PLACE_TYPE_PLURAL_CHOICE = {
        Place.UNKNOWN: 'unknown',
        Place.STATE: u'států',
        Place.CITY: u'měst',
        Place.WORLD: u'světů',
        Place.CONTINENT: u'kontinentů',
        Place.RIVER: u'řek',
        Place.LAKE: u'jezer',
        Place.REGION_CZ: u'regionů',
        Place.BUNDESLAND: u'spolkových zemí',
        Place.PROVINCE: u'provincií',
        Place.REGION_IT: u'oblastí',
        Place.REGION: u'regionů',
        Place.AUTONOMOUS_COMUNITY: u'autonomních společenství',
        Place.MOUNTAINS: u'pohoří',
        Place.ISLAND: u'ostrovů',
    }

    def __init__(self, type, place_type, number_of_options):
        self.type = type
        self.place_type = place_type
        self.number_of_options = number_of_options

    @property
    def text(self):
        place_singular = QuestionType.PLACE_TYPE_SINGULAR[self.place_type]
        place_plural_choice = QuestionType.PLACE_TYPE_PLURAL_CHOICE[self.place_type]
        place_singular_choice = QuestionType.PLACE_TYPE_SINGULAR_CHOICE.get(
            self.place_type, place_singular)

        if self.type == Answer.FIND_ON_MAP:
            if self.number_of_options > 0:
                return u"Ze zvýrazněných " + place_plural_choice + u" na mapě vyber"
            else:
                return u"Vyber na mapě " + place_singular_choice
        else:
            return u"Jak se jmenuje " + place_singular + u" " + self.highlighted + u" na mapě?"

    @property
    def highlighted(self):
        genus = QuestionType.PLACE_TYPE_GENUS[self.place_type]
        if genus == QuestionType.GENUS_MASCULINE:
            return u"zvýrazněný"
        elif genus == QuestionType.GENUS_FEMININE:
            return u"zvýrazněná"
        else:
            return u"zvýrazněné"

    def to_serializable(self):
        return {
            'type': str(self.type) + str(int(self.number_of_options)),
            'text': self.text,
        }

    def __str__(self):
        return "question-type [" + str(self.type) + "], number of options [" + str(self.number_of_options) + "]"
