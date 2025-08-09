// Environments Module - Environment monitoring functionality  
visionApp.controller('EnvironmentsController', ['$scope', '$http', '$interval', function($scope, $http, $interval) {
    // Initialize environment variables
    $scope.environmentData = {};
    $scope.healthStatus = {};
    $scope.loading = true;
    $scope.error = null;
    $scope.refreshing = false;
    $scope.lastUpdated = new Date();
    $scope.previewMode = false;
    
    // Auto-scroll variables for monitor mode
    $scope.autoScrollEnabled = false;
    $scope.scrollPosition = 0;
    $scope.scrollInterval = null;
    
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
        return $scope.healthStatus[key] ? 'health-good' : 'health-bad';
    };
    
    // Get health status text
    $scope.getHealthText = function(key) {
        if (!$scope.healthStatus.hasOwnProperty(key)) {
            return 'Checking...';
        }
        return $scope.healthStatus[key] ? 'Healthy' : 'Down';
    };
    
    // Refresh health data manually
    $scope.refreshHealth = function() {
        $scope.refreshing = true;
        loadHealthStatus();
        setTimeout(function() {
            $scope.refreshing = false;
            $scope.$apply();
        }, 1000);
    };
    
    // Monitor mode functionality
    $scope.togglePreview = function() {
        $scope.previewMode = !$scope.previewMode;
        if ($scope.previewMode) {
            $scope.startAutoScroll();
        } else {
            $scope.stopAutoScroll();
        }
    };
    
    $scope.startAutoScroll = function() {
        if ($scope.scrollInterval) return;
        
        $scope.autoScrollEnabled = true;
        $scope.scrollInterval = setInterval(function() {
            var container = document.querySelector('.accordion');
            if (container) {
                $scope.scrollPosition += 2;
                if ($scope.scrollPosition >= container.scrollHeight - container.clientHeight) {
                    $scope.scrollPosition = 0;
                }
                container.scrollTop = $scope.scrollPosition;
            }
        }, 50);
    };
    
    $scope.stopAutoScroll = function() {
        if ($scope.scrollInterval) {
            clearInterval($scope.scrollInterval);
            $scope.scrollInterval = null;
        }
        $scope.autoScrollEnabled = false;
        $scope.scrollPosition = 0;
    };
    
    // Calculate environment health percentage
    $scope.getEnvironmentHealth = function(productVersions, envName) {
        var total = 0;
        var online = 0;
        
        // Count microservices health
        productVersions.forEach(function(pv) {
            pv.environments.forEach(function(env) {
                if (env.environment_name === envName) {
                    env.microservices.forEach(function(ms) {
                        const msKey = ms.service_url;
                        if ($scope.healthStatus.hasOwnProperty(msKey)) {
                            total++;
                            if ($scope.healthStatus[msKey]) online++;
                        }
                    });
                    
                    // Count database health
                    env.databases.forEach(function(db) {
                        const dbKey = 'db_' + db.host + ':' + db.port + '/' + db.database_name;
                        if ($scope.healthStatus.hasOwnProperty(dbKey)) {
                            total++;
                            if ($scope.healthStatus[dbKey]) online++;
                        }
                    });
                }
            });
        });
        
        return total > 0 ? Math.round((online / total) * 100) : 0;
    };
    
    // Calculate product health percentage
    $scope.getProductHealth = function(productVersion) {
        var total = 0;
        var online = 0;
        
        productVersion.environments.forEach(function(env) {
            // Count microservices
            env.microservices.forEach(function(ms) {
                const msKey = ms.service_url;
                if ($scope.healthStatus.hasOwnProperty(msKey)) {
                    total++;
                    if ($scope.healthStatus[msKey]) online++;
                }
            });
            
            // Count databases
            env.databases.forEach(function(db) {
                const dbKey = 'db_' + db.host + ':' + db.port + '/' + db.database_name;
                if ($scope.healthStatus.hasOwnProperty(dbKey)) {
                    total++;
                    if ($scope.healthStatus[dbKey]) online++;
                }
            });
        });
        
        return total > 0 ? Math.round((online / total) * 100) : 0;
    };
    
    // Initialize the environments module
    function init() {
        loadEnvironmentData();
        loadHealthStatus();
        
        // Set up automatic health status updates every 10 seconds
        $interval(function() {
            loadHealthStatus();
        }, 10000);
    }
    
    // Initialize on controller load
    init();
}]);