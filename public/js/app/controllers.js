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
  this.controller('LogoutCtrl', function($location, Feeds, User) {
    User.logout();
    Feeds.clear();
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
  this.controller('HomeCtrl', function($scope, $window, ArticleList, Feeds) {
    $scope.Feeds = Feeds;
    $scope.error = false;
    $window.prevScrollY = 0; // Reset cached scroll position
    Tinycon.setBubble($scope.Feeds.unreads);

    $scope.subscribe = function(url) {
      $scope.error = false;
      Feeds.add(url).then(angular.noop, function() {
        $scope.error = true;
      });
    }
  });

  /**
   * The feed article list page.
   *
   * @controller
   * @route '/home/:feed'
   * @scope {Model} ArticleList The `ArticleList` model.
   * @scope {Object} feed The parent feed object of the article list.
   */
  this.controller('FeedCtrl', function($scope, $window, $document, Feeds,
                                       ArticleList, Article, State) {
    $scope.feed = Feeds.id(ArticleList.id);
    $scope.ArticleList = ArticleList;
    $scope.Article = Article;
    ArticleList.push();
    Tinycon.setBubble($scope.feed.unreads);

    $document.ready(function() {
      $window.scrollTo(0, $window.prevScrollY);
    });

    $scope.$watch('State.loading', function() {
      if (State.loading === true) {
        $window.prevScrollY = $window.scrollY;
      }
    });
  });

  /**
   * The article page.
   *
   * @controller
   * @route '/home/:feed/:article'
   * @scope {Model} Article The `Article` model.
   */
  this.controller('ArticleCtrl', function($scope, Article, ArticleList) {
    $scope.Article = Article;
    $scope.ArticleList = ArticleList;

    Article.read(Article.article.id);
  });

}).call(angular.module('feeder.controllers', []));
