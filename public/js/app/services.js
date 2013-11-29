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
   * @var {Array|Boolean} [feeds=false] The feeds of the current user.
   * @var {Function} id Returns a feed with a specific id.
   * @var {Number} [unreads=0] The total number of unreads in all the feeds.
   * @var {Function} update Fetches and stores the subscribed feeds of the user.
   * @var {Function} remove Unsubscribes a feed.
   */
  this.factory('Feeds', function($q, User, Restangular) {
    var endpoint = Restangular.one('feeds')
      , feeds = false
      , unreads = 0;

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
     * Returns the feed object with id `id`.
     *
     * @param {String|Number} id The id of the feed.
     * @returns {Object} Returns the feed object with id `id`.
     */
    function id(id) {
      id = parseInt(id, 10);

      if (!this.feeds) {
        return;
      }

      return _.find(this.feeds, {
        id: id
      });
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
        var feeds = result.feeds;

        this.feeds = feeds;
        this.unreads = _.reduce(feeds, function(unreads, feed) {
          return unreads + feed.unreads;
        }, 0);

        return result;
      }, this), $q.reject);
    }

    return {
      add: add,
      feeds: feeds,
      id: id,
      remove: remove,
      unreads : unreads,
      update: update
    };
  });

  /**
   * The `ArticleList` model represents the list of articles for the feed that
   * the user is currently viewing.
   *
   * @factory
   * @var {Number} [id=0] The id of the feed parent of the article list.
   * @var {Array|Boolean} [list=false] The list of articles.
   * @var {Function} push Adds to the article list, or update an article in it.
   * @var {Function} update Fetches and stores the article ids of a feed.
   */
  this.factory('ArticleList', function($q, Restangular, User, Article) {
    var endpoint = Restangular.one('feeds')
      , filter = null
      , id = 0
      , list = false
      , unreads = 0;

    function push() {
      var list = this.list
        , updatedArticle = Article.article;

      if (!updatedArticle) {
        return;
      }

      list = _.each(list, function(article, key) {
        if (article.id === updatedArticle.id) {
          list[key].read = updatedArticle.read;
        }
      });

      this.list = list;
    }

    function update(id) {
      var header = User.getAuthHeader()
        , entriesEndpoint = endpoint.one(id).getList('entries', {}, header);

      return entriesEndpoint.then(_.bind(function(result) {
        return Article.get(result.entries, {
          truncate: 300
        }).then(_.bind(function(result) {
          this.id = id;
          this.list = result.entries;
        }, this), $q.reject);
      }, this), $q.reject);
    }

    return {
      id: id,
      list: list,
      push: push,
      update: update
    };
  });

  /**
   * The `Article` model represents the list of articles for the feed that
   * the user is currently viewing.
   *
   * @factory
   * @var {Object|Boolean} [article=false] The article.
   * @var {Function} get Fetches and stores an article.
   * @var {Function} read Reads an article.
   * @var {Function} unread Unreads an article.
   * @var {Function} update Fetches and stores the article ids of a feed.
   */
  this.factory('Article', function($q, User, Restangular) {
    var endpoint = Restangular.one('entries')
      , article = false;

    function get(id, queryParams) {
      queryParams || (queryParams = {});
      return endpoint.getList(id, queryParams, User.getAuthHeader());
    }

    function update(id) {
      return this.get(id).then(_.bind(function(result) {
        this.article = result.entries.pop();
      }, this), $q.reject);
    }

    function read(id) {
      return endpoint.one(id).patch({
        read: true
      }, {}, User.getAuthHeader()).then(_.bind(function(result) {
        this.article.read = true;
      }, this), $q.reject);
    }

    function unread(id) {
      return endpoint.one(id).patch({
        read: false
      }, {}, User.getAuthHeader()).then(_.bind(function(result) {
        this.article.read = false;
      }, this), $q.reject);
    }

    return {
      article: article,
      get: get,
      read: read,
      unread: unread,
      update: update
    };
  });

}).call(angular.module('feeder.services', []));
