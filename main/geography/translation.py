from modeltranslation.translator import translator, TranslationOptions
from geography.models import Place


class PlaceTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Place, PlaceTranslationOptions)
