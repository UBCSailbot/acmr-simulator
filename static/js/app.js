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

        var flightPath = new google.maps.Polyline({
            path: [latlng, new google.maps.LatLng($scope.coords[0]+1, $scope.coords[1]+1)],
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 2
        });

        flightPath.setMap($scope.map);

        //var richMarkerContent = document.createElement('div')
        //
        //// arrow image
        //var arrowImage           = new Image();
        //arrowImage.src           = 'http://www.openclipart.org/image/250px/' +
        //                           'svg_to_png/Anonymous_Arrow_Down_Green.png';
        //// rotation in degree
        //var directionDeg         = 144 ;
        //
        //// create a container for the arrow
        //var rotationElement      = document.createElement('div');
        //var rotationStyles       = 'display:block;' +
        //                           '-ms-transform:      rotate(%rotationdeg);' +
        //                           '-o-transform:       rotate(%rotationdeg);' +
        //                           '-moz-transform:     rotate(%rotationdeg);' +
        //                           '-webkit-transform:  rotate(%rotationdeg);' ;
        //
        //// replace %rotation with the value of directionDeg
        //rotationStyles           = rotationStyles.split('%rotation').join(directionDeg);
        //
        //rotationElement.setAttribute('style', rotationStyles);
        //rotationElement.setAttribute('alt',   'arrow');
        //
        //// append image into the rotation container element
        //rotationElement.appendChild(arrowImage);
        //
        //// append rotation container into the richMarker content element
        //richMarkerContent.appendChild(rotationElement);
        //
        //// create a rich marker ("position" and "map" are google maps objects)
        //new RichMarker(
        //    {
        //        position    : latlng,
        //        map         : $scope.map,
        //        draggable   : false,
        //        flat        : true,
        //        anchor      : RichMarkerPosition.TOP_RIGHT,
        //        content     : richMarkerContent.innerHTML
        //    }
        //);
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

            var flightPath = new google.maps.Polyline({
                path: [new google.maps.LatLng($scope.coords[0], $scope.coords[1]),
                       new google.maps.LatLng($scope.coords[0]+0.1*Math.sin($scope.coords[3]/180*2*Math.PI),
                           $scope.coords[1]+0.1*Math.cos($scope.coords[3]/180*2*Math.PI))],
                geodesic: true,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2
            });

            flightPath.setMap($scope.map);

        });

        i++;
        if (i < n ){
            setTimeout( f, 2000 );
        }
    }

    f();
})

