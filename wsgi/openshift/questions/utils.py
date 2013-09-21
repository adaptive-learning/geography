# -*- coding: utf-8 -*-
from core.models import Place
from datetime import datetime, timedelta
from questions.models import Answer, UsersPlace, ConfusedPlaces, \
    QuestionTypeFactory, all_subclasses, QuestionType



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
        ps += self.get_confused_options(n -1)
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
        
    def get_confused_options(self, n):
        return ConfusedPlaces.objects.get_similar_to(self.place, self.map)[:n]
    
class QuestionChooser(object):
    def __init__(self, user, map, pre_questions):
        # TODO: figure out how to make these 3 params work without setting them again in get_questions method
        self.user = user
        self.map = map
        self.pre_questions = pre_questions

    @classmethod
    def get_ready_users_places(self, correctAnswerDelayMinutes=2):
        delay_miuntes = 1 if correctAnswerDelayMinutes > 1 else correctAnswerDelayMinutes
        minuteAgo = datetime.now() - timedelta(seconds=60 * delay_miuntes)
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
            ).exclude(
                place__code__in=[q['code'] for q in self.pre_questions]
            ).select_related('place').order_by('?')
            
    @classmethod
    def get_question_type(self, usersplace):
        if usersplace.askedCount < 2:
            successRate = self.success_rate
        else:
            successRate = usersplace.skill
        if (successRate > 0.8):
            qTypeLevel = QuestionType.HARD_QUESITON_LEVEL
        elif (successRate <= 0.5):
            qTypeLevel = QuestionType.EASY_QUESITON_LEVEL
        else:
            qTypeLevel = QuestionType.MEDIUM_QUESITON_LEVEL
        qtype = QuestionTypeFactory.get_instance_by_level(qTypeLevel)
        return qtype
            
    @classmethod
    def get_questions(self, n, user, map, pre_questions):
        self.user = user
        self.map = map
        self.pre_questions = pre_questions
        self.success_rate = self.get_success_rate()
        usersplaces = self.get_usersplaces(n)
        questions = []
        for up in usersplaces:
            qtype = self.get_question_type(up)
            question = Question(up.place, qtype, self.map)
            questions.append(question.to_serializable())
        return questions

    @classmethod
    def get_success_rate(self):
        PRIORITY_RATIO = 1.2
        lastAnswers = Answer.objects.get_last_10_answers(self.user)
        correct_answers = [a for a in lastAnswers if a.place_id == a.answer_id]
        last_answers_len = len(lastAnswers) if len(lastAnswers) > 0 else 1
        successRate = 1.0 * len(correct_answers) / last_answers_len
        return successRate

class UncertainPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_usersplaces(self, n):
        return [up for up in self.get_ready_users_places() if up.get_certainty() < 1 ][:n]

class WeakPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_usersplaces(self, n):
        return [up for up in self.get_ready_users_places(5).filter(skill__lt=0.8)[:n]]

class NewPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_usersplaces(self, n):
        places = Place.objects.filter(
                id__in=self.map.related_places.all()
            ).exclude(
                id__in=[up.place_id for up in UsersPlace.objects.filter(user=self.user)]
            ).order_by('difficulty')[:n]
        return [UsersPlace(place=p,user=self.user) for p in places]

class RandomPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_usersplaces(self, n):
        return [up for up in self.get_ready_users_places(30) if up.skill < 1][:n]

class ShortRepeatIntervalPlacesQuestionChooser(QuestionChooser):
    @classmethod
    def get_usersplaces(self, n):
        return [up for up in self.get_ready_users_places(0.5) if up.skill < 1 or up.get_certainty() < 1][:n]


class QuestionService():
    def __init__(self, user, map):
        self.user = user
        self.map = map

    def get_questions(self, n):
        question_choosers = all_subclasses(QuestionChooser)
        questions = []
        for QC in question_choosers:
            qc = QC(self.user, self.map, questions)
            remains = n - len(questions) 
            questions += qc.get_questions(remains, self.user, self.map, questions)
        return questions

    def answer(self, a):
        place = Place.objects.get(code=a["code"])
        answerPlace = Place.objects.get(code=a["answer"]) if "answer" in a and a["answer"] != "" else None
        
        answer = Answer(
            user=self.user,
            place=place,
            answer=answerPlace,
            type=a["type"],
            msResposeTime=a["msResponseTime"],
        )
        answer.save()
        if "options" in a:
            answer.options = Place.objects.filter(
                    code__in=[o["code"] for o in a["options"]],
                )
        
        if place == answerPlace:
            self.user.points += 1;
            self.user.save();

        UsersPlace.objects.addAnswer(answer)
        
