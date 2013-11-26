(function() {

  /**
   * The `State` model represents the overall state and status of the entire
   * application.
   *
   * @factory
   * @var {Boolean} [error=false] Has the application encountered an error?
   * @var {Boolean} [loading=false] Is the application is loading something?
   * @var {String} [message=''] A message to display to the user.
   */
  this.factory('State', function() {
    return {
      error: false,
      loading: false,
      message: ''
    }
  });

  /**
   * The `User` model represents the current visitor.
   *
   * @factory
   * @var {Boolean} authenticated Is the visitor authenticated?
   * @var {String} authorization The authorization token of the current user.
   * @var {Function} getAuthHeader Creates the header needed to make API calls.
   * @var {Function} login Logs the current visitor in.
   * @var {Function} logout Logs the current visitor out.
   * @var {Function} register Creates a user for the current visitor.
   * @var {String} username The username of the user.
   */
  this.factory('User', function($q, $cookieStore, Restangular) {
    var authKey = 'auth'
      , usernameKey = 'username';

    /**
     * Generates a header object that needs to be used by every other service to
     * make their API calls.
     *
     * @param {String} [auth=this.authorization] The authorization token.
     * @returns {Object} Returns the header object.
     */
    function getAuthHeader(auth) {
      auth || (auth = this.authorization);

      return {
        Authorization: 'xBasic ' + auth
      };
    }

    /**
     * Logs in a visitor by checking the server to see if the he or she exists
     * and if the username and password pair matches.
     *
     * @param {String} username The username of the visitor.
     * @param {String} password The password of the visitor.
     * @returns {Promise} Returns the promise of the login API hit.
     */
    function login(username, password) {
      var auth = btoa(username + ':' + password)
        , header = getAuthHeader(auth);

      return Restangular.one('users').get({}, header).then(_.bind(function() {
        this.authenticated = true;
        this.username = username;
        $cookieStore.put(authKey, auth);
        $cookieStore.put(usernameKey, username);
      }, this), $q.reject);
    };

    /**
     * Registers a new user.
     *
     * @param {String} username The username of the new user.
     * @param {String} password The password of the new user.
     * @returns {Promise} Returns the promise of the registration API hit.
     */
    function register(username, password) {
      return Restangular.all('users').post({
        username: username,
        password: password
      }).then(_.bind(function(result) {
        this.authenticated = true;
        this.username = username;
        $cookieStore.put(authKey, btoa(username + ':' + password));
        $cookieStore.put(usernameKey, username);
      }, this), $q.reject);
    }

    /**
     * Logs out a user by deleting the session cookie.
     */
    function logout() {
      this.authenticated = false;
      this.username = '';
      $cookieStore.remove(authKey);
      $cookieStore.remove(usernameKey);
    }

    return {
      authenticated: !!$cookieStore.get(authKey),
      authorization: $cookieStore.get(authKey),
      getAuthHeader: getAuthHeader,
      login: login,
      logout: logout,
      register: register,
      username: $cookieStore.get(usernameKey)
    };
  })

  .factory('Articles', function($q, User, Article, Restangular) {
    function get(id) {
      if (!id) {
        return $q.reject();
      }

      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders(User.getAuthHeader());
      });

      return Restangular.one('feeds', id).getList('entries').then(function(result) {
        return Article.get(result.entries).then(function(result) {
          return result.entries;
        }, $q.reject);
      }, $q.reject);
    }

    return {
      get: get
    };
  })

  .factory('Article', function($q, User, Restangular) {


    function get(id) {
      if (!id) {
        return $q.reject();
      }

      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders(User.getAuthHeader());
      });

      return Restangular.one('entries').getList(id);
    }

    function status(id, read_status) {
      if (!id || (read_status != 'read' && read_status != 'unread')) {
        return $q.reject();
      }

      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders(User.getAuthHeader());
      });

      return Restangular.one('entries', id).patch({
        status: read_status
      });
    }

    return {
      get: get,
      status: status
    };
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

    function add(URL) {
      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders(User.getAuthHeader());
      });

      return Restangular.all('feeds').post({
        url: URL
      });
    }

    function get() {
      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders(User.getAuthHeader());
      });

      return Restangular.all('feeds').getList().then(function(result) {
        return result.feeds;
      }, $q.reject);
    }

    return {
      add: add,
      get: get
    };
  });

}).call(angular.module('feeder.services', []));
