# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from contextlib import closing
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0035_disable_testing")]

    def forwards(self, orm):
        with closing(connection.cursor()) as cursor:
            cursor.execute("SELECT id FROM geography_ab_group WHERE name = 'target_probability'")
            group_id, = cursor.fetchone()
            cursor.execute(
                """
                UPDATE geography_ab_value SET probability = 5 WHERE value = 'recommendation_target_prob_75';
                UPDATE geography_ab_value SET probability = 5 WHERE value = 'recommendation_target_prob_80';
                UPDATE geography_ab_value SET probability = 5 WHERE value = 'recommendation_target_prob_85';
                INSERT INTO geography_ab_value (group_id, value, probability, is_default) VALUES
                    (%s, 'recommendation_target_prob_60', 15, 0),
                    (%s, 'recommendation_target_prob_55', 15, 0),
                    (%s, 'recommendation_target_prob_50', 15, 0);
                """, [group_id, group_id, group_id])

    def backwards(self, orm):
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                UPDATE geography_ab_value SET probability = 20 WHERE value = 'recommendation_target_prob_75';
                UPDATE geography_ab_value SET probability = 20 WHERE value = 'recommendation_target_prob_80';
                UPDATE geography_ab_value SET probability = 20 WHERE value = 'recommendation_target_prob_85';
                DELETE FROM geography_ab_value  WHERE value = 'recommendation_target_prob_60';
                DELETE FROM geography_ab_value  WHERE value = 'recommendation_target_prob_55';
                DELETE FROM geography_ab_value  WHERE value = 'recommendation_target_prob_50';
                """)

    complete_apps = ['geography']
