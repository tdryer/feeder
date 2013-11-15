(function(angular) {

  var directives = angular.module('feeder.directives', [])

  .directive('headerBar', function() {
    return {
      restrict: 'E',
      templateUrl: './partials/header.html',
      replace: true
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
