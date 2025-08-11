angular.module('visionApp', [])
.controller('MainController', ['$scope', '$http', '$interval', '$location', function($scope, $http, $interval, $location) {
    
    $scope.config = {};
    $scope.environmentData = {};
    $scope.healthStatus = {};
    $scope.bookmarks = [];
    $scope.filteredBookmarks = [];
    $scope.loading = true;
    $scope.bookmarksLoading = false;
    $scope.refreshing = false;
    $scope.error = null;
    $scope.lastUpdated = new Date();
    $scope.currentView = 'environments';
    $scope.previewMode = false;
    let autoScrollInterval = null;

    $scope.activeSqlDb = null;
    $scope.sqlEditor = {
        query: '',
        results: null,
        error: null,
        isLoading: false
    };
    let sqlEditorModal = null;

    // =================================================================
    // DATA LOADING
    // =================================================================
    const loadDashboardData = function() {
        return $http.get('/api/dashboard_data').then(function(response) {
            $scope.environmentData = response.data.environments;
            $scope.healthStatus = response.data.health;
            $scope.lastUpdated = new Date();
            $scope.loading = false;
            $scope.refreshing = false;
        }).catch(function(err) {
            $scope.error = 'Failed to load dashboard data.';
            $scope.loading = false;
            $scope.refreshing = false;
            console.error('Dashboard data load error:', err);
        });
    };

    const loadEnvironmentData = function() {
        $http.get('/api/environments').then(function(response) {
            $scope.environmentData = response.data;
            $scope.loading = false;
        }).catch(function(err) {
            $scope.error = 'Failed to load environment data.';
            $scope.loading = false;
            console.error('Environment load error:', err);
        });
    };

    const loadHealthStatus = function() {
        $http.get('/api/health').then(function(response) {
            $scope.healthStatus = response.data;
            $scope.lastUpdated = new Date();
            $scope.refreshing = false;
        }).catch(function(err) {
            console.error('Health status load error:', err);
            $scope.refreshing = false;
        });
    };

    const loadBookmarks = function() {
        $scope.bookmarksLoading = true;
        $http.get('/api/bookmarks').then(function(response) {
            $scope.bookmarks = response.data.bookmarks || [];
            $scope.filteredBookmarks = $scope.bookmarks;
            $scope.bookmarksLoading = false;
        }).catch(function(err) {
            console.error('Bookmarks load error:', err);
            $scope.bookmarksLoading = false;
        });
    };

    // =================================================================
    // SQL EDITOR MANAGEMENT (ADD THIS ENTIRE SECTION)
    // =================================================================
    $scope.openSqlEditor = function(database) {
        $scope.activeSqlDb = database;

        $scope.sqlEditor.results = null;
        $scope.sqlEditor.error = null;
        $scope.sqlEditor.isLoading = false;
        
        $scope.sqlEditor.query = 'SELECT TOP 100 name, create_date, modify_date\nFROM sys.tables\nORDER BY modify_date DESC;';

        if (!sqlEditorModal) {
            sqlEditorModal = new bootstrap.Modal(document.getElementById('sqlEditorModal'));
        }
        sqlEditorModal.show();
    };

    $scope.executeQuery = function() {
        if (!$scope.activeSqlDb || !$scope.sqlEditor.query) {
            return;
        }

        $scope.sqlEditor.isLoading = true;
        $scope.sqlEditor.results = null;
        $scope.sqlEditor.error = null;
        const startTime = new Date().getTime();

        const payload = {
            db_config: $scope.activeSqlDb,
            query: $scope.sqlEditor.query
        };

        $http.post('/api/db/execute', payload).then(function(response) {
            const data = response.data;
            if (data.success) {
                $scope.sqlEditor.results = data;
                $scope.sqlEditor.results.executionTime = new Date().getTime() - startTime;
                
                $scope.sqlEditor.query = data.executedQuery;

            } else {
                $scope.sqlEditor.error = data.error;
                if (data.executedQuery) {
                    $scope.sqlEditor.query = data.executedQuery;
                }
            }
            $scope.sqlEditor.isLoading = false;
        }).catch(function(err) {
            $scope.sqlEditor.error = err.data.error || 'A server error occurred.';
            $scope.sqlEditor.isLoading = false;
        });
    };

    // =================================================================
    // FULLSCREEN MANAGEMENT
    // =================================================================
    const enterFullScreen = function() {
        const elem = document.documentElement;
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.mozRequestFullScreen) { /* Firefox */
            elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { /* IE/Edge */
            elem.msRequestFullscreen();
        }
    };

    const exitFullScreen = function() {
        if (document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement) {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.mozCancelFullScreen) { /* Firefox */
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) { /* Chrome, Safari and Opera */
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { /* IE/Edge */
                document.msExitFullscreen();
            }
        }
    };

    
    document.addEventListener('fullscreenchange', function() {
        if (!document.fullscreenElement) {
            $scope.$apply(function() {
                if ($scope.previewMode) {
                    $scope.setViewMode('detailed');
                }
            });
        }
    });

    // =================================================================
    // HEALTH STATUS HELPERS
    // =================================================================
    $scope.getHealthClass = function(key) {
        if (!$scope.healthStatus.hasOwnProperty(key)) {
            return 'fas fa-spinner fa-spin health-checking';
        }
        return 'fas fa-circle ' + ($scope.healthStatus[key] ? 'health-up' : 'health-down');
    };

    $scope.getHealthText = function(key) {
        if (!$scope.healthStatus.hasOwnProperty(key)) {
            return '';
        }
        return $scope.healthStatus[key] ? 'Online' : 'Offline';
    };

    $scope.getMicroserviceUrlWithPort = function(serverUrl, port) {
        try {
            const url = new URL(serverUrl);
            return `${url.protocol}//${url.hostname}:${port}${url.pathname}`;
        } catch (e) {
            return serverUrl;
        }
    };

    // =================================================================
    // VIEW MANAGEMENT & ACTIONS
    // =================================================================
    $scope.setView = function(view) {
        $scope.currentView = view;

        if (view !== 'environments') {
            stopAutoScroll();
            exitFullScreen();
        }

        if (view === 'bookmarks' && $scope.bookmarks.length === 0) {
            loadBookmarks();
        }
    };
    
    $scope.setViewMode = function(mode) {
        $scope.previewMode = (mode === 'monitor');
        if ($scope.previewMode) {
            enterFullScreen();
            startAutoScroll();
        } else {
            exitFullScreen();
            stopAutoScroll();
        }
    };

    $scope.refreshHealth = function() {
        $scope.refreshing = true;
        loadDashboardData();
    };

    // =================================================================
    // DASHBOARD CALCULATION HELPERS (ADD THIS ENTIRE SECTION)
    // =================================================================

    $scope.getOverallStats = function() {
        let online = 0, offline = 0, total = 0, environments = 0;
        
        if (!$scope.environmentData.product_versions) {
            return { online: 0, offline: 0, environments: 0, uptime: 0 };
        }
        
        $scope.environmentData.product_versions.forEach(function(product) {
            product.environments.forEach(function(env) {
                environments++;
                
                const envKey = 'env_' + env.url;
                if ($scope.healthStatus.hasOwnProperty(envKey)) {
                    total++;
                    if ($scope.healthStatus[envKey]) online++; else offline++;
                }
                
                (env.microservices || []).forEach(function(ms) {
                    const msKey = 'ms_' + ms.server_url;
                    if ($scope.healthStatus.hasOwnProperty(msKey)) {
                        total++;
                        if ($scope.healthStatus[msKey]) online++; else offline++;
                    }
                });
                
                (env.databases || []).forEach(function(db) {
                    const dbKey = 'db_' + db.host + ':' + db.port + '/' + db.database_name;
                    if ($scope.healthStatus.hasOwnProperty(dbKey)) {
                        total++;
                        if ($scope.healthStatus[dbKey]) online++; else offline++;
                    }
                });
            });
        });
        
        const uptime = total > 0 ? Math.round((online / total) * 100) : 0;
        return { online, offline, environments, uptime };
    };
    
    $scope.getProductHealthScore = function(product) {
        let online = 0, total = 0;
        
        (product.environments || []).forEach(function(env) {
            const envKey = 'env_' + env.url;
            if ($scope.healthStatus.hasOwnProperty(envKey)) {
                total++;
                if ($scope.healthStatus[envKey]) online++;
            }
            
            (env.microservices || []).forEach(function(ms) {
                const msKey = 'ms_' + ms.server_url;
                if ($scope.healthStatus.hasOwnProperty(msKey)) {
                    total++;
                    if ($scope.healthStatus[msKey]) online++;
                }
            });
            
            (env.databases || []).forEach(function(db) {
                const dbKey = 'db_' + db.host + ':' + db.port + '/' + db.database_name;
                if ($scope.healthStatus.hasOwnProperty(dbKey)) {
                    total++;
                    if ($scope.healthStatus[dbKey]) online++;
                }
            });
        });
        
        return total > 0 ? Math.round((online / total) * 100) : 100;
    };

    // =================================================================
    // MONITOR MODE AUTO-SCROLL
    // =================================================================
    const startAutoScroll = function() {
        stopAutoScroll();
        autoScrollInterval = $interval(function() {
            const isAtBottom = (window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100;
            if (isAtBottom) {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                const scrollAmount = window.innerHeight * ($scope.config.monitorScrollPercentage || 0.8);
                window.scrollBy({ top: scrollAmount, behavior: 'smooth' });
            }
        }, $scope.config.monitorScrollIntervalMs || 8000);
    };

    const stopAutoScroll = function() {
        if (autoScrollInterval) {
            $interval.cancel(autoScrollInterval);
            autoScrollInterval = null;
        }
    };

    $scope.$on('$destroy', stopAutoScroll);

    // =================================================================
    // APP INITIALIZATION
    // =================================================================
    const init = function() {
        console.log("Initializing Vision Dashboard Controller...");

        $http.get('/api/config').then(function(response) {
            $scope.config = response.data;
            console.log(`Polling for dashboard data every ${$scope.config.healthCheckIntervalMs / 1000} seconds.`);
            
            $interval(loadDashboardData, $scope.config.healthCheckIntervalMs);

        }).catch(function(err) {
            console.error("Could not fetch app config. Defaulting to 15s poll interval.", err);
            $scope.config.healthCheckIntervalMs = 15000;
            $interval(loadDashboardData, $scope.config.healthCheckIntervalMs);
        });

        loadDashboardData().then(function() {
            const params = $location.search();
            if (params.mode === 'monitor') {
                console.log("Starting in Monitor Mode via URL parameter.");
                $scope.setViewMode('monitor');
            }
        });
    };

    init();
}]);
