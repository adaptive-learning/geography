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

  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl : './tpl/welcome_page.html'
    }).when('/how_it_works', {
      templateUrl : './tpl/how_it_works.html'
    }).when('/view/', {
        redirectTo: '/view/world/'
    }).when('/view/:part/:user?', {
      controller : 'AppView',
      templateUrl : './'+Hash('static/tpl/view_tpl.html')
    }).when('/practice/', {
        redirectTo: '/practice/world/'
    }).when('/practice/:part/:place_type?', {
      controller : 'AppPractice',
      templateUrl : './'+Hash('static/tpl/practice_tpl.html')
    }).otherwise({
      //redirectTo: '/'
    });
    
  })

  .run( function($rootScope, $location, $cookies, $http) {    
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] =  'application/x-www-form-urlencoded';
    
    $rootScope.$on( "$routeChangeStart", function(event, next, current) {
      if (!current && next.templateUrl == './tpl/welcome_page.html' ) {
        $rootScope.getUser(function(user){
          if ( user && user.username && user.username != "" ) {
            $location.path( "/view" );
          }
        });
      }
    });
  });
