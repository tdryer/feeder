(function() {

  /**
   * Exposes the power of Moment.js parsing and formatting.
   *
   * @filter
   * @param {*} date The date to parse.
   * @returns {String} Returns `date` as a Moment.js date object
   */
  this.filter('moment', function() {
    return function(date) {
      if (angular.isNumber(date)) {
        date = moment.unix(date);
      } else {
        date = moment(date);
      }

      return date;
    }
  });

  /**
   * Formats a Moment.js date object into a human-readable format
   *
   * @filter
   * @param {Object} date The Moment.js date object to parse.
   * @param {String} [format='LLLL'] The format to format `date` with.
   * @returns {String} Returns `date` in the format `format`.
   */
  this.filter('format', function() {
    return function(date, format) {
      format || (format = 'LLLL');

      return date.format(format);
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

  /**
   * Filters a list of articles to include recently read ones and ones
   * that match a given read status.
   *
   * @filter
   * @param {Object} data The list of Articles to filter.
   * @param {Object} filter The filter too apply to the list.
   */
  this.filter('filterArticles', function() {
    return function(data, filter) {
      var filtered = [];

      if (filter === null) {
        return data;
      }
      angular.forEach(data, function(current) {
        if (current.read === filter.read || _.indexOf(filter.ids, current.id) >= 0) {
          filtered.push(current);
        }
      });

      return filtered;
    }
  });

}).call(angular.module('feeder.filters', []));
