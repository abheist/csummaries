'use strict';

/**
 * @ngdoc overview
 * @name aboutApp
 * @description
 * # aboutApp
 *
 * Main module of the application.
 */
angular
    .module('ClimateSummaries', [
        'ngResource'
    ])
    .controller('MainCtrl', ['$http', '$scope', function($http, $scope) {
        $http.get('data/weather.json').success(function(data) {
            $scope.dataset = data;
        });
    }]);
