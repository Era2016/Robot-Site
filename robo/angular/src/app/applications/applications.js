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
angular.module( 'bolt.applications', [
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
  .state('applications',{url:'/applications',
      views: {'main':{ templateUrl: 'applications/applications.tpl.html',controller: ''}
      },
      data:{ pageTitle: 'Applications' }
    })
  .state('applications.new',{url:'/new',
      views: {'applications':{ templateUrl: 'applications/new.tpl.html',controller: 'ApplicationsController',},
      }})
  // application list for a jobId
  // this should be moved to jobs/#/application
  .state('applications.list',{url:'/:id/list',
      views: {'applications':{ templateUrl: 'applications/list.tpl.html',controller: 'ApplicationsController',},
      },
                              params:{job:{}, currentOrg:{}}
    })
  // application list that your applications
  .state('applications.userlist',{url:'/list',
      views: {'applications':{ templateUrl: 'applications/userlist.tpl.html',controller: 'ApplicationsController',},
      }})
  .state('applications.detail',{url:'/:jobId/:appId',
      views: {'applications':{ templateUrl: 'applications/detail.tpl.html',controller: 'ApplicationsController',},
      },
      params:{job:{},applicant:{}}
    })
  ;
})

/**
 * And of course we define a controller for our route.
 */
.controller('ApplicationsController', function ApplicationsController($scope, $location,
                                                                      $http, $log, $filter, $state, $stateParams, GlobalService,  OrganizationUser,AuthUser, Enum,
                                                                      Job, User, Mixin, Organization){

    angular.extend($scope, Mixin.RestErrorMixin);

    // sets the service GlobalServive object to an object in the $scope
    // so it is accessible by the view.

    $scope.globals = GlobalService;
    //GlobalService.user = AuthUser.getUser();
    // initializes the currentOrg and error objects

    $scope.errors = {};
    $scope.jobs = {};
    $scope.currentApplication = {};
    $scope.currentJob = {};
    $scope.applications = {};
    $scope.Enum = Enum;
    $scope.organizationUser = {};
    $scope.currentJob.id = $stateParams.jobId;
    $scope.observeRestErrorEvents(Job);
    $scope.employee = {};
    $scope.organization = {};
    $scope.currentUser = {};
    $scope.members = {}; // this notes the ids of all the members.

    $scope.loadJobs = function() {
        $scope.jobs = $scope.currentUser.jobs.$fetch();
    };

    $scope.loadApplications = function(job,id) {
      // Still needs to pull the applications even if pulling the job id
      if(job.id) {
         $scope.currentJob = job;
          $scope.applications = job.applications.$refresh().$then(function(response){
              console.log(response.creator);
              $scope.currentUser = User.$find(response.creator).$then(function(){
                  $scope.currentUser.orgs.$refresh().$then(function(){
                      //$scope.employee = $scope.currentUser.orgs.$getEmplyee();
                      $scope.organization = $scope.currentUser.orgs[0];
                      $scope.employee = $scope.organization.$getEmployee();
                      for(i in $scope.employee){
                          $scope.members[i.id] = i.username;
                      }
                  });
              });
          });
      } else {
          $scope.currentJob = Job.$find(id).$then(function(response){
              $scope.applications = $scope.currentJob.applications.$refresh();
              $scope.currentUser = User.$find(response.creator).$then(function(){
                  $scope.organization = $scope.currentUser.orgs.$refresh().$then(function(){
                      //console.log($scope.currentUser.orgs[0]);
                      console.log($scope.currentUser.orgs[0].tasks);
                      $scope.organization = $scope.currentUser.orgs[0];
                      $scope.employee =$scope.organization.$getEmployee().$then(function(){
                          console.log($scope.employee);
                          for(i in $scope.employee){
                              console.log(i);
                              $scope.members[i.id] = i.username;
                              console.log($scope.members.length);
                          }
                          console.log($scope.currentUser.id in $scope.members);
                      });

                  });
              });
         });
      }
        // end for loading
    };


    $scope.loadUserApplications = function() {
        // show user applications
         $scope.applications = $scope.currentUser.applications.$refresh();

    };


    $scope.viewProfile = function(user) {
        $state.go('user.profile', {user:user, id: user.id});
    };

    // removed this from the userlist
   $scope.viewOrgProfile = function(org) {
        $log.log('No organization is passed back right now.',org);
        //$state.go('orgs.detail', {org:org, id: org.id});
    };

   $scope.viewBrief = function(job, id) {
        $state.go('jobs.detail', {job:job,id: id});
        // job inside of applications is only the id
        //$state.go('jobs.detail', {job:job, id: job.id});
   };

    $scope.selectApplication = function(application) {
      var status = application.status;
      application.status = Enum.ApplicationStatus.ACCEPTED;
      application.$save().$success(function() {

        // All other candidates would be automatically rejected
        // We need to forward-reject while fetching to prevent
        // user from accepting another application
        $.each($scope.applications, function(application) {
          application.status = Enum.ApplicationStatus.REJECTED;
        });
        $scope.applications.$refresh();
      }).$error(function() {
        application.status = status;
      });
      $state.go('user.memberlist');
    };

    $scope.rejectApplication = function(application) {
      var status = application.status;
      application.status = Enum.ApplicationStatus.REJECTED;
      application.$save().$error(function() {
        application.status = status;
      });
    };

    $scope.hireFreelancer = function(application){


        var orgUser = new OrganizationUser();
        orgUser.user = application.applicant.id;
        orgUser.organization = $scope.currentUser.orgs[0].id;
        //var org = $scope.currentUser.orgs.$refresh();
        orgUser.userRole = 2;
        //orgUser.$pk = $scope.$pk;
        console.log(orgUser);
        orgUser.$save().$success(function(response){
            //console.log(response);

            // here add something to disable the button
        });

    };

    $scope.notInOrg = function(application){
        //console.log("Checking inside organization!");
        // suppose that the first organization inside the orgs of current user is the current org.
        //var applicant = User.$find(application.applicant.id);

        return true;
    }

    // This is implemented in assignments.userlist
    $scope.viewAssignment = function(brief,id) {
      // job
      $state.go('assignments.edit', {brief:brief,id:id});
    };

// this determines which functions to run when the page loads

    switch ($state.current.name) {
        case 'applications.detail':
            //$scope.loadDetails($stateParams.job,$stateParams.jobId,$stateParams.application,$stateParams.appId);
            break;

    case 'applications.list':
        $scope.loadApplications($stateParams.job,$stateParams.id);
            break;

        case 'applications.userlist':
            $scope.loadUserApplications();
            break;

        case 'applications.new':
            //$scope.loadOrgs();
            break;
    }

}); // end of JobController
