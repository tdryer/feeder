(function(angular) {

  var services = angular.module('feeder.services', []);

  services.factory('UserService', function($q, $cookieStore, Restangular) {
    var User = angular.noop
      , cookieKey = 'auth';

    function genAuth(username, password) {
      return btoa(username + ':' + password);
    }

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

    User.prototype.login = function(username, password) {
      var auth = genAuth(username, password);

      Restangular = Restangular.withConfig(function(RestangularProvider) {
        RestangularProvider.setDefaultHeaders({
          Authorization: 'xBasic ' + auth
        });
      });

      return Restangular.one('').get().then(function(result) {
        $cookieStore.put(cookieKey, auth);
      }, function(reason) {
        return $q.reject(reason);
      });
    };

    User.prototype.logout = function() {
      $cookieStore.remove(cookieKey);
    }

    User.prototype.isLoggedIn = function() {
      return !!$cookieStore.get(cookieKey);
    }

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

    return new User;
  });

}).call(this, angular);
