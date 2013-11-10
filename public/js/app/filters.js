(function(angular) {

  var filters = angular.module('feeder.filters', []);
  filters.filter('format_date', function() {
    return function(input, format) {
      return moment.unix(input).format(format);
    }
  });

}).call(this, angular);
