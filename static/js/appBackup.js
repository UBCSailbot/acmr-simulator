        boatPathCoords.push(currentPos);

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
        setTimeout( function() { windPath.setMap(null) }, 1000 );

        // Calculate True Wind Angle
        var twa_rad = $scope.coords[2] * Math.PI/180.0;

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