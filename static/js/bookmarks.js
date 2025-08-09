// Bookmarks Module - Bookmarks functionality
visionApp.controller('BookmarksController', ['$scope', '$http', function($scope, $http) {
    // Initialize bookmarks variables
    $scope.bookmarks = [];
    $scope.filteredBookmarks = [];
    $scope.bookmarksLoading = false;
    $scope.searchQuery = '';
    
    // Load bookmarks data
    function loadBookmarks() {
        $scope.bookmarksLoading = true;
        console.log('Loading bookmarks...');
        
        $http.get('/api/bookmarks')
            .then(function(response) {
                $scope.bookmarks = response.data.bookmarks || [];
                $scope.filteredBookmarks = $scope.bookmarks;
                $scope.bookmarksLoading = false;
                console.log('Bookmarks loaded successfully:', $scope.bookmarks.length, 'items');
                console.log('Bookmarks data:', response.data);
            })
            .catch(function(error) {
                console.error('Error loading bookmarks:', error);
                $scope.bookmarksLoading = false;
                $scope.bookmarks = [];
                $scope.filteredBookmarks = [];
            });
    }
    
    // Search bookmarks with fuzzy matching
    $scope.searchBookmarks = function() {
        if (!$scope.searchQuery || $scope.searchQuery.trim() === '') {
            $scope.filteredBookmarks = $scope.bookmarks;
            return;
        }
        
        // Use server-side fuzzy search
        $http.get('/api/bookmarks/search?q=' + encodeURIComponent($scope.searchQuery.trim()))
            .then(function(response) {
                $scope.filteredBookmarks = response.data.bookmarks || [];
                console.log('Search results:', response.data);
            })
            .catch(function(error) {
                console.error('Error searching bookmarks:', error);
                // Fallback to showing all bookmarks
                $scope.filteredBookmarks = $scope.bookmarks;
            });
    };
    
    // Clear search
    $scope.clearSearch = function() {
        $scope.searchQuery = '';
        $scope.filteredBookmarks = $scope.bookmarks;
    };
    
    // Initialize bookmarks on controller load
    loadBookmarks();
    
    // Expose loadBookmarks function for external calls
    $scope.loadBookmarks = loadBookmarks;
}]);