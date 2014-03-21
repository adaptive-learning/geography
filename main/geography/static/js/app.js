(function() {
  /* global hash  */
  'use strict';
  // Declare app level module which depends on filters, and services
  angular.module('blindMaps', [
    'blindMaps.filters',
    'blindMaps.services',
    'blindMaps.directives',
    'blindMaps.controllers',
    'blindMaps.map',
    'ngCookies',
    'ngRoute',
    'ngAnimate',
    'angulartics',
    'angulartics.google.analytics'
  ])

  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl : './tpl/welcome_page.html'
    }).when('/how-it-works', {
      templateUrl : './tpl/how_it_works.html'
    }).when('/about', {
      templateUrl : './tpl/about.html'
    }).when('/view/', {
      redirectTo : '/view/world/'
    }).when('/view/:part/:user?', {
      controller : 'AppView',
      templateUrl : './'+hash('static/tpl/view_tpl.html')
    }).when('/practice/', {
      redirectTo : '/practice/world/'
    }).when('/refreshpractice/:part/:place_type?', {
      redirectTo : '/practice/:part/:place_type'
    }).when('/practice/:part/:place_type?', {
      controller : 'AppPractice',
      templateUrl : './'+hash('static/tpl/practice_tpl.html')
    }).otherwise({
      //redirectTo : '/'
    });
  })

  .run(function($cookies, $http, $rootScope, $, $analytics, places) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    $analytics.settings.pageTracking.autoTrackFirstPage = false;
    
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
  });
}());
