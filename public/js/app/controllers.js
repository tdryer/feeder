(function() {

  /**
   * The splash screen.
   *
   * @controller
   * @route '/'
   */
  this.controller('IndexCtrl', angular.noop);

  /**
   * The 404 page.
   *
   * @controller
   * @route '/404'
   */
  this.controller('404Ctrl', angular.noop);

  /**
   * The login page.
   *
   * @controller
   * @route '/login'
   * @scope {Function} login Hits the authentication server on button click.
   * @scope {String} [username=''] Value of the username input field.
   * @scope {String} [password=''] Value of the password input field.
   * @scope {Boolean} [error=false] Does the login form have an error?
   */
  this.controller('LoginCtrl', function($scope, $location, User) {
    $scope.username = '';
    $scope.password = '';
    $scope.error = false;

    $scope.login = function(username, password) {
      $scope.error = false;
      User.login(username, password).then(function() {
        $location.path('/home');
      }, function() {
        $scope.error = true;
      });
    }
  });

  /**
   * The logout page, which is actually just a superficial route so we can
   * bundle the logout and redirect logic together in one controller.
   *
   * @controller
   * @route '/logout'
   */
  this.controller('LogoutCtrl', function($location, User) {
    User.logout();
    $location.path('/');
  });

  /**
   * The register page.
   *
   * @controller
   * @route '/register'
   * @scope {Function} register Registers the visitor.
   * @scope {String} [username=''] Value of the username input field.
   * @scope {String} [password=''] Value of the password input field.
   * @scope {Boolean} [error=false] Does the login form have an error?
   */
  this.controller('RegisterCtrl', function($scope, $location, User) {
    $scope.username = '';
    $scope.password = '';
    $scope.error = false;

    $scope.register = function(username, password) {
      $scope.error = false;
      User.register(username, password).then(function() {
        $location.path('/home');
      }, function() {
        $scope.error = true;
      });
    }
  });

  /**
   * The home page.
   *
   * @controller
   * @route '/home'
   * @scope {Model} [Feeds=Feeds] The `Feeds` model.
   * @scope {Function} subscribe Subscribes to a feed.
   * @scope {Boolean} [error=false] Does the login form have an error?
   */
  this.controller('HomeCtrl', function($scope, Feeds) {
    $scope.Feeds = Feeds;
    $scope.error = false;

    $scope.subscribe = function(url) {
      $scope.error = false;
      Feeds.add(url).then(angular.noop, function() {
        $scope.error = true;
      });
    }
  });

  /**
   * Displays a list of articles for a feed.
   *
   * @controller
   * @route '/home/:feed'
   * @scope {Model} ArticleList The `ArticleList` model.
   */
  this.controller('FeedCtrl', function($scope, ArticleList, Article) {
    $scope.ArticleList = ArticleList;
  });

  /**
   * Displays an article.
   *
   * @controller
   * @route '/home/:feed/:article'
   */
  this.controller('ArticleCtrl', function($scope, $location, Article, data) {
    $scope.article = data;

    $scope.unread = function() {
      Article.status($scope.article.id, 'unread');
      $location.path('/home/' + $scope.article.feed_id);
    }

    Article.status($scope.article.id, 'read');
  })

}).call(angular.module('feeder.controllers', []));
