(function(angular, moment) {

  var filters = angular.module('feeder.filters', []);

  /**
   * Exposes the power of Moment.js parsing and formatting.
   *
   * @filter
   * @param {*} date The date to parse.
   * @param {String} [format='LLL'] The format to format `date` with.
   * @returns {String} Returns `date` in the format `format`.
   */
  filters.filter('moment', function() {
    return function(date, format) {
      //format || (format = 'LLL');

      if (angular.isNumber(date)) {
        date = moment.unix(date);
      } else {
        date = moment(date);
      }

      return date.format(format);
    }
  });

}).call(this, angular, moment);
