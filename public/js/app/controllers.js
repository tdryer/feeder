(function(angular, _) {

  angular.module('feeder.controllers', [])

  /**
   * The splash screen.
   *
   * @controller
   * @route '/'
   */
  .controller('IndexCtrl', function($scope, $location, User) {
    $scope.User = User;
  })

  /**
   * Displays a user's list of subscriptions.
   * Allows a user to add subscriptions.
   *
   * @controller
   * @route '/home'
   * @scope {Function} addFeed Adds a new feed.
   * @scope {String} newFeed The URL of the new feed to add.
   */
  .controller('HomeCtrl', function($scope, $location, Feeds) {

    $scope.updateFeeds = function() {
      $scope.loadingFeeds = true;
      Feeds.get().then(function(feeds) {
        $scope.subscriptions = feeds;
        $scope.loadingFeeds = false;
      });
    }

    $scope.addFeed = function() {
      Feeds.add($scope.newFeed).then(function(feeds) {
        $scope.updateFeeds();
      });
    }

    $scope.goToFeed = function(id) {
      $location.path('/home/' + id);
    }
  })

  /**
   * Displays a list of articles for a subscription.
   *
   * @controller
   * @route '/home/:feed'
   * @scope {Number} feedId The id of the current subscription.
   * @scope {Object} feed The data of the current subscription.
   */
  .controller('FeedCtrl', function($scope, $location, Feed, Articles) {

    $scope.feed = Feed;

    Articles.get(Feed.id).then(function(articles) {
      $scope.articles = articles;
    });

    $scope.goToArticle = function(feed_id, article_id) {
      $location.path('/home/' + feed_id + '/' + article_id);
    }
  })

  /**
   * Displays an article.
   *
   * @controller
   * @route '/home/:feed/:article'
   */
  .controller('ArticleCtrl', function($scope, $location, Article, data) {
    $scope.article = data;

    $scope.unread = function() {
      Article.status($scope.article.id, 'unread');
      $location.path('/home/' + $scope.article.feed_id);
    }

    Article.status($scope.article.id, 'read');
  })

  /**
   * Registers a new user.
   * Routes the user to their home page upon successful registration.
   *
   * @controller
   * @route '/register'
   */
  .controller('RegisterCtrl', function($scope, $location, $timeout, User) {
    var timeout;

    $scope.error = false;
    $scope.loading = false;

    $scope.register = function(username, password) {
      $timeout.cancel(timeout);

      $scope.loading = true;
      User.register(username, password).then(function() {
        $location.path('/home');
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
   * The login page.
   *
   * @controller
   * @route '/login'
   * @scope {Function} login Hits the authentication server on button click.
   * @scope {String} [username=''] Value of the username input field.
   * @scope {String} [password=''] Value of the password input field.
   * @scope {Boolean} [error=false] Does the login form have an error?
   */
  .controller('LoginCtrl', function($scope, $location, State, User) {
    $scope.username = '';
    $scope.password = '';
    $scope.error = false;

    $scope.login = function(username, password) {
      State.loading = true;
      State.error = false;
      User.login(username, password).then(function() {
        $location.path('/home');
      }, function() {
        State.loading = false;
        $scope.error = true;
      });
    }
  })

  /**
   * The logout page.
   *
   * @controller
   * @route '/logout'
   */
  .controller('LogoutCtrl', function($location, User) {
    User.logout();
    $location.path('/');
  });

}).call(this, angular, _);
