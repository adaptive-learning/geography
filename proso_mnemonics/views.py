# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from logging import getLogger
from proso_mnemonics.models import Mnemonic
from django.views.decorators.cache import cache_page


LOGGER = getLogger(__name__)


@cache_page(60 * 60)
def mnemonics(request):
    lang = Mnemonic.LANGUAGES_REVERSE[request.LANGUAGE_CODE]
    mnemonics = Mnemonic.objects.filter(language=lang).select_related('place')

    response = {
        'mnemonics': [m.to_serializable() for m in mnemonics],
    }
    return JsonResponse(response)
