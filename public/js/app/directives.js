(function() {

  /**
   * Overlays the entire screen if the application is loading.
   *
   * @directive
   * @restrict element
   */
  this.directive('loading', function() {
    return {
      restrict: 'E',
      controller: function($scope, State) {
        $scope.State = State;
      }
    }
  });

  /**
   * The header houses the breadcrumbs, a greeting to the user if he or she is
   * authenticated, and various buttons.
   *
   * @directive
   * @restrict element
   */
  this.directive('header', function() {
    return {
      restrict: 'E',
      controller: function($scope, User) {
        $scope.User = User;
      },
      templateUrl: '/partials/header.html'
    }
  });

  /**
   * Displays the content of an article.
   *
   * @directive
   * @restrict element
   */
  this.directive('content', function() {
    return {
      restrict: 'E',
      link: function(scope, elem$, attrs) {
        elem$.ready(function() {
          elem$.find('a').attr('target', '_blank');
        });
      }
    }
  })

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
  });

}).call(angular.module('feeder.directives', []));
