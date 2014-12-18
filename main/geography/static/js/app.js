(function() {
  'use strict';
  /* global gettext */
  // Declare app level module which depends on filters, and services
  angular.module('blindMaps', [
    'blindMaps.filters',
    'blindMaps.services',
    'blindMaps.directives',
    'blindMaps.controllers',
    'blindMaps.map',
    'ngRoute',
    'ngAnimate',
    'angulartics',
    'angulartics.google.analytics',
    'ui.bootstrap',
    'googleExperiments',
    'xeditable',
    'proso.feedback',
    'proso.goals',
  ])

  .value('gettext', gettext)

  .config(['$routeProvider', '$locationProvider', 'googleExperimentsProvider',
      function($routeProvider, $locationProvider, googleExperimentsProvider) {
    $routeProvider.when('/', {
      templateUrl : 'static/tpl/homepage.html'
    }).when('/login/:somepath/', {
      controller : 'ReloadController',
      templateUrl : 'loading.html'
    }).when('/cs/:somepath?', {
      controller : 'ReloadController',
      templateUrl : 'loading.html'
    }).when('/en/:somepath?', {
      controller : 'ReloadController',
      templateUrl : 'loading.html'
    }).when('/es/:somepath?', {
      controller : 'ReloadController',
      templateUrl : 'loading.html'
    }).when('/cs/:somepath/:more?/:path?', {
      controller : 'ReloadController',
      templateUrl : 'loading.html'
    }).when('/en/:somepath/:more?/:path?', {
      controller : 'ReloadController',
      templateUrl : 'loading.html'
    }).when('/es/:somepath/:more?/:path?', {
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

    $locationProvider.html5Mode(true);

    googleExperimentsProvider.configure({
      experimentId: 'Z701yBLfTbakJh3W6vGdpg'
    });
  }])

  .run(['$rootScope', '$', '$analytics', 'places', 'editableOptions',
      function($rootScope, $, $analytics, places, editableOptions) {
    $analytics.settings.pageTracking.autoTrackFirstPage = false;

    editableOptions.theme = 'bs3';
    
    $rootScope.$on("$routeChangeStart", function(event, next, current) {
      if (current && current.originalPath !== "" && $(window).width() < 770) {
        $("#nav-main").collapse();
        $("#nav-main").collapse('hide');
      }
    });

    $('.dropdown-menu a[href^="#/view/"]').each( function(i, link){
      var code = $(link).attr('href').replace('#/view/', '').replace('/', '');
      var name = $(link).text();
      places.setName(code, name);
    });
  }]);
}());
