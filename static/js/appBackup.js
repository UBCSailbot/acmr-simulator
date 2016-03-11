/**
 * Created by lgarcia on 10/03/16.
 */

var app = angular.module("app", []);

//app.controller("AppCtrl", function($scope) {
//
//    var latlng = new google.maps.LatLng(35.7042995, 139.7597564);
//    var mapOptions = {
//        zoom: 8,
//        center: latlng,
//        mapTypeId: google.maps.MapTypeId.ROADMAP
//    };
//
//    $scope.map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
//
//})

app.controller('AppCtrl', function($scope, $http) {

    $http.get('http://127.0.0.1:5000/data').success(function (output) {

        $scope.coords = output;
        var latlng = new google.maps.LatLng($scope.coords[0], $scope.coords[1]);
        var mapOptions = {
            zoom: 14,
            center: latlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        $scope.map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

    });

    var i = 0, n = 100;
    function f() {
        $http.get('http://127.0.0.1:5000/data').success(function (output) {

            $scope.coords = output;
            var latlng = new google.maps.LatLng($scope.coords[0], $scope.coords[1]);

            $scope.marker = new google.maps.Marker({
                position: latlng,
                map: $scope.map,
                title: 'Current Position'
            });

        });

        i++;
        if (i < n ){
            setTimeout( f, 2000 );
        }
    }

    f();
})

