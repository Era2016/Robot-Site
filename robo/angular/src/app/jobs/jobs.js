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
angular.module( 'bolt.jobs', [
  'bolt',
  'ui.router',
  'ngResource',
  'restmod',
])

/**
 * Each section or module of the site can also have its own routes. AngularJS
 * will handle ensuring they are all available at run-time, but splitting it
 * this way makes each module more "self-contained".
 */

.config(function config( $stateProvider,$urlRouterProvider ) {

  // go to profile as default
  $urlRouterProvider.when('/jobs', '/assignments/list');


  $stateProvider
  .state('jobs',{url:'/jobs',
      views: {'main':{ templateUrl: 'jobs/jobs.tpl.html',controller: ''}
      },
      data:{ pageTitle: 'Jobs' }
    })
  .state('jobs.new',{url:'/new',
      views: {'jobs':{ templateUrl: 'jobs/new.tpl.html',controller: 'JobController',},
      }})
  .state('jobs.list',{url:'/list',
      views: {'jobs':{ templateUrl: 'jobs/list.tpl.html',controller: 'JobController',},
      }})
  .state('jobs.recs',{url:'/recs',
      views: {'jobs':{ templateUrl: 'jobs/recs.tpl.html',controller: 'JobController',},
      }})
  .state('jobs.detail',{url:'/:id',
      views: {'jobs':{ templateUrl: 'jobs/detail.tpl.html',controller: 'JobController',},
      },
      params: {job:{}},
    })
  .state('jobs.apply',{url:'/:id/apply',
      views: {'jobs':{ templateUrl: 'jobs/apply.tpl.html',controller: 'JobController',},
      }})
  ;
})

/**
 * And of course we define a controller for our route.
 */
.controller('JobController', function JobController($scope, $location,
    $http, $log, $filter, $state, $stateParams, AuthUser, Enum, GlobalService,
    Job, Message, Mixin, Task, User) {

    angular.extend($scope, Mixin.RestErrorMixin);
    // sets the service GlobalServive object to an object in the $scope
    // so it is accessible by the view.
    $scope.globals = GlobalService;

    // initializes the currentOrg and error objects
    $scope.errors = {};
    $scope.currentApp = {};
    $scope.currentJob = {categories: [], keywords:[]};
    $scope.categories = [];
    $scope.scroll = {busy:false};

    $scope.currentJobOwner = false;
    $scope.orgs = {};
    $scope.jobs = {};
    $scope.Enum = Enum;
    $scope.observeRestErrorEvents(Job);

    // filter for searching for teammates

    $scope.querySearch = function(query) {
      var results = query ? $scope.teammates.filter($scope.createFilterFor(query)) : [];
      return results;
    };
    $scope.selectedTeammate = [];
    $scope.filteredSelected = 'true';
    $scope.createFilterFor = function(query) {
      var lowercaseQuery = angular.lowercase(query);
      return function filterFn(contact) {
        var lowercaseName = angular.lowercase(contact.name);
        return (lowercaseName.indexOf(lowercaseQuery) != -1);
      };
    };

// loads the organizations that a particular user is connected to create a job

    $scope.loadOrgs = function() {
        $scope.orgs = $scope.currentUser.orgs.$fetch();
    };

    // Load all categories for user to choose to create a job
    $scope.loadCategories = function() {
        $scope.categories = Enum.Category.values.slice();
        $scope.$watch('currentJob.category', function(category) {
          if ($.inArray(category, $scope.categories) != -1)
            // if there were multiple categories (see brief)
            $scope.currentJob.categories = [category];
        });
    };

    //   // Ideally should add a listener to removal event of category
    //   // but md-chips do not have right now
    //   $scope.$watchCollection('currentJob.categories', function(categories) {
    //     $scope.categories = $.grep($scope.allCategories, function(category) {
    //       return $.inArray(category, $scope.currentJob.categories) == -1;
    //     });
    //   });
    // };

    // loads all of the jobs without any pagination

    $scope.loadJobs = function() {
        $scope.jobs = Job.$collection().$refresh();
    };

    $scope.loadMoreJobs = function(next) {
        if(next) {
            $scope.scroll.busy = true;
            var currentPage = $scope.jobs.$metadata.page;
            $scope.jobs.$fetch({page:currentPage+1}).$then(function(){
                $scope.scroll.busy = false;
            });
        }
    };

    $scope.loadOpenJobs = function() {
        $scope.jobs = $scope.currentUser.jobs.$refresh();
    };

// load job details into the scope, first checks to see if it is passed

    $scope.loadDetails = function(job,jobId) {
        // pull job information
        // if(job.id){
        //   $log.log(job);
        //   $scope.currentJob = job.$resolve(); // crashing at the moment
        //   $scope.jobCreator = User.$find($scope.currentJob.creator);
        // } else{
          $scope.currentJob = Job.$find(jobId).$then(function() {
              $scope.jobCreator = User.$find($scope.currentJob.creator).$then(function(){
                // pulls the job's creator
                if($scope.currentJob.creator == $scope.currentUser.id) {
                  $scope.currentJobOwner = true;
                }

              });
          });
        //}

        // determines if the current user has applied to this job (?)
        $scope.userApplicationLoaded = false;
        $scope.currentUser.applications.$search({job: jobId})
        .$then(function() {
          $scope.userApplicationLoaded = true;
          $scope.userApplication = this.length ? this[0] : null;
        });
    };

// this changes the state to the job detail page

    $scope.viewJob = function(job) {
        $state.go('jobs.detail', {job:job, id: job.id});
    };

    $scope.loadJobApplications = function(job) {
        $state.go('applications.list', {job:job, id: job.id});
    };

    $scope.saveJob = function() {
        if($scope.dateValidation()) {
            $scope.currentJob.organization= $scope.currentOrg.id;
            console.log($scope.currentJob.canView);
            var job = Job.$build($scope.currentJob);
            console.log(job);
            job.$save().$then(function(){
              $state.go('jobs.detail',{id:job.id});
          });
        }
    };

    $scope.loadOpenJobArticle = function() {
        $scope.jobs = $scope.currentUser.jobs.$refresh();
    };

    $scope.dateValidation = function(){
      var currentDay = GlobalService.day._d;
       var applicationClosing = $scope.currentJob.applicationClosingDate;
       var deadLine = $scope.currentJob.deadline;
       $scope.errors = {};
       var valid = true;

       if(currentDay > applicationClosing)
       {
        $scope.errors.applicationClosing = "Application closing date should be greater than current date.";
        valid = false;
       }
       if(currentDay > deadLine)
        {

          $scope.errors.deadline =  "Deadline date should be greater than current date.";
          valid = false;
       }
        if(applicationClosing > deadLine) // deadline change
        {
          $scope.errors.applicationClosingDeadline = "Please choose a date greater than or equal to application Closing Date.";
          valid = false;
        }
        return valid;
    };

    $scope.delJob = function(job,index) {
      job.$destroy();
    };

    $scope.loadApply = function(job){
        job.applications.$create({message: $scope.currentApp.message})
        .$then(function(application) {
          $scope.userApplication = application;
        });
    };


// this determines which functions to run when the page loads

    switch ($state.current.name) {
        case 'jobs.detail':
            $scope.loadDetails($stateParams.job,$stateParams.id);
            break;
        case 'jobs.list':
            switch ($scope.isOrg) {
                case 0:
                    $scope.loadJobs();
                    break;
                case 1:
                    $scope.loadOpenJobs();
                    break;
            }
            break;
        case 'jobs.new':
            $scope.loadOrgs();
            $scope.loadCategories();
            break;


    }

}); // end of JobController
