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
angular.module( 'bolt.briefs', [
  'bolt',
  'ui.router',
  'ngResource',
  'restmod',
  'ui.utils.masks'
])

/**
 * Each section or module of the site can also have its own routes. AngularJS
 * will handle ensuring they are all available at run-time, but splitting it
 * this way makes each module more "self-contained".
 */
.config(function config( $stateProvider ) {
  $stateProvider
  .state('briefs',{url:'/briefs',
      views: {'main':{ templateUrl: 'briefs/briefs.tpl.html',controller: ''}
      },
      data:{ pageTitle: 'Briefs' }
    })
  .state('briefs.new',{url:'/new',
      views: {'briefs':{ templateUrl: 'briefs/new.tpl.html',controller: 'BriefController',},
      }})
  ;
})

/**
 * And of course we define a controller for our route.
 */
.controller('BriefController', function BriefController($scope, $log, $state,
    $stateParams, $interval, $timeout, GlobalService, AuthUser, User, Mixin,
    Brief, Task, Enum) {

    angular.extend($scope, Mixin.RestErrorMixin);
    $scope.observeRestErrorEvents(Brief);

    $scope.globals = GlobalService;
    $scope.Enum = Enum;
    $scope.errors = {};

    $scope.brief = {categories:[], keywords:[]};
    $scope.tasks = [];
    $scope.userOrganizations = [];
    $scope.categories = [];

    $scope.observeRestErrorEvents(Brief);

    var autoSaveTimeout;
    var autoSaveObjects = [];
    $scope.autoSaving = false;
    $scope.lastSaveTime = null;

    Brief.addObserverHooks($scope, {
        'after-request-error': function() {
            var errors = this.$response.data;
            if (errors.hasOwnProperty('tasks')) {
                $.each(errors['tasks'], function(i, task_errors) {
                    var id = task_errors.id;
                    var task = $.grep($scope.tasks, function(task) {
                        return task.id == id;
                    })[0];
                    task.$setErrors(task_errors);
                    if (task_errors.hasOwnProperty('job'))
                        task.job.$setErrors(task_errors['job'][0]);
                });
            }
        }
    });

    $scope.loadUserOrganizations = function() {

        $scope.userOrganizations = $scope.currentUser.orgs.$resolve();
        return $scope.userOrganizations;

    };

    $scope.loadCategories = function() {
        $scope.categories = Enum.Category.values.slice();
        $scope.$watch('brief.category', function(category) {
          if ($.inArray(category, $scope.categories) != -1)
            $scope.brief.categories = [category];
        });
    };

    $scope.addTask = function() {
        task = $scope.brief.tasks.$build({type: Enum.TaskType.WRITING}).$save();
        $scope.autoSaveTask(task);
        $scope.tasks.push(task);
    };

    $scope.deleteTask = function(task) {
        $scope.tasks = $.grep($scope.tasks, function(_task) {
            return _task != task;
        });
        task.$destroy().$error(function() {
            $scope.tasks.push(task);
        });
    };

    $scope.createJob = function(task) {
        task.job = task.jobs.$build({}).$save();
        $scope.autoSaveJob(task.job);
    };

    $scope.autoSaveBrief = function() {
        var autoSave = $scope.createAutoSave($scope.brief);

        // watch individual fields is usually better in performance
        // than watching the whole object
        $scope.$watch('brief.title', autoSave);
        $scope.$watch('brief.deadline', autoSave);
        $scope.$watch('brief.organization', autoSave);
        $scope.$watchCollection(('brief.keywords'), autoSave);
        $scope.$watchCollection('brief.categories', autoSave);
    };

    $scope.autoSaveTask = function(task) {
        var autoSave = $scope.createAutoSave(task);
        $scope.$watch(function() { return task.deadline; }, autoSave);
        $scope.$watch(function() { return task.description; }, autoSave);
        $scope.$watch(function() { return task.goal; }, autoSave);
        $scope.$watch(function() { return task.contentType; }, autoSave);
        $scope.$watch(function() { return task.style; }, autoSave);
        $scope.$watch(function() { return task.pointOfView; }, autoSave);
        $scope.$watch(function() { return task.wordCount; }, autoSave);
    };

    $scope.autoSaveJob = function(job) {
        var autoSave = $scope.createAutoSave(job);
        $scope.$watch(function() { return job.closingDate; }, autoSave);
        $scope.$watch(function() { return job.price; }, autoSave);
        // Changed
        //console.log("Here ran");
        //$scope.$watch(function() {return job.canView;}, autoSave);
    };

    $scope.createAutoSave = function(object) {
        return function autoSave(oldValue, newValue) {
            var changed = newValue != oldValue;
            if (angular.isDate(oldValue) && angular.isDate(newValue))
                changed = newValue.getTime() != oldValue.getTime();
            if (changed) {
                if ($.inArray(object, autoSaveObjects) == -1)
                    autoSaveObjects.push(object);
                if (autoSaveTimeout)
                    $timeout.cancel(autoSaveTimeout);
                autoSaveTimeout = $timeout($scope.performAutoSave, 1000);
            }
        };
    };

    $scope.performAutoSave = function() {
        if (autoSaveObjects.length) {
            $scope.autoSaving = true;
            var autoSaveCount = 0;
            $.each(autoSaveObjects, function(i, obj) {
                autoSaveCount++;
                obj.$backgroundSave().$then(function() {
                    if (!--autoSaveCount) {
                        $scope.autoSaving = false;
                        $scope.lastSaveTime = Date.now();
                    }
                });
            });
        }
        $scope.stopAutoSave();
    };

    $scope.stopAutoSave = function() {
        autoSaveObjects = [];
        if (autoSaveTimeout) {
            $timeout.cancel(autoSaveTimeout);
            autoSaveTimeout = null;
        }
    };

    $scope.publishBrief = function() {
        $scope.performAutoSave();
        $scope.brief.$then(function() {
            $scope.brief.published = true;
            $scope.brief.$save();
        });
        $state.go('jobs.detail',{job:task.job,id:task.job.id});
    };

    switch ($state.current.name) {
        case 'briefs.new':
            $scope.loadCategories();
            $scope.loadUserOrganizations();
            $scope.brief = Brief.$build($scope.brief).$save();
            $scope.autoSaveBrief();

            break;
    }
});
