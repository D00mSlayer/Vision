// Main Vision App - Navigation and View Management
angular.module('visionApp', [])
.controller('MainController', ['$scope', function($scope) {
    // View management
    $scope.currentView = 'environments'; // Default to environments view
    
    // Set view and trigger appropriate controller actions
    $scope.setView = function(view) {
        console.log('Switching to view:', view);
        $scope.currentView = view;
        
        // Trigger specific actions based on view
        if (view === 'bookmarks') {
            // Let the BookmarksController handle its own initialization
            console.log('Bookmarks view activated');
        } else if (view === 'environments') {
            // Let the EnvironmentsController handle its own initialization
            console.log('Environments view activated');
        }
    };
}]);