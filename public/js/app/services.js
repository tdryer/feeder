(function() {

  /**
   * The `State` model represents the overall state and status of the entire
   * application.
   *
   * @factory
   * @var {Boolean} [error=false] Has the application encountered an error?
   * @var {Boolean} [loading=false] Is the application is loading something?
   */
  this.factory('State', function() {
    return {
      error: false,
      loading: false
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
    var endpoint = Restangular.one('users')
      , authKey = 'auth'
      , usernameKey = 'username'
      , authenticated = !!$cookieStore.get(authKey)
      , authorization = $cookieStore.get(authKey)
      , username = $cookieStore.get(usernameKey);

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

      return endpoint.get({}, header).then(_.bind(function() {
        this.authenticated = true;
        this.authorization = auth;
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
      var auth = btoa(username + ':' + password);

      return endpoint.all('').post({
        username: username,
        password: password
      }).then(_.bind(function() {
        this.authenticated = true;
        this.authorization = auth;
        this.username = username;
        $cookieStore.put(authKey, auth);
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
      authenticated: authenticated,
      authorization: authorization,
      getAuthHeader: getAuthHeader,
      login: login,
      logout: logout,
      register: register,
      username: username
    };
  });

  /**
   * The `Feeds` model represents all the subscribed feeds of the user.
   *
   * @factory
   * @var {Function} update Fetches and stores the subscribed feeds of the user.
   * @var {Array} [feeds=[]] The feeds of the current user.
   * @var {Function} update Fetches and stores the subscribed feeds of the user.
   * @var {Function} remove Unsubscribes a feed.
   */
  this.factory('Feeds', function($q, User, Restangular) {
    var endpoint = Restangular.one('feeds')
      , feeds = [];

    /**
     * Adds a new feed to the list of subscribed feeds of the current user.
     *
     * @param {String} url The url of the feed.
     * @returns {Promise} Returns the promise of the add feed API hit.
     */
    function add(url) {
      var header = User.getAuthHeader();

      return endpoint.all('').post({
        url: url
      }, {}, header).then(_.bind(function() {
        return this.update();
      }, this));
    }

    /**
     * Removes a feed from the list of subscribed feeds of the current user.
     *
     * @returns {Promise} Returns the promise of the remove feed API hit.
     */
    function remove(id) {
      var header = User.getAuthHeader();

      return endpoint.one(id).remove({}, header).then(_.bind(function() {
        return this.update();
      }, this), $q.reject);
    }

    /**
     * Fetches the list of subscribed feeds of the current user, and stores it
     * within the current `Feeds` model.
     *
     * @returns {Promise} Returns the promise of the update feeds API hit.
     */
    function update() {
      var header = User.getAuthHeader();

      return endpoint.get({}, header).then(_.bind(function(result) {
        this.feeds = result.feeds;
        return result;
      }, this), $q.reject);
    }

    return {
      add: add,
      feeds: feeds,
      remove: remove,
      update: update
    };
  });

  this.factory('Articles', function($q, User, Article, Restangular) {
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
  });

}).call(angular.module('feeder.services', []));
