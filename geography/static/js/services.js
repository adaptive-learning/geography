
/* Services */
angular.module('proso.geography.services', ['ngCookies', 'gettext'])

  .factory('places', ['$http', 'gettextCatalog', function($http, gettextCatalog) {
    'use strict';
    var cache = {};
    var mapCache = {};
    var categoriesCache = {};
    var names = {
        'us' : gettextCatalog.getString('USA'),
        'world' : gettextCatalog.getString('Svět')
      };
    var categories = [
    ];
    var placeTypeNames = {};

    function addOneToNames(code, name) {
      if (!names[code]) {
        names[code] = name;
      }
    }

    function addToNames(code, placesTypes) {
      angular.forEach(placesTypes, function(type) {
        angular.forEach(type.places, function(place) {
          addOneToNames(place.code, place.name);
        });
      });
    }

    var that = {
      get : function(part, user, fn) {
        var url = '/usersplaces/' + part + '/' + user;
        var promise = $http.get(url, {cache: user == 'average'}).success(function(data) {
          var placesTypes = data.placesTypes;
          cache[url] = placesTypes;
          fn(placesTypes);
        });
        return promise;
      },
      setName : function(code, name) {
        names[code] = names[code] || name;
      },
      getName : function(code) {
        return names[code];
      },
      practicing : function (part) {
        // To fetch names of all places on map and be able to show name of wrongly answered place
        var process = function(placesTypes){
          addToNames(part, placesTypes);
        };
        var url = '/usersplaces/' + part + '/';
        if (cache[url]) {
          process(cache[url]);
        } else {
          that.get(part, '', process);
        }
      },
      getOverview : function () {
        return $http.get('/placesoverview/', {cache: true});
      },
      getMapLayers : function(map) {
        return mapCache[map].placesTypes.map(function(l){
          return l.slug;
        });
      },
      getMapLayerCount : function(map, layer) {
        if (!mapCache[map]) {
          return 0;
        }
        return mapCache[map].placesTypes.filter(function(l){
          return l.slug == layer;
        }).map(function(l){
          return l.count;
        })[0];
      },
      setPlaceTypeNames : function (obj) {
        placeTypeNames = obj;
      },
      getPlaceTypeName : function (slug) {
        return placeTypeNames[slug];
      },
    };
    /*
    that.getOverview().success(function(data){
      angular.forEach(data, function(category){
        angular.forEach(category.maps, function(map){
          mapCache[map.slug] = map;
        });
      });
    });
    */
    return that;
  }])

  .factory('mapTitle', ['places', function(places) {
    'use strict';
    return function(part, user) {
      var name = places.getName(part);
      if (!name) {
        return;
      } else if (user === '' || user == 'average') {
        return name;
      } else {
        return name + ' - ' + user;
      }
    };
  }])

  .factory('events', function() {
    'use strict';
    var handlers = {};
    return {
      on : function(eventName, handler) {
        handlers[eventName] = handlers[eventName] || [];
        handlers[eventName].push(handler);
      },
      emit : function(eventName, args) {
        handlers[eventName] = handlers[eventName] || [];
        handlers[eventName].map(function(handler) {
          handler(args);
        });
      }
    };
  })

  .factory('pageTitle',['places', 'gettextCatalog', 'placeTypeService',
      function(places, gettextCatalog, placeTypeService) {
    'use strict';

    var titles = {
      'static/tpl/about.html' : gettextCatalog.getString('O projektu') + ' - ',
      'static/tpl/overview_tpl.html' : gettextCatalog.getString('Přehled map') + ' - ',
    };
    return function (route) {
      var title;
      if (route.controller == "AppView" || route.controller == "AppPractice") {
        title = places.getName(route.params.part) + ' - ';
        var typeName = placeTypeService.getBySlug(route.params.place_type);
        if (typeName) {
          title += typeName + ' - ';
        }
      } else if (route.controller == "AppUser") {
        title = route.params.user + ' - ';
      } else {
        title = titles[route.templateUrl] || '';
      }
      return title;
    };
  }])

  .factory('params', ["$routeParams", "$location",
      function ($routeParams, $location) {
    'use strict';
    var keys = ['limit'];
    var params = {};
    var that =  {
      get: function (key) {
        if (params[key] && ! $routeParams[key]) {
          $location.search(key, params[key]);
        }
        if ($routeParams[key]) {
          params[key] = $routeParams[key];
        }
        return params[key];
      },
      all : function() {
        for (var i = 0; i < keys.length; i++) {
          that.get(keys[i]);
        }
        return params;
      },
      queryString : function() {
        that.all();
        var string = keys.map(function(key) {
          return that.get(key) ? '&' + key + '=' + that.get(key) : '';
        }).join('');
        return string;
      }
    };
    return that;
  }])

  .factory('categoryService', ["$http", "$q", function ($http, $q) {
    'use strict';
    var categories = [];
    var categoriesByIdentifier = {};
    var httpPromise;
    var deferredCategory = $q.defer();
    function init(){
      var filter = {
        all : 'True',
        db_orderby : 'name',
      };
      httpPromise = $http.get('/flashcards/categorys', {params: filter}).success(function(data) {
        categories = data.data;
        var categoriesByType = {};
        for (var i = 0; i < data.data.length; i++) {
          categoriesByIdentifier[data.data[i].identifier] = data.data[i];
          if (!categoriesByType[data.data[i].type]) {
            categoriesByType[data.data[i].type] = [];
          }
          categoriesByType[data.data[i].type].push(data.data[i]);
        }
        var allCategories = [];
        for (i in categoriesByType) {
          allCategories.push({
            maps: categoriesByType[i],
            identifier: i,
          });
        }
        deferredCategory.resolve(allCategories);
      }).error(function(error){
        console.error("Something went wrong while loading categories from backend.");
        deferredCategory.reject(error);
      });
    }
    init();
    var that = {
      getCategory: function (identifier) {
        return categoriesByIdentifier[identifier];
      },
      getAll: function () {
        return deferredCategory.promise;
      },
    };
    return that;
  }])

  .factory('flashcardService', ["$http", "$q", "gettextCatalog",
      function ($http, $q, gettextCatalog) {
    'use strict';
    var flashcardCache = {};
    var categoriesCache = {};

    function updateFlashcardCache(flashcards) {
      for (var i = 0; i < flashcards.length; i++) {
        var fc = flashcards[i];
        flashcardCache[fc.description] = fc;
      }
    }

    var that = {
      getFlashcards: function (filter) {
        var deferredFlashcards = $q.defer();
        for (var i in filter) {
          filter[i] = angular.toJson(filter[i]);
        }
        filter = angular.copy(filter);
        filter.all = 'True';
        $http.get('/flashcards/flashcards', {
          params: filter
        }).success(function(data) {
          deferredFlashcards.resolve(data.data);
          updateFlashcardCache(data.data);
        }).error(function(data) {
          deferredFlashcards.reject(data);
        });
        return deferredFlashcards.promise;
      },
      getFlashcardByDescription : function (description) {
        return flashcardCache[description];
      },
    };
    return that;
  }])


  .service('placeTypeService', ["gettextCatalog", function (gettextCatalog) {
    'use strict';
    var self = this;
    
    var placeTypeNames = {};
    var placeTypes = [];
    function hackForCorrectLanguage() {
      placeTypeNames = {
          'state' : gettextCatalog.getString('Státy'),
          'state-by-city' : gettextCatalog.getString('Státy skrze hlavní města'),
          'region' : gettextCatalog.getString('Regiony'),
          'province' : gettextCatalog.getString('Provincie'),
          'region_cz' : gettextCatalog.getString('Kraje'),
          'district' : gettextCatalog.getString('Okresy'),
          'region_it' : gettextCatalog.getString('Oblasti'),
          'autonomous_Comunity' : gettextCatalog.getString('Autonomní společenství'),
          'bundesland' : gettextCatalog.getString('Spolkové země'),
          'city' : gettextCatalog.getString('Města'),
          'city-by-state' : gettextCatalog.getString('Hlavní města skrze státy'),
          'river' : gettextCatalog.getString('Řeky'),
          'reservoir' : gettextCatalog.getString('Vodní nádrže'),
          'lake' : gettextCatalog.getString('Jezera'),
          'sea' : gettextCatalog.getString('Moře'),
          'mountains' : gettextCatalog.getString('Pohoří'),
          'surface' : gettextCatalog.getString('Povrch'),
          'island' : gettextCatalog.getString('Ostrovy'),
          'chko' : gettextCatalog.getString('CHKO a NP'),
      };
      placeTypes = [];
      for(var i in placeTypeNames) {
        if (i.indexOf('-by-') == -1) {
          placeTypes.push({
            name : placeTypeNames[i],
            identifier : i,
          });
        } else {
          placeTypes[placeTypes.length - 1].subtypes = 
            placeTypes[placeTypes.length - 1].subtypes || [];
          placeTypes[placeTypes.length - 1].subtypes.push({
            name : placeTypeNames[i],
            identifier : i,
          });
        }
      }
    }

    self.getTypes = function () {
      hackForCorrectLanguage();
      return placeTypes;
    };
    self.getBySlug = function (slug) {
      hackForCorrectLanguage();
      return placeTypeNames[slug];
    };
  }]);
