/* Directives */
angular.module('proso.geography.directives', ['proso.geography.templates'])

  .directive('placeLabel', ['colorScale', 'gettext', function(colorScale, gettext) {
    return {
      restrict : 'A',
      template : '<i class="flag-{{place.description}}"></i> {{place.term.name}}',
      link : function($scope, elem) {
        elem.addClass('label');
        elem.addClass('label-default');
        elem.tooltip({
          html : true,
          placement: 'bottom',
          container: 'body',
          title : '<div class="skill-tooltip">' +
                gettext('Odhad znalosti') +
                ' <span class="badge badge-default">' +
                  '<i class="color-indicator" style="background-color :' +
                  colorScale($scope.place.prediction).hex() + '"></i>' +
                  Math.round(10 * $scope.place.prediction) + ' / 10 ' +
                '</span>' +
               '</div>'
        });
      }
    };
  }])

  .directive('blindMap', ['mapControler', 'places', 'singleWindowResizeFn',
        'getMapResizeFunction', '$parse',
      function(mapControler, places, singleWindowResizeFn,
        getMapResizeFunction, $parse) {
    return {
      restrict : 'E',
      templateUrl : 'static/tpl/map_tpl.html',
      link : function($scope, elem, attrs) {
        $scope.loading = true;
        $scope.name = places.getName($scope.part);
        $scope.practice = !attrs.showTooltips;
        var showTooltips = attrs.showTooltips !== undefined;

        var map = mapControler($scope.part, showTooltips, elem, function(m) {
          $scope.loading = false;
          var resize = getMapResizeFunction(m, elem, $scope.practice);
          singleWindowResizeFn(resize);
          resize();
          $scope.$eval(attrs.callback);
          $scope.$digest();
        });
        var model = $parse(attrs.map);
        //Set scope variable for the map
        model.assign($scope, map);
      },
      replace : true
    };
  }])

  .directive('email', function() {
    return {
      restrict : 'C',
      compile : function(elem) {
        var emailAddress = elem.html();
        emailAddress = emailAddress.replace('{zavinac}', '@');
        emailAddress = '<a href="mailto:' + emailAddress +
  '">' + emailAddress +
  '</a>';
        elem.html(emailAddress);
      }
    };
  })

  .directive('atooltip', function() {
    return {
      restrict : 'C',
      link : function($scope, elem, attrs) {
        elem.tooltip({
          'placement' : attrs.placement || 'bottom',
          'container' : attrs.container,
        });
      }
    };
  })

  .directive('points', ['$timeout', 'events', function($timeout, events) {
    return {
      scope : true,
      restrict : 'C',
      link : function($scope, elem) {
        events.on('userUpdated', function(user) {
          $scope.user = user;
          if (user.points == 1) {
            $timeout(function() {
              elem.tooltip('show');
            }, 0);
          }
        });
      }
    };
  }])

  .directive('mapProgress', ['gettext', function(gettext) {
    return {
      restrict : 'C',
      template : '<div class="progress overview-progress">' +
                    '<div class="progress-bar progress-bar-learned" style="' +
                        'width: {{100 * skills.number_of_mastered_flashcards / skills.number_of_flashcards}}%;">' +
                    '</div>' +
                    '<div class="progress-bar progress-bar-practiced" style="' +
                        'width: {{100 * skills.number_of_nonmastered_practiced_flashcards / skills.number_of_flashcards}}%;">' +
                    '</div>' +
                  '</div>',
      link : function($scope, elem, attrs) {
        attrs.$observe('skills', function(skills) {
          if(skills !== '') {
            $scope.skills = angular.fromJson(skills);
            $scope.skills.number_of_nonmastered_practiced_flashcards = 
              $scope.skills.number_of_practiced_flashcards - 
              $scope.skills.number_of_mastered_flashcards; 
            elem.tooltip({
              html : true,
              placement: 'bottom',
              container: 'body',
              title : '<div class="skill-tooltip">' +
                     gettext('Naučeno') + ' ' +
                     '<span class="badge badge-default">' +
                       '<i class="color-indicator learned"></i>' +
                       ($scope.skills.number_of_mastered_flashcards || 0) + ' / ' +
                       $scope.skills.number_of_flashcards +
                     '</span>' +
                   '</div>' +
                   '<div class="skill-tooltip">' +
                     gettext('Procvičováno') + ' ' +
                     '<span class="badge badge-default">' +
                       '<i class="color-indicator practiced"></i>' +
                       ($scope.skills.number_of_nonmastered_practiced_flashcards || 0) + ' / ' +
                       $scope.skills.number_of_flashcards +
                     '</span>' +
                   '</div>'
            });
          }
        });
      }
    };
  }])

  .directive('levelProgressBar',['user', '$timeout', 'gettext',
      function(user, $timeout, gettext) {
    return {
      restrict : 'C',
      template : '<span class="badge level-start" ' +
                   'tooltip-append-to-body="true" ' +
                   'ng-bind="level.level" tooltip="' + gettext('Aktuální úroveň') + '">' +
                 '</span>' +
                 '<div class="progress level-progress" ' +
                     'tooltip-append-to-body="true" ' +
                     'tooltip="{{level.points}} / {{level.range}} ' +
                     gettext('bodů do příští úrovně') + '">' +
                   '<div class="progress-bar progress-bar-warning" ' +
                        'style="width: {{(level.points/level.range)|percent}};">' +
                   '</div>' +
                 '</div>' +
                 '<span class="badge level-goal" ' +
                     'tooltip-append-to-body="true" ' +
                     'ng-bind="level.level+1" tooltip="' + gettext('Příští úroveň') + '">' +
                 '</span>',
      link : function($scope, elem, attrs) {
        elem.addClass('level-wrapper');
        if (attrs.username) {
          user.getPromiseByName(attrs.username).success(function(data){
            $scope.level = user.getLevelInfo(data);
          });
        } else {
          $scope.level = user.getUser().getLevelInfo();
        }
      }
    };
  }])

  .directive('myGooglePlus', ['$window', function ($window) {
    return {
      restrict: 'A',
      link: function (scope, element) {
        element.addClass('g-plus');
        scope.$watch(function () { return !!$window.gapi; },
          function (gapiIsReady) {
            if (gapiIsReady) {
              $window.gapi.plus.go(element.parent()[0]);
            }
          });
      }
    };
  }])

  .directive('myFbShare', ['$window', function ($window) {
    return {
      restrict: 'A',
      link: function (scope, element) {
        element.addClass('fb-share-button');
        scope.$watch(function () { return !!$window.FB; },
          function (fbIsReady) {
            if (fbIsReady) {
              $window.FB.XFBML.parse(element.parent()[0]);
            }
          });
      }
    };
  }])

  .directive('locationAppend', ['$rootScope', '$location',
      function ($rootScope, $location) {
    return {
      restrict: 'A',
      link: function ($scope, element, attrs) {
        var url = attrs.href.substring(0, 3);
        $rootScope.$on("$routeChangeSuccess", function() {
          element.attr('href', url + $location.path());
        });
      }
    };
  }])

  .directive('trackClick', ['$analytics', function ($analytics) {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        element.click(function(){
          $analytics.eventTrack('click', {
            category: attrs.trackClick,
            label: attrs.href,
          });
        });
      }
    };
  }])

  .directive('dynamicTitle', ['$rootScope', 'pageTitle', '$route', '$timeout',
      function ($rootScope, pageTitle, $route, $timeout) {
    return {
      restrict : 'A',
      scope : {},
      link : function (scope, element, attrs) {
        $rootScope.$on("$locationChangeSuccess", function() {
          $rootScope.title = pageTitle($route.current) + attrs.dynamicTitle;
          //console.log($rootScope.title);
          $timeout(function() {
            element.text($rootScope.title);
            //console.log($rootScope.title);
          }, 0, false);
        });
      }
    };
  }])

  .directive('setPlaceTypeNames', ['places', function (places) {
    return {
      restrict : 'A',
      link : function (scope, element, attrs) {
        var obj = angular.fromJson(attrs.setPlaceTypeNames);
        places.setPlaceTypeNames(obj);
      }
    };
  }])

  .directive('errorMessage', ['gettext', function (gettext) {
    return {
      restrict : 'A',
      template: '<div class="alert alert-danger">' +
                  gettext("V aplikaci bohužel nastala chyba.") +
                '</div>',
    };
  }])

  .directive('showAfterXAnswers', ['$timeout', 'events', function($timeout, events) {
    return {
      scope : true,
      restrict : 'A',
      link : function($scope, elem, attrs) {
        var x = parseInt(attrs.showAfterXAnswers);
        events.on('userUpdated', function(user) {
          if (user.answered_count == x) {
            $timeout(function() {
              elem.tooltip({
                placement: 'right',
                title : elem.attr('tooltip'),
              });
              elem.tooltip('show');
            }, 100);
          }
        });
      }
    };
  }]);
