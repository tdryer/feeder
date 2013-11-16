(function(angular) {

  angular.module('feeder.services', [])

  /**
   * Creates a `User` model.
   *
   * @factory
   * @var {Function} User `User` constructor.
   * @var {String} cookieKey The identifier for the user cookie.
   * @var {Function} genAuth Creates a base64 encoding of the username/password.
   */
  .factory('User', function($q, $cookieStore, Restangular) {
    var User = angular.noop
      , cookieKey = 'auth';

    function genAuth(username, password) {
      return btoa(username + ':' + password);
    }

    /**
     * Registers a new user.
     *
     * @param {String} username The new user's username.
     * @param {String} password The new user's password.
     * @returns {Promise} Returns the promise of the registration API hit.
     */
    User.prototype.register = function(username, password) {
      return Restangular.all('users').post({
        username: username,
        password: password
      }).then(function(result) {
        $cookieStore.put(cookieKey, genAuth(username, password));
      }, function(reason) {
        return $q.reject(reason);
      });
    }

    /**
     * Logs in a user by checking the server to see if the user exists and the
     * password matches.
     *
     * @param {String} username The user's username.
     * @param {String} password The user's password.
     * @returns {Promise} Returns the promise of the login API hit.
     */
    User.prototype.login = function(username, password) {
      var auth = genAuth(username, password);

      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders({
          Authorization: 'xBasic ' + auth
        });
      });

      return Restangular.one('users').get().then(function(result) {
        $cookieStore.put(cookieKey, auth);
      }, function(reason) {
        return $q.reject(reason);
      });
    };

    /**
     * Logs out a user by deleting the session cookie.
     */
    User.prototype.logout = function() {
      $cookieStore.remove(cookieKey);
    }

    /**
     * Checks to see if an user is logged in.
     *
     * @returns {Boolean} Returns whether or not a user is currently logged in.
     */
    User.prototype.isLoggedIn = function() {
      return !!$cookieStore.get(cookieKey);
    }

    /**
     * Returns the current user's username by checking the server.
     *
     * @returns {Promise} Returns the promise of the API hit.
     */
    User.prototype.getUsername = function() {
      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders({
          Authorization: 'xBasic ' + $cookieStore.get(cookieKey)
        });
      });

      return Restangular.one('users').get().then(function(result) {
        return result.username;
      }, function(reason) {
        return $q.reject(reason);
      });
    }

    User.prototype.getAuth = function() {
      return $cookieStore.get(cookieKey);
    }

    return new User;
  })

  .factory('Articles', function($q, User, Restangular) {
    var Articles = angular.noop;

    Restangular = Restangular.withConfig(function(RestangularProvider) {
      RestangularProvider.setDefaultHeaders({
        Authorization: 'xBasic ' + User.getAuth()
      });
    });

    return new Articles;
  })

  /**
   * Creates a `User` model.
   *
   * @factory
   * @var {Function} User `User` constructor.
   * @var {String} cookieKey The identifier for the user cookie.
   * @var {Function} genAuth Creates a base64 encoding of the username/password.
   */
  .factory('Feeds', function($q, User, Restangular) {
    var Feeds = angular.noop;

    Restangular = Restangular.withConfig(function(RestangularProvider) {
      RestangularProvider.setDefaultHeaders({
        Authorization: 'xBasic ' + User.getAuth()
      });
    });

    Feeds.prototype.add = function(URL) {
      return Restangular.all('feeds').post({
        url: URL
      });
    }

    Feeds.prototype.get = function() {
      return Restangular.all('feeds').getList().then(function(result) {
        return result.feeds;
      }, function(reason) {
        $q.reject(reason);
      });
    }

    return new Feeds;
  });

}).call(this, angular);
