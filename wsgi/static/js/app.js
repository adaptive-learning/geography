'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers'])

  .config(function($routeProvider) {
    $routeProvider.when('/', {
      redirectTo: '/view/Afrika'
    }).when('/view/:part', {
      controller : 'AppView',
      templateUrl : './tpl/view_tpl.html'
    }).when('/practice/:part', {
      controller : 'AppPractice',
      templateUrl : './tpl/practice_tpl.html'
    }).when('/practice/:part/:type', {
      controller : 'AppPractice',
      templateUrl : './tpl/practice_tpl.html'
    }).otherwise({
      //redirectTo: '/'
    });
  })
