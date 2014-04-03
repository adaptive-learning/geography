# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0018_add_states_maps_cities")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            CREATE TABLE `geography_ab_group` (
                `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `active` bool NOT NULL,
                `name` varchar(100) NOT NULL,
                `max_answers` integer NOT NULL,
                `min_answers` integer NOT NULL
            );

            CREATE TABLE `geography_ab_value` (
                `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `group_id` integer NOT NULL,
                `value` varchar(100) NOT NULL,
                `probability` integer NOT NULL,
                `is_default` bool NOT NULL,
                UNIQUE(`group_id`, `value`)
            );
            ALTER TABLE `geography_ab_value`
                ADD CONSTRAINT `group_id_refs_id_cf4eca0e`
                FOREIGN KEY (`group_id`) REFERENCES `geography_ab_group` (`id`);

            CREATE TABLE `geography_ab_uservalues` (
                `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `user_id` integer NOT NULL
            );
            ALTER TABLE `geography_ab_uservalues`
                ADD CONSTRAINT `user_id_refs_id_76b303a2`
                FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

            CREATE TABLE `geography_ab_uservalues_values` (
                `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `uservalues_id` integer NOT NULL,
                `value_id` integer NOT NULL,
                UNIQUE (`uservalues_id`, `value_id`)
            );
            ALTER TABLE `geography_ab_uservalues_values`
                ADD CONSTRAINT `value_id_refs_id_889879be`
                FOREIGN KEY (`value_id`) REFERENCES `geography_ab_value` (`id`);
            ALTER TABLE `geography_ab_uservalues_values`
                ADD CONSTRAINT `uservalues_id_refs_id_5ded572f`
                FOREIGN KEY (`uservalues_id`) REFERENCES `geography_ab_uservalues` (`id`);
            ''')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            DROP TABLE IF EXISTS `geography_ab_uservalues_values`;
            DROP TABLE IF EXISTS `geography_ab_uservalues`;
            DROP TABLE IF EXISTS `geography_ab_value`;
            DROP TABLE IF EXISTS `geography_ab_group`;
            ''')

    complete_apps = ['geography']
