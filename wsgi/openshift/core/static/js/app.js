'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers', 'ngCookies'])

  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl : './tpl/welcome_page.html'
    }).when('/how_it_works', {
      templateUrl : './tpl/how_it_works.html'
    }).when('/view/', {
        redirectTo: '/view/world/'
    }).when('/view/:part/:user', {
      controller : 'AppView',
      templateUrl : './static/tpl/view_tpl.html'
    }).when('/practice/', {
        redirectTo: '/practice/world'
    }).when('/practice/:part', {
      controller : 'AppPractice',
      templateUrl : './static/tpl/practice_tpl.html'
    }).when('/practice/:part/:type', {
      controller : 'AppPractice',
      templateUrl : './static/tpl/practice_tpl.html'
    }).otherwise({
      //redirectTo: '/'
    });
  })
  
  .run( function($rootScope, $location) {
    $rootScope.$on( "$routeChangeStart", function(event, next, current) {
      if ( next.templateUrl == "./tpl/welcome_page.html" ) {
        $rootScope.getUser(function(user){
          if ( user && user.username && user.username != "" ) {
            $location.path( "/view" );
          }
        })
      }
    });
  })
