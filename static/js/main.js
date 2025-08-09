// Main Vision App - Navigation and View Management
var visionApp = angular.module('visionApp', []);

visionApp.controller('MainController', ['$scope', function($scope) {
    // View management
    $scope.currentView = 'environments'; // Default to environments view
    
    // Set view and trigger appropriate controller actions
    $scope.setView = function(view) {
        console.log('Switching to view:', view);
        $scope.currentView = view;
        
        // Trigger specific actions based on view
        if (view === 'bookmarks') {
            console.log('Bookmarks view activated');
        } else if (view === 'environments') {
            console.log('Environments view activated');
        }
    };
}]);