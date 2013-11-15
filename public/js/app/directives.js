(function(angular) {

  angular.module('feeder.directives', [])

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
   * @route '/home'
   */
  .directive('header', function() {
    return {
      templateUrl: 'partials/header.html'
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
