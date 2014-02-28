# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from math import exp
from geography.models import KnowledgeUpdater


class Command(BaseCommand):
    help = u'''Recompute derived data'''

    def handle(self, *args, **options):
        if len(args) > 0:
            raise CommandError('The command doesn\'t need any option.')
        self.load_derived_data()

    def load_derived_data(self):
        cursor = connection.cursor()
        # foreach answer update new datasets
        print 'computing knowledge data in memory'
        cursor.execute('SELECT * FROM geography_answer ORDER BY id')
        answer = self.fetchone(cursor)
        knowledge_retriever = KnowledgeUpdater.on_answer_save(answer, in_memory=True)
        while answer:
            knowledge_retriever = KnowledgeUpdater.on_answer_save(
                answer, knowledge_retriever=knowledge_retriever)
            answer = self.fetchone(cursor)
        # empty precomputed datasets
        cursor.execute('DELETE FROM geography_difficulty;')
        cursor.execute('DELETE FROM geography_priorskill;')
        cursor.execute('DELETE FROM geography_currentskill;')
        # save new precomputed datasets
        print 'flushing knowledge data to database'
        knowledge_retriever.flush()

    def predict(self, local_skill, guess):
        return guess + (1 - guess) * (1.0 / (1 + exp(-local_skill)))

    def fetchone(self, cursor):
        fetched = cursor.fetchone()
        if fetched:
            return dict(zip([col[0] for col in cursor.description], fetched))
        else:
            return None
