# -*- coding: utf-8 -*-
from geography.models import Answer
from geography.models import Place
from random import choice
import logging


LOGGER = logging.getLogger(__name__)


class Question():
    options = []

    def __init__(self, place, number_of_options, map_place):
        self.place = place
        self.map_place = map_place
        if number_of_options > 1:
            self.qtype = QuestionType(
                choice([Answer.FIND_ON_MAP, Answer.PICK_NAME]),
                number_of_options)
        else:
            self.qtype = QuestionType(Answer.FIND_ON_MAP, 0)
        if number_of_options > 1:
            self.options = self.get_options(self.qtype.number_of_options)

    def to_serializable(self):
        ret = self.qtype.to_serializable()
        ret.update(self.place.to_serializable())
        ret["place"] = ret["name"]
        ret.pop("name")
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

    def __init__(self, user, map_place):
        self.user = user
        self.map_place = map_place

    def get_questions(self, n):
        candidates = Place.objects.get_places_to_ask(self.user, self.map_place, 0.75, n)
        LOGGER.debug(
            "question candidates with predicted probability for map %s are %s",
            str(self.map_place),
            str(candidates))
        candidates = map(
            lambda (place, prediction): (place, self.number_of_options(prediction, 0.75)),
            candidates)
        LOGGER.debug(
            "question candidates with number of options for map %s are %s",
            str(self.map_place),
            str(candidates))
        return [
            Question(
                place,
                options,
                self.map_place).to_serializable()
            for (place, options) in candidates]

    def number_of_options(self, prob_real, prob_expected):
        g = min(0.5, max(0, prob_expected - prob_real) / (1 - prob_real))
        k = round(1.0 / g) if g != 0 else 1
        return 1 if k > 6 else k

    def answer(self, a):
        place = Place.objects.get(code=a["code"])
        try:
            place_answered = Place.objects.get(
                code=a[
                    "answer"]) if "answer" in a and a[
                "answer"] != "" else None
        except Place.DoesNotExist:
            place_answered = None
            code = a["answer"] if "answer" in a else None
            LOGGER.error("Place with code '{0}' does not exist.".format(code))

        answer = Answer(
            user=self.user,
            place_asked=place,
            place_answered=place_answered,
            type=int(str(a["type"])[0]),
            response_time=a["response_time"],
            number_of_options=int(str(a["type"][1:]))
        )
        answer.save()
        if "options" in a:
            answer.options = Place.objects.filter(
                code__in=[o["code"] for o in a["options"]],
            )
        answer.save(True)


class QuestionType(object):

    def __init__(self, type, number_of_options):
        self.type = type
        self.number_of_options = number_of_options

    @property
    def text(self):
        if self.type == Answer.FIND_ON_MAP:
            if self.number_of_options > 0:
                return u"Ze zvýrazněných států na mapě vyber"
            else:
                return u"Vyber na mapě stát"
        else:
            return u"Jak se jmenuje stát zvýrazněný na mapě?"

    def to_serializable(self):
        return {
            'type': str(self.type) + str(int(self.number_of_options)),
            'text': self.text,
        }

    def __str__(self):
        return "question-type [" + str(self.type) + "], number of options [" + str(self.number_of_options) + "]"
