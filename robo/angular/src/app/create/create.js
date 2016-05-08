/**
 * Each section of the site has its own module. It probably also has
 * submodules, though this boilerplate is too simple to demonstrate it. Within
 * `src/app/home`, however, could exist several additional folders representing
 * additional modules that would then be listed as dependencies of this one.
 * For example, a `note` section could have the submodules `note.create`,
 * `note.delete`, `note.edit`, etc.
 *
 * Regardless, so long as dependencies are managed correctly, the build process
 * will automatically take take of the rest.
 *
 * The dependencies block here is also where component dependencies should be
 * specified, as shown below.
 */
angular.module( 'bolt.create', [
  'bolt',
  'ui.router',
  'ngResource',
  'restmod'
])

/**
 * Each section or module of the site can also have its own routes. AngularJS
 * will handle ensuring they are all available at run-time, but splitting it
 * this way makes each module more "self-contained".
 */
.config(function config( $stateProvider ) {
  $stateProvider
  .state('create',{url:'/create',
      views: {'main':{ templateUrl: 'create/create.tpl.html',controller: ''}
      },
      data:{ pageTitle: 'Create' }
    })
  .state('create.pitch',{url:'/pitch',
      views: {'create':{templateUrl: 'create/pitch.tpl.html',controller: 'CreateController',},
      }})
  .state('create.note',{url:'/note',
      views: {'create':{templateUrl: 'create/note.tpl.html',controller: 'CreateController',},
      }})         
  ;
})

/**
 * And of course we define a controller for our route.
 */
.controller('CreateController', function CreateController($scope, $location, $http,
    $log, $state, $stateParams, GlobalService,AuthUser, Organization){

// sets the service GlobalServive object to an object in the $scope
// so it is accessible by the view.

    $scope.globals = GlobalService;
    
// initializes the currentOrg and error objects



}); // end of CreateController

