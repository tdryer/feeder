(function(angular) {

  var directives = angular.module('feeder.directives', [])

  /**
   * Displays the user's username.
   *
   * @directive
   * @route '/home'
   * @scope {String} username The user's username.
   */
  .directive('username', function() {
    return {
      controller: function($scope, UserService) {
        UserService.getUsername().then(function(username) {
          $scope.username = username;
        });
      }
    }
  })

  /**
   * Logs a user out.
   * Routes the visitor to the login page.
   *
   * @directive
   * @route '/home'
   * @scope {Function} logout Deletes the session cookie.
   */
  .directive('logout', function() {
    return {
      controller: function($scope, UserService) {
        $scope.logout = UserService.logout;
      },
      link: function(scope, element) {
        element.on('click', scope.logout);
      }
    }
  });

}).call(this, angular);
