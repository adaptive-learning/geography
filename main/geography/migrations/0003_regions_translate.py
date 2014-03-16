# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):
    TRANSLATE = {
        u'Baden-Württemberg': u'Bádensko-Württembersko',
        u'Bayern': u'Bavorsko',
        u'Brandenburg': u'Braniborsko',
        u'Bremen': u'Brémy',
        u'Burgenland': u'Burgenland',
        u'Hamburg': u'Hamburk',
        u'Hessen': u'Hesensko',
        u'Kärnten': u'Korutany',
        u'Mecklenburg-Vorpommern': u'Meklenbursko-Přední Pomořansko',
        u'Niedersachsen': u'Dolní Sasko',
        u'Niederösterreich': u'Dolní Rakousko',
        u'Nordrhein-Westfalen': u'Severní Porýní-Vestfálsko',
        u'Oberösterreich': u'Horní Rakousko',
        u'Rheinland-Pfalz': u'Porýní-Falc',
        u'Saarland': u'Sársko',
        u'Sachsen': u'Sasko',
        u'Sachsen-Anhalt': u'Sasko-Anhaltsko',
        u'Salzburg': u'Salcbursko',
        u'Schleswig-Holstein': u'Šlesvicko-Holštýnsko',
        u'Steiermark': u'Štýrsko',
        u'Thüringen': u'Durynsko',
        u'Tirol': u'Tyrolsko',
        u'Vorarlberg': u'Vorarlbersko',
        u'Wien': u'Vídeň',
        u'cn-34': u'An-chuej',
        u'cn-11': u'Peking',
        u'cn-50': u'Čchung-čching',
        u'CN-': u'Fu-ťien',
        u'cn-62': u'Kan-su',
        u'cn-44': u'Kuang-tung',
        u'cn-45': u'Kuang-si',
        u'cn-52': u'Kuej-čou',
        u'cn-46': u'Chaj-nan',
        u'cn-13': u'Che-pej',
        u'cn-23': u'Chej-lung-ťiang',
        u'cn-41': u'Che-nan',
        u'cn-42': u'Chu-pej',
        u'cn-43': u'Chu-nan',
        u'cn-15': u'Vnitřní Mongolsko',
        u'cn-32': u'Ťiang-su',
        u'cn-36': u'Ťiang-si',
        u'cn-22': u'Ťi-lin',
        u'cn-21': u'Liao-ning',
        u'cn-64': u'Ning-sia',
        u'cn-63': u'Čching-chaj',
        u'cn-61': u'Šen-si',
        u'cn-37': u'Šan-tung',
        u'cn-31': u'Šanghaj',
        u'cn-14': u'Šan-si',
        u'cn-51': u'S\'-čchuan',
        u'cn-12': u'Tchien-ťin',
        u'cn-65': u'Sin-ťiang',
        u'cn-54': u'Tibetská autonomní oblast',
        u'cn-53': u'Jün-nan',
        u'cn-33': u'Če-ťiang',
        u'Andaman and Nicobar': u'Andamany a Nikobary',
        u'Andhra Pradesh': u'Ándhrapradéš',
        u'Arunachal Pradesh': u'Arunáčalpradéš',
        u'Assam': u'Ásám',
        u'Bihar': u'Bihár',
        u'Chandigarh': u'Čhattísgarh',
        u'Chhattisgarh': u'Čandígarh',
        u'Dadra and Nagar Haveli': u'Dádra a Nagar-havéli',
        u'Daman and Diu': u'Damán a Díjú',
        u'Delhi': u'Dillí',
        u'Goa': u'Goa',
        u'Gujarat': u'Gudžarát',
        u'Haryana': u'Harijána',
        u'Himachal Pradesh': u'Himáčalpradéš',
        u'Jammu and Kashmir': u'Džammú a Kašmír',
        u'Jharkhand': u'Džhárkhand',
        u'Karnataka': u'Karnátaka',
        u'Kerala': u'Kérala',
        u'Lakshadweep': u'Lakadivy / Lakšadvíp',
        u'Madhya Pradesh': u'Madhjapradéš',
        u'Maharashtra': u'Maháráštra',
        u'Manipur': u'Manípur',
        u'Meghalaya': u'Méghálaj',
        u'Mizoram': u'Mizóram',
        u'Nagaland': u'Nágáland',
        u'Orissa': u'Urísa',
        u'Prague': u'Praha',
        u'Puducherry': u'Puttuččéri',
        u'Punjab': u'Paňdžáb',
        u'Rajasthan': u'Rádžasthán',
        u'Sikkim': u'Sikkim',
        u'Tamil Nadu': u'Tamilnádu',
        u'Tripura': u'Tripura',
        u'Uttar Pradesh': u'Uttarákhand',
        u'Uttaranchal': u'Uttarpradéš',
        u'West Bengal': u'Západní Bengálsko'
    }

    dependencies = [("migrations", "0002_regions_load")]

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
