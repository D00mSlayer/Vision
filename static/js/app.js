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
    $scope.previewMode = false;
    
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
    
    // Toggle preview mode
    $scope.togglePreviewMode = function() {
        $scope.previewMode = !$scope.previewMode;
        
        // Start auto-scroll when entering preview mode
        if ($scope.previewMode) {
            $scope.startAutoScroll();
        } else {
            $scope.stopAutoScroll();
        }
    };
    
    // Auto-scroll functionality for monitor display
    $scope.autoScrollInterval = null;
    
    $scope.startAutoScroll = function() {
        $scope.stopAutoScroll(); // Clear any existing interval
        
        $scope.autoScrollInterval = $interval(function() {
            // Smooth scroll down
            window.scrollBy({
                top: window.innerHeight * 0.8,
                behavior: 'smooth'
            });
            
            // Reset to top when reaching bottom
            setTimeout(function() {
                if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
                    window.scrollTo({
                        top: 0,
                        behavior: 'smooth'
                    });
                }
            }, 1000);
        }, 8000); // Scroll every 8 seconds
    };
    
    $scope.stopAutoScroll = function() {
        if ($scope.autoScrollInterval) {
            $interval.cancel($scope.autoScrollInterval);
            $scope.autoScrollInterval = null;
        }
    };
    
    // Clean up on destroy
    $scope.$on('$destroy', function() {
        $scope.stopAutoScroll();
    });
    
    // Calculate overall statistics for monitor display
    $scope.getOverallStats = function() {
        let online = 0, offline = 0, total = 0, environments = 0;
        
        if (!$scope.environmentData.product_versions) {
            return { online: 0, offline: 0, environments: 0, uptime: 0 };
        }
        
        $scope.environmentData.product_versions.forEach(function(product) {
            product.environments.forEach(function(env) {
                environments++;
                
                // Count environment URL
                const envKey = 'env_' + env.url;
                if ($scope.healthStatus.hasOwnProperty(envKey)) {
                    total++;
                    if ($scope.healthStatus[envKey]) online++;
                    else offline++;
                }
                
                // Count microservices
                if (env.microservices) {
                    env.microservices.forEach(function(ms) {
                        const msKey = 'ms_' + ms.server_url;
                        if ($scope.healthStatus.hasOwnProperty(msKey)) {
                            total++;
                            if ($scope.healthStatus[msKey]) online++;
                            else offline++;
                        }
                    });
                }
            });
        });
        
        const uptime = total > 0 ? Math.round((online / total) * 100) : 0;
        return { online, offline, environments, uptime };
    };
    
    // Calculate health score for a product
    $scope.getProductHealthScore = function(product) {
        let online = 0, total = 0;
        
        product.environments.forEach(function(env) {
            // Count environment URL
            const envKey = 'env_' + env.url;
            if ($scope.healthStatus.hasOwnProperty(envKey)) {
                total++;
                if ($scope.healthStatus[envKey]) online++;
            }
            
            // Count microservices
            if (env.microservices) {
                env.microservices.forEach(function(ms) {
                    const msKey = 'ms_' + ms.server_url;
                    if ($scope.healthStatus.hasOwnProperty(msKey)) {
                        total++;
                        if ($scope.healthStatus[msKey]) online++;
                    }
                });
            }
        });
        
        return total > 0 ? Math.round((online / total) * 100) : 0;
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
