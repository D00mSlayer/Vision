// Vision App AngularJS Application
angular.module('visionApp', [])
.controller('MainController', ['$scope', '$http', '$interval', function($scope, $http, $interval) {
    // Initialize scope variables
    $scope.environmentData = {};
    $scope.healthStatus = {};
    $scope.loading = true;
    $scope.error = null;
    $scope.refreshing = false;
    $scope.lastUpdated = new Date();
    
    // Load environment data
    function loadEnvironmentData() {
        $scope.loading = true;
        $scope.error = null;
        
        $http.get('/api/environments')
            .then(function(response) {
                $scope.environmentData = response.data;
                $scope.loading = false;
                $scope.lastUpdated = new Date();
                console.log('Environment data loaded:', response.data);
            })
            .catch(function(error) {
                $scope.error = 'Failed to load environment data';
                $scope.loading = false;
                console.error('Error loading environment data:', error);
            });
    }
    
    // Load health status
    function loadHealthStatus() {
        $http.get('/api/health')
            .then(function(response) {
                $scope.healthStatus = response.data;
                console.log('Health status updated:', response.data);
            })
            .catch(function(error) {
                console.error('Error loading health status:', error);
            });
    }
    
    // Get health status class for styling
    $scope.getHealthClass = function(key) {
        if (!$scope.healthStatus.hasOwnProperty(key)) {
            return 'health-checking';
        }
        return $scope.healthStatus[key] ? 'health-up' : 'health-down';
    };
    
    // Get health status text
    $scope.getHealthText = function(key) {
        if (!$scope.healthStatus.hasOwnProperty(key)) {
            return 'Checking...';
        }
        return $scope.healthStatus[key] ? 'Online' : 'Offline';
    };
    
    // Refresh health status manually
    $scope.refreshHealth = function() {
        $scope.refreshing = true;
        
        $http.get('/api/health/check')
            .then(function(response) {
                $scope.healthStatus = response.data.health;
                $scope.lastUpdated = new Date();
                $scope.refreshing = false;
                console.log('Health status refreshed:', response.data);
            })
            .catch(function(error) {
                console.error('Error refreshing health status:', error);
                $scope.refreshing = false;
            });
    };
    
    // Initialize the application
    function init() {
        loadEnvironmentData();
        loadHealthStatus();
        
        // Set up automatic health status updates every 30 seconds
        $interval(function() {
            loadHealthStatus();
        }, 30000);
    }
    
    // Start the application
    init();
}]);
