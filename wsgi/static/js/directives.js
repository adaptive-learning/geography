'use strict';

/* Directives */


angular.module('myApp.directives', []).
  directive('appVersion', ['version', function(version) {
    return function(scope, elm, attrs) {
      elm.text(version);
    };
  }])
  
  .directive('state', function() {
    // return the directive link function. (compile function not needed)
    return function(scope, element, attrs) {
      var code = attrs.code;
      var name = attrs.name;
      var template = '<span class="label" ng-show="question.type == 0"> '+
        '<i class="flag-us-'+code+'"></i> '+ name +
        '</span>';

        element.html(template)
    }

  })
  
  .directive('autocompleteUsername', function() {
	  return function($scope, element) {
	    return $scope.getUsername = function() {
	      return element.val();
	    };
	  };
  })

  .directive('autocompletePassword', function() {
	  return function($scope, element) {
	    return $scope.getPassword = function() {
	      return element.val();
	    };
	  };
  });
