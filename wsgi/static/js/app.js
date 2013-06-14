'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers'])

  .config(function($routeProvider) {
    $routeProvider.when('/', {
      redirectTo: '/view/USA'
    }).when('/view/:part', {
      controller : 'AppView',
      templateUrl : './static/tpl/view_tpl.html'
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
