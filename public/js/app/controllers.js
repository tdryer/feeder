(function(angular) {

  angular.module('feeder.controllers', [])

  /**
   * Routes the user to their home page.
   * Routes a visitor to the login page.
   *
   * @controller
   * @route '/'
   */
  .controller('IndexCtrl', function($location, UserService) {
    if (UserService.isLoggedIn()) {
      $location.path('/home');
    } else {
      $location.path('/login');
    }
  })

  /**
   * Displays a user's list of subscriptions.
   * Allows a user to add subscriptions.
   *
   * @controller
   * @route '/home'
   */
  .controller('HomeCtrl', function($scope, $cookies, $location, Restangular, UserService) {
    var feeds, entries;

    if (!UserService.isLoggedIn()) {
      $location.path('/login');
    }

    Restangular = Restangular.withConfig(function(RestangularProvider) {
      RestangularProvider.setDefaultHeaders({
        Authorization: 'xBasic ' + $cookies.auth
      });
    });

    feeds = Restangular.all('feeds');
    entries = Restangular.several('entries', [1, 2, 3, 4]);

    feeds.getList().then(function(data) {
      $scope.testApi = data.feeds;
    });

    $scope.addFeed = {};
    $scope.addFeed.add = function() {

      feeds.post({
        url: this.url
      }).then(function() {

        feeds.getList().then(function(data) {
          $scope.testApi = data.feeds;
        });

      }, function() {
        // if the thing 500s
      });

    }

    entries.getList().then(function(data) {
      $scope.entries = data.entries;
    });

  })

  /**
   * Registers a new user.
   * Routes the user to their home page upon successful registration.
   *
   * @controller
   * @route '/register'
   */
  .controller('RegisterCtrl', function($scope, $location, $timeout, UserService) {
    var timeout;

    $scope.error = false;
    $scope.loading = false;

    $scope.register = function() {
      $timeout.cancel(timeout);

      $scope.loading = true;
      UserService.register($scope.username, $scope.password).then(function() {
        $location.path('/');
      }, function() {
        $scope.error = true;

        timeout = $timeout(function() {
          $scope.error = false;
        }, 200);
      }).then(function() {
        $scope.loading = false;
      });
    }
  })

  /**
   * Routes the user to their home page upon successful authentication.
   *
   * @controller
   * @route '/login'
   * @scope {Function} login Hits the authentication server on button click.
   * @scope {String} username Value of the username input field.
   * @scope {String} password Value of the password input field.
   * @scope {Boolean} error Error state of authentication.
   * @scope {Boolean} loading Loading state of authentication.
   */
  .controller('LoginCtrl', function($scope, $location, $timeout, UserService) {
    var timeout;

    $scope.error = false;
    $scope.loading = false;

    $scope.login = function() {
      $timeout.cancel(timeout);

      $scope.loading = true;
      UserService.login($scope.username, $scope.password).then(function() {
        $location.path('/');
      }, function() {
        $scope.error = true;

        timeout = $timeout(function() {
          $scope.error = false;
        }, 200);
      }).then(function() {
        $scope.loading = false;
      });
    }
  })

  /**
   * Logs a user out of their account.
   * Routes the user to the login page.
   *
   * @controller
   */
  .controller('LogoutCtrl', function($scope, $location, $timeout, UserService) {
    $scope.logout = function() {
      UserService.logout();

      $location.path('/login');
    }
  });

}).call(this, angular);
