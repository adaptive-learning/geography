# -*- coding: utf-8 -*-
from math import exp


def predict(skill, guess=0):
    return guess + (1 - guess) * (1.0 / (1 + exp(-skill)))


def guess(answer):
    return 1.0 / answer['number_of_options'] if answer['number_of_options'] != 0 else 0


def elo(answer, prior_skill, difficulty, knowledge_retriever):
    ALPHA = 1.0
    DYNAMIC_ALPHA = 0.05
    alpha_fun = lambda n: ALPHA / (1 + DYNAMIC_ALPHA * n)
    difficulty_alpha = alpha_fun(knowledge_retriever.number_of_first_answers_for_place())
    prior_skill_alpha = alpha_fun(knowledge_retriever.number_of_first_answers_for_user())
    g = guess(answer)
    prediction = predict(prior_skill, g)
    result = answer['place_asked_id'] == answer['place_answered_id']
    return (
        prior_skill + prior_skill_alpha * (result - prediction),
        difficulty - difficulty_alpha * (result - prediction))
