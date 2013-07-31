'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers', 'ngCookies'])

  .config(function($routeProvider) {
    $routeProvider.when('/', {
      templateUrl : './static/tpl/welcome_page_tpl.html'
    }).when('/view/', {
        redirectTo: '/view/USA/'
    }).when('/view/:part/:user', {
      controller : 'AppView',
      templateUrl : './static/tpl/view_tpl.html'
    }).when('/practice/', {
        redirectTo: '/practice/USA'
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
