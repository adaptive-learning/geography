// Declare app level module which depends on filters, and services
angular.module('proso.geography', [
    'proso.geography.filters',
    'proso.geography.services',
    'proso.geography.directives',
    'proso.geography.controllers',
    'proso.geography.map',
    'proso.geography.templates',
    'ngRoute',
    'ngAnimate',
    'angulartics',
    'angulartics.google.analytics',
    'ui.bootstrap',
    'googleExperiments',
    'xeditable',
    'proso.apps',
    'angularDjangoCsrf',
    'gettext',
])

.constant('domain', window.domain || '')

.config(['$routeProvider', '$locationProvider', 'googleExperimentsProvider',
    function($routeProvider, $locationProvider, googleExperimentsProvider) {
        'use strict';
        $routeProvider.when('/', {
            templateUrl : 'static/tpl/homepage.html'
        }).when('/login/:somepath/', {
            controller : 'ReloadController',
            templateUrl : 'loading.html'
        }).when('/about', {
            templateUrl : 'static/tpl/about.html'
        }).when('/view/', {
            redirectTo : '/view/world/'
        }).when('/view/:part/:user?', {
            controller : 'AppView',
            templateUrl : 'static/tpl/view_tpl.html'
        }).when('/practice/', {
            redirectTo : '/practice/world/'
        }).when('/refreshpractice/:part/:place_type?', {
            redirectTo : '/practice/:part/:place_type'
        }).when('/practice/:part/:place_type?', {
            controller : 'AppPractice',
            templateUrl : 'static/tpl/practice_tpl.html'
        }).when('/overview/:user?', {
            controller : 'AppOverview',
            templateUrl : 'static/tpl/overview_tpl.html'
        }).when('/u/:user', {
            controller : 'AppUser',
            templateUrl : 'static/tpl/user_tpl.html'
        }).when('/goals/', {
            templateUrl : 'static/tpl/personal-goals-page_tpl.html'
        }).when('/mistakes/', {
            controller : 'AppConfused',
            templateUrl : 'static/tpl/confused_tpl.html'
        }).otherwise({
          //redirectTo : '/'
        });

        var languages = ['cs', 'en', 'es'];
        for (var i = 0; i < languages.length; i++) {
            $routeProvider.when('/' + languages[i] + '/:somepath?', {
                controller : 'ReloadController',
                templateUrl : 'loading.html'
            }).when('/' + languages[i] + '/:somepath/:more?/:path?', {
                controller : 'ReloadController',
                templateUrl : 'loading.html'
            });
        }

        $locationProvider.html5Mode(true);

        googleExperimentsProvider.configure({
            experimentId: 'Z701yBLfTbakJh3W6vGdpg'
        });
    }
])

.run(['$rootScope', '$', '$analytics', 'editableOptions', 'places', 'userService', 'configService',
    function($rootScope, $, $analytics, editableOptions, places, userService, configService) {
        'use strict';
        $analytics.settings.pageTracking.autoTrackFirstPage = false;

        editableOptions.theme = 'bs3';

        $rootScope.$on("$routeChangeStart", function(event, next, current) {
            if (current && current.originalPath !== "" && $(window).width() < 770) {
                $("#nav-main").collapse();
                $("#nav-main").collapse('hide');
            }
        });

        $rootScope.$on('questionSetFinished', function() {
          var checkPoints = configService.getConfig(
            'proso_feedback', 'evaluation_checkpoints', []);
          var answered_count = userService.user.profile.number_of_answers;
          var setLength = configService('proso_flashcards', 'practice.common.set_length', 10);

          angular.forEach(checkPoints, function(checkPoint) {
            if (checkPoint - setLength < answered_count && answered_count <= checkPoint) {
              $rootScope.$emit("openRatingModal");
            }
          });
        });
        
        $('.dropdown-menu a[href^="/view/"]').each( function(i, link){
            var code = $(link).attr('href').replace('/view/', '').replace('/', '');
            var name = $(link).text();
            places.setName(code, name);
        });

    }
]);
