(function(angular) {

  angular.module('feeder.directives', [])

  /**
   * Navigates a user back one level.
   *
   * @directive
   */
  .directive('back', function() {
    return {
      controller: function($rootScope, $scope) {
        $rootScope.$watch('breadcrumbs', function(breadcrumbs) {
          $scope.anchor = _.last(breadcrumbs);
        });
      }
    }
  })

  /**
   * Displays the user's list of subscriptions.
   *
   * @directive
   * @route '/home'
   */
  .directive('subscriptions', function() {
    return {
      templateUrl: 'partials/subscriptions.html'
    }
  })

  /**
   * Displays the header bar.
   *
   * @directive
   */
  .directive('header', function() {
    return {
      templateUrl: 'partials/header.html',
      controller: function($scope, $rootScope, User) {
        $rootScope.$watch('showHeader', function(showHeader) {
          if (!showHeader) {
            return;
          }

          User.getUsername().then(function(username) {
            $scope.username = username;
          });
        });
      }
    }
  })

  /**
   * Displays the user's username.
   *
   * @directive
   * @route '/home'
   * @scope {String} username The user's username.
   */
  .directive('username', function() {
    return {
      controller: function($scope, User) {
        User.getUsername().then(function(username) {
          $scope.username = username;
        });
      }
    }
  });

}).call(this, angular);
