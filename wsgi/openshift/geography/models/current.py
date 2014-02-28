# -*- coding: utf-8 -*-
from prior import predict, guess


def pfa(answer, current_skill, knowledge_retriever):
    K_GOOD = 0.9
    K_BAD = 0.6
    g = guess(answer)
    prediction = predict(current_skill, g)
    result = answer['place_asked_id'] == answer['place_answered_id']
    if result:
        return current_skill + K_GOOD * (result - prediction)
    else:
        return current_skill + K_BAD * (result - prediction)
