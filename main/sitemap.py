from django.contrib.sitemaps import Sitemap
from geography.models import Place
from django.core.urlresolvers import reverse


class MapSitemap(Sitemap):
    def location(self, item):
        return '/#/view/' + item.code + '/'


class ContinentsSitemap(MapSitemap):
    priority = 0.5

    def items(self):
        return Place.objects.get_continents()


class StatesSitemap(MapSitemap):
    priority = 0.3

    def items(self):
        return Place.objects.get_states_with_map()


class FlatPages(Sitemap):
    locations = {
        'about': '/#/about',
        'how-it-works': '/#/how-it-works',
        'world': '/#/view/world/',
    }

    def priority(self, item):
        return 1 if item == "home" else 0.8

    def items(self):
        return ['home', 'about', 'how-it-works', 'world']

    def location(self, item):
        return self.locations[item] if item in self.locations else reverse(item)


sitemaps = {
    'flatpages': FlatPages,
    'continents': ContinentsSitemap,
    'states': StatesSitemap,
}
