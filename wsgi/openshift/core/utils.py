# -*- coding: utf-8 -*-
from core.models import Answer, Place, Student, UsersPlace, ConfusedPlaces
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import simplejson
from random import  choice


class JsonResponse(HttpResponse):
    """
        JSON response
    """
    def __init__(self, content, mimetype='application/json', status=None, content_type=None):
        super(JsonResponse, self).__init__(
            content=simplejson.dumps(content),
            mimetype=mimetype,
            status=status,
            content_type=content_type,
        )


class QuestionType(object):
    id = 0
    text = ""
    noOfOptions = 0
    level = 2
    
    @classmethod
    def to_serializable(self):
        return {
            'type' : self.id,
            'text' : self.text,
        }

class FindOnMapQuestionType(QuestionType):
    id = 0
    text = u"Vyber na mapě stát"
    
class PickNameOfQuestionType(QuestionType):
    id = 1
    text = u"Jak se jmenuje stát zvýrazněný na mapě?"
    noOfOptions = 6
    
class PickNameOf4OptionsQuestionType(PickNameOfQuestionType):
    id = 2
    noOfOptions = 4
    level = 1

class FindOnMapOf4OptionsQuestionType(QuestionType):
    id = 3
    noOfOptions = 4
    text = u"Ze čtyř zvýrazněných států na mapě vyber"
    level = 1
    
class PickNameOf2OptionsQuestionType(PickNameOfQuestionType):
    id = 4
    noOfOptions = 2
    level = 0

class FindOnMapOf2OptionsQuestionType(QuestionType):
    id = 5
    noOfOptions = 2
    text = u"Ze dvou zvýrazněných států na mapě vyber"
    level = 0

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]

class Question():
    options = []
    def __init__(self, place, qtype=QuestionType()):
        self.place = place
        self.qtype = qtype
        if (qtype.noOfOptions != 0) :
            self.options = self.get_options(self.qtype.noOfOptions)
        
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
        if self.qtype.level == 0 :
            ps += self.get_easy_options(n -1)
        elif self.qtype.level == 2 :
            ps += self.get_hard_options(n -1)
        remains = n - len(ps) 
        if (remains > 0):
            ps += self.get_random_options(remains, ps)
        options = [p.to_serializable() for p in ps]
        options.sort(key=lambda tup: tup["name"])
        return options
    
    def get_easy_options(self, n):
        return Place.objects.filter(difficulty__lt=self.place.difficulty).order_by('?')[:n]
        
    def get_random_options(self, n, excluded):
        return Place.objects.exclude(id__in = [p.id for p in excluded]).order_by('?')[:n]
        
    def get_hard_options(self, n):
        return ConfusedPlaces.objects.get_similar_to(self.place)[:n]


class QuestionService():
    def __init__(self, user):
        self.user = user
        self.easyQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 0]
        self.mediumQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 1]
        self.hardQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 2]

    def get_questions(self, n):
        places = self.get_uncertain_places(n)

        remains = n - len(places) 
        if (remains > 0):
            places += self.get_new_places(remains)

        remains = n - len(places) 
        if (remains > 0):
            places += self.get_weak_places(remains)

        remains = n - len(places) 
        if (remains > 0):
            places += self.get_random_places(remains)

        questions = self.places_to_questions(places)
        return questions

    def places_to_questions(self, places):
        successRate = self.success_rate()
        if (successRate > 0.66):
            qTypeLevel = self.hardQuestionTypes
        elif (successRate < 0.33):
            qTypeLevel = self.easyQuestionTypes
        else:
            qTypeLevel = self.mediumQuestionTypes
        questions = []
        for place in places:
            qtype = choice(qTypeLevel)
            question = Question(place, qtype)
            questions.append(question.to_serializable())
        return questions

    def success_rate(self):
        PRIORITY_RATIO = 1.2
        lastAnswers = Answer.objects.filter(
                user=self.user,
            ).order_by("-askedDate")[:10]
        successRate = 0
        for i in range(len(lastAnswers)):
            a = lastAnswers[i]
            thisSuccess = 1 if a.place == a.answer else 0
            successRate = (successRate * i + thisSuccess * PRIORITY_RATIO) / (i + PRIORITY_RATIO)
        return successRate

    def get_uncertain_places(self, n):
        return [up.place for up in self.get_ready_users_places() if up.certainty() < 1 ][:n]

    def get_new_places(self, n):
        return Place.objects.exclude(
                id__in=[up.place_id for up in UsersPlace.objects.filter(user=self.user)]
            ).order_by('difficulty')[:n]

    def get_weak_places(self, n):
        return [up.place for up in self.get_ready_users_places(10) if up.skill() < 0.8 ][:n]

    def get_random_places(self, n):
        return [up.place for up in self.get_ready_users_places(60) if up.skill() < 1][:n]

    def get_ready_users_places(self, correctAnswerDelayMinutes=2):
        minuteAgo = datetime.now() - timedelta(seconds=60)
        correctMinutesAgo = datetime.now() - timedelta(seconds=correctAnswerDelayMinutes*60)
        return UsersPlace.objects.filter(
                user=self.user,
                lastAsked__lt=correctMinutesAgo,
            ).exclude(
                place_id__in=[a.place_id for a in Answer.objects.filter(
                    user=self.user,
                    askedDate__gt=minuteAgo
                )]
            ).order_by('?')

    def answer(self, a):
        student = Student.objects.fromUser(self.user)
        place = Place.objects.get(code=a["code"])
        answerPlace = Place.objects.get(code=a["answer"]) if "answer" in a and a["answer"] != "" else None
        
        answer = Answer(
            user=student,
            place=place,
            answer=answerPlace,
            type=a["type"],
            msResposeTime=a["msResponseTime"] 
        )
        answer.save()

        student.points += 1;
        student.save();

        UsersPlace.objects.addAnswer(answer)
