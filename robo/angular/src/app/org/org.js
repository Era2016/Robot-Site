angular.module('bolt.org', [
    'bolt',
    'ui.router',
    'ngResource',
    'restmod',
    'ngMaterial',
])

.config(function config($stateProvider) {
    $stateProvider
        .state('org', {
            url: '/org',
            views: {
                'main': {
                    templateUrl: 'org/org.tpl.html',
                    controller: ''
                }
            },
            data: {
                pageTitle: 'Organization'
            }
        })
        .state('org.list', {
            url: '/list',
            views: {
                'org': {
                    templateUrl: 'org/list.tpl.html',
                    controller: 'OrgController',
                },
            }
        })
        .state('org.create', {
            url: '/new',
            views: {
                'org': {
                    templateUrl: 'org/new.tpl.html',
                    controller: 'OrgController',
                },
            }
        })
        .state('org.profile', {
            url: '/:id',
            views: {
                'org': {
                    templateUrl: 'org/profile.tpl.html',
                    controller: 'OrgController',
                },
            },
            params: {
                org: null
            }
        });
})

/**
 * And of course we define a controller for our route.
 */
.controller('OrgController', function OrgController($scope, $location, $http,
    $log, $state, $stateParams, GlobalService, AuthUser, Job, Organization, Message, Mixin, Utils){

// sets the service GlobalServive object to an object in the $scope
// so it is accessible by the view.

    angular.extend($scope, Mixin.PaginationMixin);
    angular.extend($scope, Mixin.RestErrorMixin);
    
    $scope.globals = GlobalService;
    
// initializes the currentOrg and error objects

    $scope.orgProfile = {};
    $scope.orgProfilePicture = {};
    $scope.errors = {};

    $scope.observeRestErrorEvents(Organization);
    $scope.observePaginationEvents(Organization);

    $scope.$watch('orgProfilePicture', function() {
        if ($scope.orgProfilePicture && $scope.orgProfilePicture.$error) {
            Message.showToast('File too large ' + Math.round($scope.orgProfilePicture.size / 100000) / 10 +
                ' MB: max ' + $scope.orgProfilePicture.$errorParam + '', 'error', $scope);
        }
    });

    $scope.enableEdit = function() {
        $scope.editMode = true;
        $scope.saveSuccessMsg = null;
        $scope.orgProfileBackup = Utils.copyModelInfo($scope.orgProfile);
    };

    $scope.cancelEdit = function() {
        Utils.restoreModelInfo($scope.orgProfile, $scope.orgProfileBackup);
        $scope.orgProfileBackup = null;
        $scope.editMode = false;
    };

// loads organizations into the view. modelUtils, so regular get is req

    $scope.loadOrgs = function(pageNumber) {
        $scope.orgs = Organization.$collection().$refresh({page: pageNumber || 1});
    };

    $scope.saveOrg = function() {
        $scope.orgProfile.$save().$then(function() {
            $scope.editMode = false;
            $scope.OrgProfileBackup = null;
            Message.showToast('Your profile information was saved successfully', 'success');
        });
    };

// loads one organization into the view, using the orgID
    $scope.loadDetails = function(org, id) {
      $scope.orgProfilePicture = null;
      $scope.orgProfile = Organization.$find(id);

    };

    $scope.setOrgPicture = function(pic) {

        if ($scope.orgProfilePicture && !$scope.orgProfilePicture.$error) {
            $scope.orgProfile.$setProfilePicture($scope.orgProfilePicture)
                .$then(function() {
                  $scope.orgProfilePicture = null;
                });
        }
    };

// passes organization that is clicked into the currentOrg $scope var
// and reloads the organizations (is this necessary?)

    $scope.selectOrg = function(org) {
        $scope.orgProfile = org;
    };

// saves the organization using the org object and passes back errors
// if any are found

    $scope.createOrg = function() {
        $scope.currentOrg = Organization.$create($scope.currentOrg).$then(function() {
            $scope.viewOrg($scope.currentOrg);
        });
    };

// this changes the state to the organization detail...

    $scope.viewOrg = function(org) {
        $state.go('org.profile', {org:org,id: org.id});
    };

    $scope.viewJobs = function(org) {
        $log.log(org);
        $state.go('jobs.list', {org:org,id: org.id});
    };

// deletes the organization and then removes the item from
// the scope in order

    $scope.delOrg = function(org) {

    org.$destroy();

    };

// this determines which functions to run when the page loads
    
    switch ($state.current.name) {
        case 'org.profile':
            $scope.loadDetails($state.params.org,$state.params.id);
            break;

        case 'org.list':
            $scope.loadOrgs();
            break;
        case 'org.create':
            break;
    }


}); // end of OrgController

