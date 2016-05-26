
/* Controllers */
angular.module('proso.geography.controllers', [])

.controller('AppCtrl', ['$scope', '$rootScope', 'userService', 'pageTitle',
      'configService', 'gettextCatalog', '$location',
    function($scope, $rootScope, userService, pageTitle,
      configService, gettextCatalog, $location) {
        'use strict';
        $scope.configService = configService;
        $scope.userService = userService;

        $rootScope.initTitle = function (title) {
            $rootScope.initialTitle = title;
            $rootScope.title = title;
        };

        $rootScope.$on("$routeChangeStart", function(event, next) {
            $rootScope.title = pageTitle(next) + $rootScope.initialTitle;
        });

        $scope.initLanguageCode = function (code) {
            gettextCatalog.setCurrentLanguage(code);
            $rootScope.LANGUAGE_CODE = code;
        };

        if ($location.search().sessionid) {
          userService.loadUser();
          $location.search('sessionid', undefined);
        } else {
          $scope.initUser = function (data) {
              userService.processUser(data);
          };
        }

        $scope.logout = function() {
            $rootScope.user = userService.logout();
        };

}])

.controller('AppView', ['$scope', '$routeParams', '$filter', 'flashcardService', 'mapTitle', 'placeTypeService', '$location', 'userStatsService',
    function($scope, $routeParams, $filter, flashcardService, mapTitle, placeTypeService, $location, userStatsService) {
        'use strict';
        $scope.part = $routeParams.part;
        $scope.type = $routeParams.type;
        var user = $routeParams.user || '';
        var type = $routeParams.type || '';
        var activePlaceType = placeTypeService.getBySlug(type);
        if (type && !activePlaceType) {
          user = type;
          $scope.type = undefined;
        }

        if ($routeParams.user == 'average') {
          $scope.average = true;
        }

        var placeTypes = placeTypeService.getTypes();
        for (var j = 0; j < placeTypes.length; j++) {
          var pt = placeTypes[j];
          userStatsService.addGroup(pt.identifier, {});
          userStatsService.addGroupParams(pt.identifier,
            [['context/' + $routeParams.part, 'category/' + pt.identifier]], '');
        }
        userStatsService.getStatsPost(true).success(function(data) {
          for (var j = 0; j < placeTypes.length; j++) {
            var pt = placeTypes[j];
            pt.stats = data.data[pt.identifier];
            if (pt.name == activePlaceType){
              activePlaceType = pt;
            }
          }
          $scope.placesTypes = placeTypes;
          $scope.updateMap(activePlaceType);
        });

        $scope.placeClick = function(place) {
            $scope.imageController.highlightItem(place.description);
        };

        $scope.updateMap = function(type) {

            angular.forEach($scope.placesTypes, function(type) {
                type.hidden = true;
            });
            if (!type && $scope.placesTypes) {
              type = $scope.placesTypes.filter(function(type) {
                return type.stats.number_of_flashcards;
              })[0];
            }
            if (type) {
              type.hidden = false;
              $scope.type = type.identifier;
              if (!type.places) {
                var filter = {
                    filter : [[
                      'context/' + $routeParams.part,
                      'category/' + type.identifier
                    ]],
                    stats : true,
                };
                if ($routeParams.user == 'average') {
                  filter.new_user_predictions = true;
                }
                flashcardService.getFlashcards(filter).then(function(data) {
                  type.places = data;
                  angular.forEach(type.places, function(flashcard) {
                    if (filter.new_user_predictions) {
                      flashcard.prediction = flashcard.new_user_prediction;
                      flashcard.practiced = true;
                    }
                    flashcard.prediction = Math.ceil(flashcard.prediction * 10) / 10;
                  });
                  type.loaded = true;
                  $scope.imageController.updateItems($scope.placesTypes, true);
                }, function(){
                    $scope.error = true;
                });
              }
            }
            $scope.imageController.updateItems($scope.placesTypes, false);
            $scope.name = mapTitle($scope.part, user);

            var newPath = '/' + [
              'view',
              $routeParams.part,
              type.identifier,
              user,
            ].join('/').replace('//', '/');
            $location.update_path(newPath);
        };
    }
])

.controller('AppPractice', ['$scope', '$routeParams', '$timeout', '$filter',
    'practiceService', 'userService', '$rootScope', 'colors', '$', 'highlighted',
    'categoryService', 'flashcardService', '$http',

    function($scope, $routeParams, $timeout, $filter,
        practiceService, userService, $rootScope, colors, $, highlighted,
        categoryService, flashcardService, $http) {
        'use strict';

        $scope.part = $routeParams.part;
        $scope.placeType = $routeParams.place_type;
        $scope.progress = 0;

        $scope.highlight = function() {
            var active = $scope.question;
            $scope.layer = $scope.imageController.getLayerContaining(active.description);
            $scope.imageController.highLightLayer($scope.layer);
            $scope.imageController.placeToFront(active.description);
            if ($filter('isPickNameOfType')($scope.question)) {
                var callback = function(iteration) {
                  $scope.imageController.highlightItem(active.description, colors.NEUTRAL);
                  $timeout(function() {
                    if (!active.responseTime) {
                      callback(iteration + 1);
                    }
                  }, 2000 * iteration * iteration);
                };
                callback(1);
            }
            if ($filter('isFindOnMapType')($scope.question) && active.options) {
                var codes = active.options.map(function(option) {
                    return option.description;
                });
                highlighted.setHighlighted(codes);
                $scope.imageController.highlightItems(codes, colors.NEUTRAL);
            }
        };

        $scope.checkAnswer = function(selected) {
            if ($scope.checking) {
                return;
            }
            $scope.checking = true;
            var asked = $scope.question.description;
            highlightAnswer(asked, selected);
            $scope.question.answered_code = selected;
            $scope.question.responseTime = new Date().valueOf() - $scope.question.startTime;
            var selectedFC = flashcardService.getFlashcardByDescription(selected);
            if ($scope.question.meta != 'email') {
              practiceService.saveAnswerToCurrentQuestion(selectedFC ? selectedFC.id : null, $scope.question.responseTime);
            } else {
              saveEmailAnswer($scope.question, selectedFC ? selectedFC.id : null, $scope.question.responseTime);
            }
            $scope.progress = 100 * (practiceService.getSummary().count / practiceService.getConfig().set_length);
            //user.addAnswer(asked == selected);
            if (asked == selected) {
                $timeout(function() {
                    $scope.next(function() {
                      $scope.checking = false;
                    });
                }, 700);
            } else {
                $scope.checking = false;
                $scope.canNext = true;
            }
            addAnswerToUser(asked == selected);
        };

        $scope.next = function(callback) {
            if ($scope.progress < 100) {
                $scope.loadingNextQuestion = true;
                practiceService.getQuestion().then(function(q) {
                    $scope.loadingNextQuestion = false;
                    q.payload.question_type = q.question_type;
                    setQuestion(q.payload);
                    if (callback) callback();
                }, function(){
                    $scope.loadingNextQuestion = false;
                    $scope.error = true;
                });
            } else {
                setupSummary();
                if (callback) callback();
            }
        };

        function addAnswerToUser(isCorrect) {
          if (userService.user.profile) {
            userService.user.profile.number_of_answers++;
            if (isCorrect) {
              userService.user.profile.number_of_correct_answers++;
            }
          }
        }

        function highlightAnswer (asked, selected) {
            if ($filter('isFindOnMapType')($scope.question)) {
                $scope.imageController.highlightItem(asked, colors.GOOD);
            }
            $scope.imageController.highlightItem(selected, asked == selected ? colors.GOOD : colors.BAD);
            if ($filter('isPickNameOfType')($scope.question) && $scope.question.options) {
                highlightOptions(selected);
            }
        }

        function setupSummary() {
            $scope.question.slideOut = true;
            $scope.layer = undefined;
            // prevents additional points gain. issue #38
            $scope.summary = practiceService.getSummary();
            $scope.summary.correctlyAnsweredRatio = $scope.summary.correct / $scope.summary.count;
            $scope.showSummary = true;
            $scope.imageController.clearHighlights();
            $scope.imageController.hideLayers();
            $scope.imageController.showSummaryTooltips($scope.questions);
            angular.forEach($scope.summary.questions, function(q) {
                var correct = q.payload.description == q.payload.answered_code;
                $scope.imageController.showLayerContaining(q.payload.description);
                $scope.imageController.highlightItem(q.payload.description, correct ? colors.GOOD : colors.BAD);
            });
            $("html, body").animate({ scrollTop: "0px" });
            $rootScope.$emit('questionSetFinished');
        }

        function setQuestion(active) {
            if ($scope.question) {
                $scope.question.slideOut = true;
            }
            active.term.type = $scope.placeType;
            $scope.question = active;
            $scope.question.startTime = new Date().valueOf();
            $scope.questions.push(active);
            $scope.imageController.clearHighlights();
            $scope.highlight();
            $scope.canNext = false;
        }

        function highlightOptions(selected) {
            $scope.question.options.map(function(o) {
                o.correct = o.description == $scope.question.description;
                o.selected = o.description == selected;
                o.disabled = true;
                return o;
            });
        }

        function isInActiveLayer(code) {
            return $scope.layer == $scope.imageController.getLayerContaining(code);
        }

        function saveEmailAnswer(question, answeredId, responseTime) {
          var answer = {
            "flashcard_id": question.id,
            "flashcard_answered_id": answeredId,
            "response_time": responseTime,
            "question_type": question.question_type,
            "meta": {"referer" : "email"},
          };
          $http.post("/models/answer/",
            {answer: answer},
            {params : question.filter});
        }

        $scope.mapCallback = function() {
            practiceService.initSet('common');
            var filter = {
                filter : [[
                  'context/' + $routeParams.part,
                  // TODO fix
                  // '-category/' + 'too_small',
                ]]
            };
            if ($routeParams.place_type) {
                filter.filter[0].push('category/' +$routeParams.place_type);
            }
            flashcardService.getFlashcards(filter).then(function() {
              practiceService.setFilter(filter);
              if ($routeParams.q) {
                flashcardService.getFlashcardById($routeParams.q).then(function(q) {
                  q.question_type = $routeParams.d || 't2d';
                  q.options = [];
                  q.meta = 'email';
                  q.filter = filter;
                  $scope.questions = [];
                  setQuestion(q);
                });
              } else {
                practiceService.getQuestion().then(function(q) {
                    $scope.questions = [];
                    q.payload.question_type = q.question_type;
                    setQuestion(q.payload);
                    var imageName = $routeParams.part + '-' + $routeParams.place_type + (
                      q.question_type == 'd2t' ? '-' + q.payload.description : '');
                    if (! q.payload.options || q.payload.options.length === 0) {
                      $rootScope.$emit('imageDisplayed', imageName);
                    }
                }, function(){
                    $scope.error = true;
                });
              }
            }, function(){
                $scope.error = true;
            });
            $scope.imageController.onClick(function(code) {
                if ($filter('isFindOnMapType')($scope.question) &&
                    !$scope.canNext &&
                    $filter('isAllowedOption')($scope.question, code) &&
                    isInActiveLayer(code)) {

                    $scope.checkAnswer(code);
                    $scope.$apply();
                }
            });
    };
  }])

.controller('AppOverview', ['$scope', '$routeParams', 'categoryService', 'userStatsService', 'placeTypeService', 'gettextCatalog',
    function($scope, $routeParams, categoryService, userStatsService, placeTypeService, gettextCatalog) {
        'use strict';

        // var mapSkills = {};
        function addNamesAndSort(categories) {
          var categoryNames = {
            'state' : gettextCatalog.getString('Státy'),
            'continent' : gettextCatalog.getString('Kontinenty'),
            'region' : gettextCatalog.getString('Kraje ČR'),
          };
          var categoriesByIdentifier = {};
          for (var i = 0; i < categories.length; i++) {
            categories[i].name = categoryNames[categories[i].identifier];
            categoriesByIdentifier[categories[i].identifier] = categories[i];
          }
          var categoryTypes = ['world', 'continent', 'state', 'region'];
          var ret = [];
          for (i = 0; i < categoryTypes.length; i++) {
            if (categoriesByIdentifier[categoryTypes[i]]) {
              ret.push(categoriesByIdentifier[categoryTypes[i]]);
            }
          }
          return ret;
        }

        $scope.user = $routeParams.user || '';
        $scope.refreshthumbs = $routeParams.refreshthumbs || '';
        categoryService.getAll().then(function(categories){
            $scope.mapCategories = addNamesAndSort(categories);
            var maps = [];
            for (var i = 0; i < categories.length; i++) {
              maps = maps.concat(categories[i].maps);
            }
            var placeTypes = placeTypeService.getTypes();
            for (i = 0; i < maps.length; i++) {
              var map = maps[i];
              for (var j = 0; j < placeTypes.length; j++) {
                var pt = placeTypes[j];
                var id = map.identifier + '-' + pt.identifier;
                userStatsService.addGroup(id, {});
                userStatsService.addGroupParams(id,
                  [['context/' +map.identifier, 'category/' + pt.identifier]], '');
              }
            }

            userStatsService.getStatsPost().success(function(data) {
              processStats(data);
              userStatsService.getStatsPost(true).success(processStats);
            });

            function processStats(data) {
              $scope.userStats = data.data;
              angular.forEach(maps, function(map) {
                map.placeTypes = [];
                angular.forEach(angular.copy(placeTypes), function(pt) {
                  var key = map.identifier + '-' + pt.identifier;
                  pt.stats = data.data[key];
                  if (pt.stats && pt.stats.number_of_flashcards > 0) {
                    map.placeTypes.push(pt);
                  }
                });
              });
              $scope.statsLoaded = true;
            }
        }, function(){});

        $scope.mapSkills = function(map, type) {
            if (!$scope.statsLoaded) {
                return;
            }
            var defalut = {
                count : 0
            };
            if (!type) {
                return avgSkills(map);
            }
            return type.stats || defalut;
        };

        function avgSkills(map) {
            var avg = {};
            angular.forEach(map.placeTypes, function(pt) {
              for (var i in pt.stats) {
                if (!avg[i]) {
                  avg[i] = 0;
                }
                avg[i] += pt.stats[i];
              }
            });
            return avg;
        }
    }
])

.controller('AppConfused', ['$scope', '$http',
    function($scope, $http){
        'use strict';
        $http.get('/confused/').success(function(data){
            angular.forEach(data, function(p){
                p.wrongRatio = p.mistake_count / p.asked_count;
            });
            $scope.confused = data;
            $scope.loaded = true;
        }).error(function(){
            $scope.loaded = true;
            $scope.error = true;
        });
    }
])

.controller('AppUser', ['$scope', 'userService', '$routeParams', '$location',
    '$timeout', 'gettextCatalog',
    function($scope, userService, $routeParams, $location, $timeout, gettextCatalog) {

  $scope.profileUrl = $location.absUrl();
  if ($routeParams.user == userService.user.username) {
    $scope.user = userService.user;
    $scope.editRights = true;
    if ($routeParams.edit !== undefined && $scope.editRights) {
      $timeout(function() {
        $scope.editableForm.$show();
      },10);
    }
  } else {
    $scope.user = {username: $routeParams.user};
    userService.getUserProfile($routeParams.username, true).success(function(response){
      $scope.user = response.data;
    }).error(function() {
      $scope.error = gettextCatalog.getString("Hledaný profil neexistuje.");
      console.error($scope.error);
    });
  }

  $scope.saveUser = function() {
    // $scope.user already updated!
    return userService.updateProfile($scope.user).error(function(err) {
      if(err.field && err.msg) {
        // err like {field: "name", msg: "Server-side error for this username!"}
        $scope.editableForm.$setError(err.field, err.msg);
      } else {
        // unknown error
        $scope.editableForm.$setError('name', gettextCatalog.getString("V aplikaci bohužel nastala chyba."));
      }
    });
  };

}])


.controller('ReloadController', ['$window', function($window){
    'use strict';
    $window.location.reload();
}]);

