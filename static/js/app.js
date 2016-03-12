var app = angular.module("app", []);

// Wrap the entire thing with the controller.
app.controller('AppCtrl', function($scope, $http) {

    $http.get('http://127.0.0.1:5000/data').success(function (output) {

        // Initialize map options with center at starting point of boat
        $scope.coords = output;
        var latlng = new google.maps.LatLng($scope.coords[0], $scope.coords[1]);
        var mapOptions = {
            zoom: 15,
            center: latlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        // Create map with ID: "map_canvas"
        $scope.map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
        $scope.map.setOptions({scrollwheel:true})

        // Set coordinates of destination as a flag.
        $scope.marker = new google.maps.Marker({
            position: {lat: $scope.coords[5], lng: $scope.coords[6]},
            map: $scope.map,
            title: 'Current Position',
            icon: 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png'
        });
    });

    // Loop n times. (Eventually make this infinite.)
    var i = 0, n = 100;
    function f() {
        // Get new data in specified url.
        $http.get('http://127.0.0.1:5000/data').success(function (output) {
            $scope.coords = output;
            var latlng = new google.maps.LatLng($scope.coords[0], $scope.coords[1]);

            // Use this to recenter the simulation map on each update
            //$scope.map.setCenter(latlng)

            // Create marker for current position of boat.
            // TODO: Replace with more appropriate/informative marker.
            $scope.marker = new google.maps.Marker({
                position: latlng,
                map: $scope.map,
                title: 'Current Position'
            });

            // Create arrow symbol to add to polylines
            var lineSymbol = {
                path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
            };

            // Calculate True Wind Angle
            var twa_rad = $scope.coords[2]*Math.PI/180;

            // Erase previous True Wind polyline + arrow with delay of 1000ms
            setTimeout( function() { windPath.setMap(null);}, 1000 )

            // Create new polyline path for the True Wind.
            var windPath = new google.maps.Polyline({
                path: [new google.maps.LatLng($scope.coords[0]-0.015*Math.sin(twa_rad),
                           $scope.coords[1]-0.015*Math.cos(twa_rad)),
                       new google.maps.LatLng($scope.coords[0]-0.005*Math.sin(twa_rad),
                           $scope.coords[1]-0.005*Math.cos(twa_rad))],
                geodesic: true,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2,
                icons: [{icon: lineSymbol,
                        offset: '100%' }]
            });

            // Add True Wind polyline + arrow to the current map.
            windPath.setMap($scope.map);
        });

        i++;
        if (i < n ){
            setTimeout( f, 2000 );
        }
    }

    f();
})

