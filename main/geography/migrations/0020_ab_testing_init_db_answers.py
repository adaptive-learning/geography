# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0019_ab_testing_init_db")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            CREATE TABLE `geography_answer_ab_values` (
                `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `answer_id` integer NOT NULL,
                `value_id` integer NOT NULL,
                UNIQUE (`answer_id`, `value_id`)
            );
            ALTER TABLE `geography_answer_ab_values`
                ADD CONSTRAINT `value_id_refs_id_eedcb883`
                FOREIGN KEY (`value_id`) REFERENCES `geography_ab_value` (`id`);
            ''')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            DROP TABLE IF EXISTS `geography_answer_ab_values`;
            ''')

    complete_apps = ['geography']
