(function(angular) {

  var directives = angular.module('feeder.directives', ['feeder.services'])
    .directive('headerBar', function() {
      return {
        restrict: 'E',
        templateUrl: './partials/header.html',
        replace: true
      }
    })
    
    .directive('logout', function() {
      return {
        restrict: 'E',
        templateUrl: './partials/logout.html',
        replace: true,
        controller: 'LogoutCtrl'
      }
    });

}).call(this, angular);
