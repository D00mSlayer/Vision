// Vision Dashboard Controller - Detailed View
angular.module('visionApp', [])
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{{');
    $interpolateProvider.endSymbol('}}');
})
.controller('MainController', function($scope, $http, $interval) {
    // Initialize data
    $scope.environmentData = null;
    $scope.healthStatus = {};
    $scope.healthStats = {
        environments: { up: 0, total: 0 },
        microservices: { up: 0, total: 0 },
        databases: { up: 0, total: 0 }
    };
    $scope.error = null;

    // Load environment data
    function loadEnvironmentData() {
        $http.get('/api/environments')
            .then(function(response) {
                $scope.environmentData = response.data;
                $scope.error = null;
                console.log('Environment data loaded:', $scope.environmentData);
            })
            .catch(function(error) {
                console.error('Error loading environment data:', error);
                $scope.error = 'Failed to load environment data. Please refresh the page.';
            });
    }

    // Load health status
    function loadHealthStatus() {
        $http.get('/api/health')
            .then(function(response) {
                $scope.healthStatus = response.data;
                calculateHealthStats();
                console.log('Health status updated:', $scope.healthStatus);
            })
            .catch(function(error) {
                console.error('Error loading health status:', error);
            });
    }

    // Calculate health statistics
    function calculateHealthStats() {
        $scope.healthStats = {
            environments: { up: 0, total: 0 },
            microservices: { up: 0, total: 0 },
            databases: { up: 0, total: 0 }
        };

        if (!$scope.environmentData) return;

        $scope.environmentData.product_versions.forEach(function(product) {
            product.environments.forEach(function(env) {
                // Count environments
                $scope.healthStats.environments.total++;
                if ($scope.healthStatus['env_' + env.url]) {
                    $scope.healthStats.environments.up++;
                }

                // Count microservices
                if (env.microservices) {
                    env.microservices.forEach(function(service) {
                        $scope.healthStats.microservices.total++;
                        if ($scope.healthStatus['ms_' + service.server_url]) {
                            $scope.healthStats.microservices.up++;
                        }
                    });
                }

                // Count databases
                if (env.databases) {
                    env.databases.forEach(function(db) {
                        $scope.healthStats.databases.total++;
                        if ($scope.healthStatus['db_' + db.host + ':' + db.port + '/' + db.database_name]) {
                            $scope.healthStats.databases.up++;
                        }
                    });
                }
            });
        });
    }

    // Get health class for styling
    $scope.getHealthClass = function(key) {
        if (key.startsWith('environments') || key.startsWith('microservices') || key.startsWith('databases')) {
            var stat = $scope.healthStats[key];
            if (stat && stat.total > 0) {
                if (stat.up === stat.total) return 'health-up';
                if (stat.up === 0) return 'health-down';
                return 'health-checking';
            }
            return 'health-checking';
        }
        
        var status = $scope.healthStatus[key];
        if (status === true) return 'health-up';
        if (status === false) return 'health-down';
        return 'health-checking';
    };

    // Initialize the application
    loadEnvironmentData();
    loadHealthStatus();

    // Set up periodic health updates (every 30 seconds)
    $interval(loadHealthStatus, 30000);
});