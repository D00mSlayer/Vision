// Vision Monitor Controller - Full Screen Display
angular.module('visionApp', [])
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{{');
    $interpolateProvider.endSymbol('}}');
})
.controller('MonitorController', function($scope, $http, $interval, $timeout) {
    // Initialize data
    $scope.environmentData = null;
    $scope.healthStatus = {};
    $scope.healthStats = {
        environments: { up: 0, total: 0 },
        microservices: { up: 0, total: 0 },
        databases: { up: 0, total: 0 }
    };
    $scope.error = null;
    $scope.lastUpdate = new Date();

    // Auto-scroll configuration
    var scrollIntervals = {};

    // Load environment data
    function loadEnvironmentData() {
        $http.get('/api/environments')
            .then(function(response) {
                $scope.environmentData = response.data;
                $scope.error = null;
                console.log('Environment data loaded:', $scope.environmentData);
                
                // Initialize auto-scrolling for environments with 20+ microservices
                $timeout(function() {
                    initializeAutoScroll();
                }, 1000);
            })
            .catch(function(error) {
                console.error('Error loading environment data:', error);
                $scope.error = 'SYSTEM ERROR: Failed to load environment data';
            });
    }

    // Load health status
    function loadHealthStatus() {
        $http.get('/api/health')
            .then(function(response) {
                $scope.healthStatus = response.data;
                $scope.lastUpdate = new Date();
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

    // Get service health class for environment summary
    $scope.getServiceHealthClass = function(services) {
        if (!services || services.length === 0) return 'health-checking';
        
        var healthy = 0;
        services.forEach(function(service) {
            if ($scope.healthStatus['ms_' + service.server_url]) {
                healthy++;
            }
        });

        if (healthy === services.length) return 'health-up';
        if (healthy === 0) return 'health-down';
        return 'health-checking';
    };

    // Get database health class for environment summary
    $scope.getDatabaseHealthClass = function(databases) {
        if (!databases || databases.length === 0) return 'health-checking';
        
        var healthy = 0;
        databases.forEach(function(db) {
            if ($scope.healthStatus['db_' + db.host + ':' + db.port + '/' + db.database_name]) {
                healthy++;
            }
        });

        if (healthy === databases.length) return 'health-up';
        if (healthy === 0) return 'health-down';
        return 'health-checking';
    };

    // Get healthy service count
    $scope.getHealthyCount = function(services, prefix) {
        if (!services) return 0;
        var count = 0;
        services.forEach(function(service) {
            if ($scope.healthStatus[prefix + service.server_url]) {
                count++;
            }
        });
        return count;
    };

    // Get healthy database count
    $scope.getHealthyDbCount = function(databases) {
        if (!databases) return 0;
        var count = 0;
        databases.forEach(function(db) {
            if ($scope.healthStatus['db_' + db.host + ':' + db.port + '/' + db.database_name]) {
                count++;
            }
        });
        return count;
    };

    // Initialize auto-scrolling for environments with many services
    function initializeAutoScroll() {
        // Clear existing intervals
        Object.keys(scrollIntervals).forEach(function(key) {
            clearInterval(scrollIntervals[key]);
        });
        scrollIntervals = {};

        if (!$scope.environmentData) return;

        $scope.environmentData.product_versions.forEach(function(product, productIndex) {
            product.environments.forEach(function(env, envIndex) {
                if (env.microservices && env.microservices.length >= 20) {
                    var elementId = 'services-' + productIndex + '-' + envIndex;
                    var element = document.getElementById(elementId);
                    
                    if (element) {
                        var serviceItems = element.querySelector('.service-items');
                        if (serviceItems) {
                            var scrollPosition = 0;
                            var maxScroll = serviceItems.scrollWidth - element.clientWidth;
                            
                            scrollIntervals[elementId] = setInterval(function() {
                                scrollPosition += 200; // Scroll 200px every 8 seconds
                                
                                if (scrollPosition >= maxScroll) {
                                    scrollPosition = 0; // Reset to beginning
                                }
                                
                                element.scrollTo({
                                    left: scrollPosition,
                                    behavior: 'smooth'
                                });
                            }, 8000); // Scroll every 8 seconds
                        }
                    }
                }
            });
        });
    }

    // Cleanup intervals on destroy
    $scope.$on('$destroy', function() {
        Object.keys(scrollIntervals).forEach(function(key) {
            clearInterval(scrollIntervals[key]);
        });
    });

    // Initialize the application
    loadEnvironmentData();
    loadHealthStatus();

    // Set up periodic health updates (every 30 seconds)
    $interval(loadHealthStatus, 30000);

    // Reinitialize auto-scroll when data changes
    $scope.$watch('environmentData', function(newVal, oldVal) {
        if (newVal && newVal !== oldVal) {
            $timeout(function() {
                initializeAutoScroll();
            }, 1000);
        }
    });
});