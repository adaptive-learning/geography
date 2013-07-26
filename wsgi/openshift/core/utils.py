# -*- coding: utf-8 -*-
from core.models import Answer, Place, Student, UsersPlace
from datetime import datetime, timedelta
from django.db.models import F
from random import shuffle, choice




class QuestionType():
    id = 0
    text = ""
    noOfOptions = 0
    
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
    
class PickNameOfOptionsQuestionType(PickNameOfQuestionType):
    id = 2
    noOfOptions = 4


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
        shuffle(options)
        return options


class QuestionService():
    easyQuestionTypes = [PickNameOfOptionsQuestionType]
    hardQuestionTypes = [FindOnMapQuestionType, PickNameOfQuestionType]

    def __init__(self, user):
        self.user = user

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
        qTypeLevel = self.hardQuestionTypes if successRate > 0.5 else self.easyQuestionTypes
        questions = []
        for place in places:
            qtype = choice(qTypeLevel)
            question = Question(place, qtype)
            questions.append(question.toSerializable())
        return questions

    def successRate(self):
        lastAnswers = Answer.objects.filter(
                user=self.user,
            ).order_by("-askedDate")[:10]
        correctLastAnswers = [a for a in lastAnswers if a.place == a.answer]
        successRate = 1.0 * len(correctLastAnswers) / len(lastAnswers)  if len(lastAnswers) > 0 else 0
        return successRate
                

    def getNewPlaces(self, n):
        return Place.objects.exclude(
                id__in=[up.place_id for up in UsersPlace.objects.filter(user=self.user)]
            ).order_by('difficulty')[:n]

    def getWeakPlaces(self, n):
        return [up.place for up in self.getReadyUsersPlaces().filter(
                askedCount__gt=F('correctlyAnsweredCount') * 10 / 9.0,
            )[:n]]

    def getRandomPlaces(self, n):
        return [up.place for up in self.getReadyUsersPlaces()[:n]]

    def getReadyUsersPlaces(self):
        yesterday = datetime.now() - timedelta(days=1)
        minuteAgo = datetime.now() - timedelta(seconds=60)
        return UsersPlace.objects.filter(
                user=self.user,
                lastAsked__lt=yesterday,
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
