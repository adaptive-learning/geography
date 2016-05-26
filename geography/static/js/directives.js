/* Directives */
angular.module('proso.geography.directives', ['proso.geography.templates'])

  .directive('placeLabel', ['colorScale', 'gettextCatalog', function(colorScale, gettextCatalog) {
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
                '<div>' +
                  gettextCatalog.getString('Odhad znalosti') +
                  ' <span class="badge badge-default">' +
                    '<i class="color-indicator" style="background-color :' +
                    colorScale($scope.place.prediction).hex() + '"></i>' +
                    (10 * $scope.place.prediction) + ' / 10 ' +
                  '</span>' +
                '</div>' +
                ($scope.place['state-by-city'] ? '<div>' +
                  gettextCatalog.getString('Hlavní město') + ': ' +
                  ' <span class="label label-default">' +
                   $scope.place['state-by-city']  +
                  '</span></div>' : '') +
                ($scope.place['city-by-state'] ? '<div>' +
                  gettextCatalog.getString('Stát') + ': ' +
                  ' <span class="label label-default">' +
                   $scope.place['city-by-state']  +
                  '</span></div>' : '') +
               '</div>'
        });
      }
    };
  }])

  .directive('termLabel', ['gettextCatalog', function(gettextCatalog) {
    return {
      restrict : 'A',
      template : '<i class="flag-{{code}}"></i> {{name}}',
      link : function($scope, elem, attrs) {
        var term = angular.fromJson(attrs.termLabel);
        $scope.code = term.identifier;
        $scope.name = term.name;
        if (term.type == 'state-by-city') {
          $scope.code = 'none';
          $scope.name = gettextCatalog.getString(
            'stát s hl. městem') + ' ' + term.name;
        }
        if (term.type == 'city-by-state') {
          $scope.code = 'none';
          $scope.name = gettextCatalog.getString(
            'hl. město státu') + ' ' + term.name;
        }
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
        var config = {
          showTooltips: attrs.showTooltips !== undefined,
          mapCode : $scope.part,
          layerId : ($scope.placeType || '').split('-by-')[0],
        };

        var map = mapControler(elem, config, function(m) {
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

  .directive('mapProgress', ['gettextCatalog', function(gettextCatalog) {
    return {
      restrict : 'C',
      template : '<div class="progress overview-progress">' +
                    '<div class="progress-bar progress-bar-learned" style="' +
                        'width: {{100 * skills.number_of_mastered_flashcards / skills.number_of_flashcards}}%;"' +
                        'ng-if="skills.number_of_practiced_flashcards">' +
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
              Math.max(0, $scope.skills.number_of_practiced_flashcards -
              ($scope.skills.number_of_mastered_flashcards || 0));
            if($scope.skills.number_of_mastered_flashcards !== undefined) {
              elem.tooltip({
                html : true,
                placement: 'bottom',
                container: 'body',
                title : '<div class="skill-tooltip">' +
                       gettextCatalog.getString('Naučeno') + ' ' +
                       '<span class="badge badge-default">' +
                         '<i class="color-indicator learned"></i>' +
                         $scope.skills.number_of_mastered_flashcards + ' / ' +
                         $scope.skills.number_of_flashcards +
                       '</span>' +
                     '</div>' +
                     '<div class="skill-tooltip">' +
                       gettextCatalog.getString('Procvičováno') + ' ' +
                       '<span class="badge badge-default">' +
                         '<i class="color-indicator practiced"></i>' +
                         ($scope.skills.number_of_nonmastered_practiced_flashcards || 0) + ' / ' +
                         $scope.skills.number_of_flashcards +
                       '</span>' +
                     '</div>'
              });
            }
          }
        });
      }
    };
  }])

  .directive('levelProgressBar',['userService', '$timeout', 'gettextCatalog',
      function(userService, $timeout, gettextCatalog) {

    function getLevelInfo(user) {
      var points = user.number_of_correct_answers || 0;
      console.log(user);
      var levelEnd = 0;
      var levelRange = 30;
      var rangeIncrease = 0;
      for (var i = 1; true; i++) {
        levelEnd += levelRange;
        if ((points || 0) < levelEnd) {
          return {
            level : i,
            form : levelEnd - levelRange,
            to : levelEnd,
            range : levelRange,
            points : points - (levelEnd - levelRange),
          };
        }
        levelRange += rangeIncrease;
        rangeIncrease += 10;
      }

    }
    return {
      restrict : 'C',
      template : '<span class="badge level-start" ' +
                   'tooltip-append-to-body="true" ' +
                   'ng-bind="level.level" tooltip="' + gettextCatalog.getString('Aktuální úroveň') + '">' +
                 '</span>' +
                 '<div class="progress level-progress" ' +
                     'tooltip-append-to-body="true" ' +
                     'tooltip="{{level.points}} / {{level.range}} ' +
                     gettextCatalog.getString('bodů do příští úrovně') + '">' +
                   '<div class="progress-bar progress-bar-warning" ' +
                        'style="width: {{(level.points/level.range)|percent}};">' +
                   '</div>' +
                 '</div>' +
                 '<span class="badge level-goal" ' +
                     'tooltip-append-to-body="true" ' +
                     'ng-bind="level.level+1" tooltip="' + gettextCatalog.getString('Příští úroveň') + '">' +
                 '</span>',
      link : function($scope, elem, attrs) {
        elem.addClass('level-wrapper');
        if (attrs.username != userService.user.username) {
          userService.getUserProfile(attrs.username, true).success(function(data){
            $scope.level = getLevelInfo(data.data);
          });
        } else {
          $scope.level = getLevelInfo(userService.user.profile);
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

  .directive('errorMessage', ['gettextCatalog', function (gettextCatalog) {
    return {
      restrict : 'A',
      template: '<div class="alert alert-danger">' +
                  '<p><strong>' +
                  gettextCatalog.getString("V aplikaci bohužel nastala chyba.") +
                  '</strong></p>' +
                  '<ul><li>' +
                    gettextCatalog.getString('Pro vyřešení problému zkuste') +
                    ' <a href="" onClick="window.location.href=window.location.href" ' +
                        'class="btn btn-default">' +
                      gettextCatalog.getString('obnovit stránku') +
                    '</a>' +
                  '</li><li>' +
                    gettextCatalog.getString("Pokud problém přetrval zkuste to znovu později nebo") +
                    ' <a feedback-comment class="btn btn-default" email="{{email}}" href=""> ' +
                       gettextCatalog.getString('nám napište')  +
                    '</a>' +
                  '</li></ul>' +
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
  }])

  .directive('contentAdminBanner', [function() {
    return {
      restrict: 'A',
      templateUrl : 'static/tpl/content_admin_banner.html',
    };
  }])

  .directive('setCookieOnClick', ['$cookies', function($cookies) {
    return {
      restrict: 'A',
      link: function ($scope, element, attrs) {
        element.click(function() {
          $cookies[attrs.setCookieOnClick] = 'true';
        });
      }
    };
  }])

  .directive('signInBanner', ['userService', 'signupModal',
      function(userService, signupModal) {
    return {
      restrict: 'A',
      templateUrl : 'static/tpl/sign_in_banner.html',
      link: function ($scope) {
        $scope.userService = userService;
        $scope.openSignupModal = function() {
            signupModal.open();
        };
      }
    };
  }])

  .directive('imageScreenShot', ['$rootScope', '$http', '$timeout',
      function($rootScope, $http, $timeout) {
    var screenshotTaken;
    return {
      restrict: 'A',
      replace: true,
      template : '<canvas style="display: none" id="screen-shot"></canvas> ',
      link: function () {
        function takeScreenshot(event, identifier) {
          if (screenshotTaken) {
            return;
          }
          var svg = document.querySelector( "svg" );
          var svgData = new XMLSerializer().serializeToString(svg);
          var canvas = document.getElementById("screen-shot");
          window.canvg(canvas, svgData);
          var imgSrc    = canvas.toDataURL("image/png");
          var data = {
            name : identifier,
            image : imgSrc,
          };
          $http.post('/savescreenshot/', data);
          screenshotTaken = true;
        }
        $rootScope.$on('imageDisplayed', function(event, identifier) {
          $timeout(function() {
            takeScreenshot(event, identifier);
          }, 500);
        });

      }
    };
  }]);

