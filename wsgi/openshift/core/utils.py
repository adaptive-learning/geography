# -*- coding: utf-8 -*-
from core.models import Answer, Place, Student, UsersPlace
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
    def toSerializable(self):
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
            self.options = self.getOptions()
        
    def toSerializable(self):
        ret = self.qtype.toSerializable()
        ret.update(self.place.toSerializable())
        ret["place"] = ret["name"]
        ret.pop("name")
        if (self.options != []):
            ret["options"] = self.options
        return ret

    def getOptions(self):
        options = []
        ps = Place.objects.exclude(id=self.place.id).order_by('?')[:self.qtype.noOfOptions - 1]
        for p in ps:
            options.append(p.toSerializable())
        options.append(self.place.toSerializable())
        options.sort(key=lambda tup: tup["name"])
        return options


class QuestionService():
    def __init__(self, user):
        self.user = user
        self.easyQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 0]
        self.mediumQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 1]
        self.hardQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 2]

    def getQuestions(self, n):
        places = self.getWeakPlaces(n)

        remains = n - len(places) 
        if (remains > 0):
            places += self.getNewPlaces(remains)

        remains = n - len(places) 
        if (remains > 0):
            places += self.getRandomPlaces(remains)

        questions = self.placesToQuestions(places)
        return questions

    def placesToQuestions(self, places):
        successRate = self.successRate()
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
            questions.append(question.toSerializable())
        return questions

    def successRate(self):
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
                

    def getNewPlaces(self, n):
        return Place.objects.exclude(
                id__in=[up.place_id for up in UsersPlace.objects.filter(user=self.user)]
            ).order_by('difficulty')[:n]

    def getWeakPlaces(self, n):
        return [up.place for up in self.getReadyUsersPlaces() if up.certainty() < 1 ][:n]

    def getRandomPlaces(self, n):
        return [up.place for up in self.getReadyUsersPlaces()[:n]]

    def getReadyUsersPlaces(self):
        minuteAgo = datetime.now() - timedelta(seconds=60)
        twoMinutesAgo = datetime.now() - timedelta(seconds=120)
        return UsersPlace.objects.filter(
                user=self.user,
                lastAsked__lt=twoMinutesAgo,
            ).exclude(
                place_id__in=[a.place_id for a in Answer.objects.filter(
                    user=self.user,
                    askedDate__gt=minuteAgo
                )]
            ).order_by('?')

    def answer(self, a):
        student = Student.fromUser(self.user)
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

        UsersPlace.addAnswer(answer)
