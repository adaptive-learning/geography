(function() {
  'use strict';
  /* Controllers */
  angular.module('proso.feedback', ['ui.bootstrap'])

  .value('gettext', gettext)

  .directive('feedback', ['$modal', '$window', function ($modal, $window) {
    return {
      restrict: 'A',
      link: function ($scope, element, attrs) {

        $scope.feedback = {
          user_agent: $window.navigator.userAgent,
          email: '@',
          text: '',
        };

        $scope.openFeedback = function () {
          if (attrs.email) {
            $scope.feedback.email = attrs.email;
          }

          $modal.open({
            templateUrl: 'feedback_modal.html',
            controller: ModalFeedbackCtrl,
            size: 'lg',
            resolve: {
              feedback: function () {
                return $scope.feedback;
              }
            }
          });
        };

        var ModalFeedbackCtrl = ['$scope', '$modalInstance', '$http', '$cookies',
              '$location', 'feedback', 'gettext',
            function ($scope, $modalInstance, $http, $cookies, 
              $location, feedback, gettext) {

          $scope.feedback = feedback;
          $scope.alerts = [];

          $scope.send = function() {
            feedback.page = $location.absUrl();
            $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
            $http.post('/feedback/', feedback).success(function(data){
              $scope.alerts.push(data);
              $scope.sending = false;
              feedback.text = '';
            }).error(function(){
              $scope.alerts.push({
                type : 'danger',
                msg : gettext("V aplikaci bohužel nastala chyba."),
              });
              $scope.sending = false;
            });
            $scope.sending = true;
          };

          $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
          };

          $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
          };
        }];

      }
    };
  }]);

})();
