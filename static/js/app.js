var app = angular.module("app", []);

// Wrap the entire thing with the controller.
app.controller('AppCtrl', function($scope, $http) {

    $http.get('http://127.0.0.1:5000/data').success(function (output) {

        // Initialize map options with center at starting point of boat
        $scope.coords = output;
        var latlng = new google.maps.LatLng($scope.coords[0], $scope.coords[1]);
        var mapOptions = {
            zoom: 16,
            center: latlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        // Create map with ID: "map_canvas"
        $scope.map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

        // Set coordinates of destination as a flag.
        $scope.marker = new google.maps.Marker({
            position: {lat: $scope.coords[5], lng: $scope.coords[6]},
            map: $scope.map,
            title: 'Destination',
            icon: 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png'
        });

        // Create marker for starting position of the boat.
        $scope.marker = new google.maps.Marker({
            position: latlng,
            map: $scope.map,
            title: 'Starting Position'
        });
    });

    // Create array of boat path coordinates to be used when creating the Polyline object
    var boatPathCoords = [];

    // Create X symbol to add to each boat position coordinate
    var crossSymbol = {
        path: 'M -2,-2 2,2 M 2,-2 -2,2',
        strokeColor: '#292',
        strokeWeight: 4
    };

    var dashSymbol = {
        path: 'M 0,-1 0,1',
        strokeOpacity: 1,
        scale: 4
    };

    var markerList = [];
    var bearingList = [];
    var trueWindList = [];
    var currentList = [];

    // Loop n times. (Eventually make this infinite.)
    var i = 0;
    var n = 100;

    function f() {
        // Get new data in specified url.
        $http.get('http://127.0.0.1:5000/data').success(function (output) {
            $scope.coords = output;

            var currentPos = new google.maps.LatLng($scope.coords[0], $scope.coords[1]);
            var destPos = new google.maps.LatLng($scope.coords[5], $scope.coords[6]);
            // Add current position LatLng object to array
            boatPathCoords.push(currentPos);

            // Create marker for current position
            var marker = new google.maps.Marker({
                position: currentPos,
                map: $scope.map,
                title: 'Current Position'
            });

            // Add marker to array
            markerList.push(marker);

            // Create Polyline object indicating boat path
            var boatPath = new google.maps.Polyline({
                path: boatPathCoords,
                strokeColor: "#0000FF",
                strokeOpacity: 1.0,
                strokeWeight: 2,
                icons: [{
                    icon: crossSymbol,
                    offset: '100%'
                }]
            });

            boatPath.setMap($scope.map);

            // Use this to recenter the simulation map on each update
            //$scope.map.setCenter(latlng)

            // Erase previous True Wind polyline + arrow with delay of 1000ms
            //setTimeout( function() { windPath.setMap(null) }, 1000 );

            // Calculate True Wind Angle
            var twa_rad = $scope.coords[2] * Math.PI/180.0;

            //Create arrow symbol to add to polylines
            var lineSymbol = {
                path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
            };

            // Create new polyline path for the True Wind.
            var windPath = new google.maps.Polyline({
                path: [new google.maps.LatLng($scope.coords[0] + 0.005 * Math.cos(twa_rad),
                    $scope.coords[1] + 0.005 * Math.sin(twa_rad)),
                    new google.maps.LatLng($scope.coords[0] + 0.001 * Math.cos(twa_rad),
                        $scope.coords[1] + 0.001 * Math.sin(twa_rad))],
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2,
                icons: [{
                    icon: lineSymbol,
                    offset: '100%'
                }]
            });

            // Push True Wind Polyline object to array for reference (to later be deleted)
            trueWindList.push(windPath);

            // Create desired bearing polyline + arrow
            var bearing = new google.maps.Polyline({
                path: [currentPos, destPos],
                strokeOpacity: 0,
                map: $scope.map,
                icons: [{
                  icon: dashSymbol,
                  offset: '0',
                  repeat: '20px'
                }]
            });

            bearingList.push(bearing);

            // TODO: Create polyline for current
            var currentSpeed = $scope.coords[7];
            var currentAngle_rad = $scope.coords[8] * Math.PI / 180.0;
            var currentPath = new google.maps.Polyline({
                path: [new google.maps.LatLng($scope.coords[0] + 0.002 * Math.cos(currentAngle_rad),
                    $scope.coords[1] + 0.002 * Math.sin(currentAngle_rad)),
                    new google.maps.LatLng($scope.coords[0] + 0.001 * Math.cos(currentAngle_rad),
                        $scope.coords[1] + 0.001 * Math.sin(currentAngle_rad))],
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2,
                icons: [{
                    icon: lineSymbol,
                    offset: '100%'
                }]
            });

            currentPath.setMap($scope.map);
            currentList.push(currentPath);

            // Create boat HOG polyline + arrow
            //var sow = $scope.coords[3];
            var hog_rad = $scope.coords[4] * Math.PI / 180.0;
            var boatDir = new google.maps.Polyline({
                path: [new google.maps.LatLng($scope.coords[0], $scope.coords[1]),
                       new google.maps.LatLng($scope.coords[0] + 0.0001*Math.cos(hog_rad),
                                            $scope.coords[1] + 0.0001*Math.sin(hog_rad))],
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2,
                icons: [{
                    icon: lineSymbol,
                    offset: '100%'
                }]
            });

            // Add True Wind and Boat Direction polyline + arrow to the current map.
            windPath.setMap($scope.map);
            boatDir.setMap($scope.map);
        });

        if ( i > 0 ){
            markerList.shift().setMap(null);
            trueWindList.shift().setMap(null);
            bearingList.shift().setMap(null);
            currentList.shift().setMap(null);
        }

        i++;

        if (i < n ){
            setTimeout( f, 2000 );
        }
    }

    f();
});

