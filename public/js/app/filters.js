(function() {

  /**
   * Exposes the power of Moment.js parsing and formatting.
   *
   * @filter
   * @param {*} date The date to parse.
   * @param {String} [format='LLLL'] The format to format `date` with.
   * @returns {String} Returns `date` in the format `format`.
   */
  this.filter('moment', function() {
    return function(date, format) {
      format || (format = 'LLLL');

      if (angular.isNumber(date)) {
        date = moment.unix(date);
      } else {
        date = moment(date);
      }

      return date;
    }
  });

  /**
   * Converts a Moment.js date object into a human-readable from now format.
   *
   * @filter
   * @param {Object} date The Moment.js date object to parse.
   * @returns {String} Returns `date` in a human-readable format from now.
   */
  this.filter('fromNow', function() {
    return function(date) {
      return date.fromNow();
    }
  });

}).call(angular.module('feeder.filters', []));
