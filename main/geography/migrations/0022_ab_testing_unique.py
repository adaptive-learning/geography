# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    dependencies = [("migrations", "0021_answer_ip_address_db")]

    def forwards(self, orm):
        # Adding unique constraint on 'Value', fields ['value']
        db.create_unique('geography_ab_value', ['value'])

        # Adding unique constraint on 'Group', fields ['name']
        db.create_unique('geography_ab_group', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Group', fields ['name']
        db.delete_unique('geography_ab_group', ['name'])

        # Removing unique constraint on 'Value', fields ['value']
        db.delete_unique('geography_ab_value', ['value'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'geography.answer': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Answer'},
            'ab_values': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['geography.Value']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inserted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'number_of_options': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['geography.Place']", 'symmetrical': 'False'}),
            'place_answered': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'place_answered_id'", 'null': 'True', 'blank': 'True', 'to': "orm['geography.Place']"}),
            'place_asked': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'place_asked_id'", 'to': "orm['geography.Place']"}),
            'place_map': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'place_map_id'", 'null': 'True', 'to': "orm['geography.Place']"}),
            'response_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'geography.averageplace': {
            'Meta': {'object_name': 'AveragePlace', 'managed': 'False'},
            'dummy_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geography.Place']", 'on_delete': 'models.DO_NOTHING'}),
            'skill': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'geography.currentskill': {
            'Meta': {'unique_together': "(('user', 'place'),)", 'object_name': 'CurrentSkill'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geography.Place']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'geography.difficulty': {
            'Meta': {'object_name': 'Difficulty'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geography.Place']", 'unique': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'geography.group': {
            'Meta': {'object_name': 'Group', 'db_table': "'geography_ab_group'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_answers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'min_answers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'geography.place': {
            'Meta': {'ordering': "['type', 'name']", 'object_name': 'Place'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'geography.placerelation': {
            'Meta': {'unique_together': "(('type', 'place'),)", 'object_name': 'PlaceRelation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'place_id'", 'to': "orm['geography.Place']"}),
            'related_places': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['geography.Place']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'geography.priorskill': {
            'Meta': {'object_name': 'PriorSkill'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'geography.userplace': {
            'Meta': {'object_name': 'UserPlace', 'managed': 'False'},
            'dummy_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geography.Place']", 'on_delete': 'models.DO_NOTHING'}),
            'skill': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'on_delete': 'models.DO_NOTHING'})
        },
        'geography.uservalues': {
            'Meta': {'object_name': 'UserValues', 'db_table': "'geography_ab_uservalues'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'values': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['geography.Value']", 'symmetrical': 'False'})
        },
        'geography.value': {
            'Meta': {'object_name': 'Value', 'db_table': "'geography_ab_value'"},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geography.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'probability': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['geography']
