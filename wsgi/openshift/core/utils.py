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

def get_question_type_by_id(id):
    question_types = all_subclasses(QuestionType)
    for QT in question_types:
        qt = QT()
        if qt.id == id:
            return qt
    return None

class QuestionType(object):
    id = 0
    text = ""
    no_of_options = 0
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
    no_of_options = 6
    
class PickNameOf4OptionsQuestionType(PickNameOfQuestionType):
    id = 2
    no_of_options = 4
    level = 1

class FindOnMapOf4OptionsQuestionType(QuestionType):
    id = 3
    no_of_options = 4
    text = u"Ze čtyř zvýrazněných států na mapě vyber"
    level = 1
    
class PickNameOf2OptionsQuestionType(PickNameOfQuestionType):
    id = 4
    no_of_options = 2
    level = 0

class FindOnMapOf2OptionsQuestionType(QuestionType):
    id = 5
    no_of_options = 2
    text = u"Ze dvou zvýrazněných států na mapě vyber"
    level = 0

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]

class Question():
    options = []
    def __init__(self, place, qtype, map):
        self.place = place
        self.qtype = qtype
        self.map = map
        if (qtype.no_of_options != 0) :
            self.options = self.get_options(self.qtype.no_of_options)
        
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
            pass#ps += self.get_easy_options(n -1)
        elif self.qtype.level == 2 :
            ps += self.get_hard_options(n -1)
        remains = n - len(ps) 
        if (remains > 0):
            ps += self.get_random_options(remains, ps)
        options = [p.to_serializable() for p in ps]
        options.sort(key=lambda tup: tup["name"])
        return options
    
    def get_options_base(self):
        return Place.objects.filter(id__in=self.map.related_places.all())
    
    def get_easy_options(self, n):
        return self.get_options_base().filter(difficulty__lt=self.place.difficulty).order_by('?')[:n]
        
    def get_random_options(self, n, excluded):
        return self.get_options_base().exclude(id__in = [p.id for p in excluded]).order_by('?')[:n]
        
    def get_hard_options(self, n):
        return ConfusedPlaces.objects.get_similar_to(self.place)[:n]

class QuestionChooser(object):
    easyQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 0]
    mediumQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 1]
    hardQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 2]
    def __init__(self, user, map):
        self.user = user
        self.map = map

    @classmethod
    def get_ready_users_places(self, correctAnswerDelayMinutes=2):
        minuteAgo = datetime.now() - timedelta(seconds=60)
        correctMinutesAgo = datetime.now() - timedelta(seconds=correctAnswerDelayMinutes*60)
        return UsersPlace.objects.filter(
                user=self.user,
                lastAsked__lt=correctMinutesAgo,
                place_id__in=self.map.related_places.all(),
            ).exclude(
                place_id__in=[a.place_id for a in Answer.objects.filter(
                    user=self.user,
                    askedDate__gt=minuteAgo
                )]
            ).order_by('?')
            
    @classmethod
    def get_question_level(self, place):
        up = UsersPlace.objects.fromStudentAndPlace(self.user,place)
        if up.askedCount < 2:
            successRate = up.similar_places_knowladge()
        else:
            successRate = up.skill() * up.certainty()
#         raise Exception(u"here {0} {1}".format(successRate, place.name))
        if (successRate > 0.8):
            qTypeLevel = self.hardQuestionTypes
        elif (successRate <= 0.5):
            qTypeLevel = self.easyQuestionTypes
        else:
            qTypeLevel = self.mediumQuestionTypes
        return qTypeLevel
            
    @classmethod
    def get_questions(self, n, user, map):
        self.user = user
        self.map = map
        places = self.get_places(n)
        questions = []
        for place in places:
            qTypeLevel = self.get_question_level(place)
            qtype = choice(qTypeLevel)
            question = Question(place, qtype, self.map)
            questions.append(question.to_serializable())
        return questions

    @classmethod
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

class UncertainPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_places(self, n):
        return [up.place for up in self.get_ready_users_places() if up.certainty() < 1 ][:n]

class WeakPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_places(self, n):
        return [up.place for up in self.get_ready_users_places(10) if up.skill() < 0.8 ][:n]

class NewPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_places(self, n):
        return Place.objects.filter(
                id__in=self.map.related_places.all()
            ).exclude(
                id__in=[up.place_id for up in UsersPlace.objects.filter(user=self.user)]
            ).order_by('difficulty')[:n]

class RandomPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_places(self, n):
        return [up.place for up in self.get_ready_users_places(60) if up.skill() < 1][:n]


class QuestionService():
    def __init__(self, user, map):
        self.user = Student.objects.fromUser(user)
        self.map = map
        self.easyQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 0]
        self.mediumQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 1]
        self.hardQuestionTypes = [qType for qType in all_subclasses(QuestionType) if qType.level == 2]

    def get_questions(self, n):
        question_choosers = all_subclasses(QuestionChooser)
        questions = []
        for QC in question_choosers:
            qc = QC(self.user, self.map)
            remains = n - len(questions) 
            questions += qc.get_questions(remains, self.user, self.map)
        return questions

    def answer(self, a):
        place = Place.objects.get(code=a["code"])
        answerPlace = Place.objects.get(code=a["answer"]) if "answer" in a and a["answer"] != "" else None
        
        answer = Answer(
            user=self.user,
            place=place,
            answer=answerPlace,
            type=a["type"],
            msResposeTime=a["msResponseTime"] 
        )
        answer.save()
        
        if place == answerPlace:
            self.user.points += 1;
            self.user.save();

        UsersPlace.objects.addAnswer(answer)

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"