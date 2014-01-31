(function() {
  /* global console */
  /* global jQuery  */
  /* global hash  */
  /* global chroma  */
  /* global Kartograph */
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
    'angulartics',
    'angulartics.google.analytics'
  ])

  .value('$console', console)

  .value('chroma', chroma)

  .value('$', jQuery)

  .value('$K', Kartograph)

  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl : './tpl/welcome_page.html'
    }).when('/how_it_works', {
      templateUrl : './tpl/how_it_works.html'
    }).when('/view/', {
      redirectTo : '/view/world/'
    }).when('/view/:part/:user?', {
      controller : 'AppView',
      templateUrl : './'+hash('static/tpl/view_tpl.html')
    }).when('/practice/', {
      redirectTo : '/practice/world/'
    }).when('/practice/:part/:place_type?', {
      controller : 'AppPractice',
      templateUrl : './'+hash('static/tpl/practice_tpl.html')
    }).otherwise({
      //redirectTo : '/'
    });
  })

  .run(function($cookies, $http) {
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
  });
}());
