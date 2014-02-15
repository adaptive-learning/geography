
# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):
    TRANSLATE = {
        u'Andalucía': u'Andalusie',
        u'Aragón': u'Aragonie',
        u'Cantabria': u'Kantábrie',
        u'Castilla y León': u'Kastilie a León',
        u'Castilla-La Mancha': u'Kastilie-La Mancha',
        u'Cataluña': u'Katalánsko',
        u'Ceuta y Melilla': u'Ceuta a Melilla',
        u'Comunidad de Madrid': u'Madrid',
        u'Comunidad Foral de Navarra': u'Navarra',
        u'Comunidad Valenciana': u'Valencie',
        u'Extremadura': u'Extremadura',
        u'Galicia': u'Galicie',
        u'Islas Baleares': u'Baleárské ostrovy',
        u'Islas Canarias': u'Kanárské ostrovy',
        u'La Rioja': u'La Rioja',
        u'País Vasco': u'Baskicko',
        u'Principado de Asturias': u'Asturie',
        u'Región de Murcia': u'Murcie',
        u'Abruzzo': u'Abruzzo',
        u'Apulia': u'Apulie',
        u'Basilicata': u'Basilicata',
        u'Calabria': u'Kalábrie',
        u'Campania': u'Kampánie',
        u'Emilia-Romagna': u'Emilia-Romagna',
        u'Friuli-Venezia Giulia': u'Furlandsko-Julské Benátsko',
        u'Lazio': u'Lazio',
        u'Liguria': u'Ligurie',
        u'Lombardia': u'Lombardie',
        u'Marche': u'Marche',
        u'Molise': u'Molise',
        u'Piemonte': u'Piemont',
        u'Sardegna': u'Sardinie',
        u'Sicily': u'Sicilie',
        u'Toscana': u'Toskánsko',
        u'Trentino-Alto Adige': u'Tridentsko-Jižní Tyrolsko',
        u'Umbria': u'Umbrie',
        u'Valle d\'Aosta': u'Údolí Aosty',
        u'Veneto': u'Benátsko',
        u'Jervis Bay Territory': u'Teritorium Jervisova zátoka',
        u'Northern Territory': u'Severní Teritorium',
        u'Western Australia': u'Západní Austrálie',
        u'Australian Capital Territory': u'Teritorium hlavního města',
        u'New South Wales': u'Nový Jižní Wales',
        u'South Australia': u'Jižní Austrálie',
        u'Victoria': u'Victoria',
        u'Queensland': u'Queensland',
        u'Norfolk Island': u'Norfolk',
        u'Tasmania': u'Tasmánie',
        u'Manitoba': u'Manitoba',
        u'Saskatchewan': u'Saskatchewan',
        u'Alberta': u'Alberta',
        u'British Columbia': u'Britská Kolumbie',
        u'Nunavut': u'Nunavut',
        u'Northwest Territories': u'Severozápadní teritoria',
        u'Yukon': u'Yukon',
        u'Ontario': u'Ontario',
        u'Québec': u'Québec',
        u'New Brunswick': u'Nový Brunšvik',
        u'Nova Scotia': u'Nové Skotsko',
        u'Newfoundland and Labrador': u'Newfoundland a Labrador',
        u'Prince Edward Island': u'Ostrov prince',
        u'Alsace': u'Alsasko',
        u'Aquitaine': u'Akvitánie',
        u'Auvergne': u'Auvergne',
        u'Basse-Normandie': u'Dolní Normandie',
        u'Bourgogne': u'Burgundsko',
        u'Bretagne': u'Bretaň',
        u'Centre': u'Centre',
        u'Champagne-Ardenne': u'Champagne-Ardenne',
        u'Corse': u'Korsika',
        u'Franche-Comté': u'Franche-Comté',
        u'Haute-Normandie': u'Horní Normandie',
        u'Île-de-France': u'Île-de-France',
        u'Languedoc-Roussillon': u'Languedoc-Roussillon',
        u'Limousin': u'Limousin',
        u'Lorraine': u'Lotrinsko',
        u'Midi-Pyrénées': u'Midi-Pyrénées',
        u'Nord-Pas-de-Calais': u'Nord-Pas-de-Calais',
        u'Pays de la Loire': u'Pays de la Loire',
        u'Picardie': u'Pikardie',
        u'Poitou-Charentes': u'Poitou-Charentes',
        u'Provence-Alpes-Côte-d\'Azur': u'Provensálsko-Alpy-Azurové pobřeží',
        u'Rhône-Alpes': u'Rhône-Alpes',
    }

    dependencies = [("migrations", "0009_load_maps_it_fr_es_ca_au")]

    def forwards(self, orm):
        cursor = connection.cursor()
        for code, name in Migration.TRANSLATE.iteritems():
            cursor.execute(
                '''
                UPDATE
                    geography_place
                SET
                    name = %s
                WHERE code = %s OR name = %s
                ''',
                [name, code, code]
            )

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
