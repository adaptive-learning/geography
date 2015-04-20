from models import Mnemonic
from django.contrib import admin


class MnemonicAdmin(admin.ModelAdmin):
    list_display = ('place', 'text', 'language')


admin.site.register(Mnemonic, MnemonicAdmin)
