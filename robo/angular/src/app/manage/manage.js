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
angular.module('bolt.manage', [
    'bolt',
    'ui.router',
    'ngResource',
    'restmod',
    'ui.calendar',
    'angularMoment',
])

/**
 * Each section or module of the site can also have its own routes. AngularJS
 * will handle ensuring they are all available at run-time, but splitting it
 * this way makes each module more "self-contained".
 */
.config(function config($stateProvider, $urlRouterProvider) {

    $urlRouterProvider.when('/manage', '/manage/dashboard');

    $stateProvider
        .state('manage', {
            url: '/manage',
            views: {
                'main': {
                    templateUrl: 'manage/manage.tpl.html',
                    controller: ''
                }
            },
            data: {
                pageTitle: 'Organizations'
            }
        })
        .state('manage.dashboard', {
            url: '/dashboard',
            views: {
                'manage': {
                    templateUrl: 'manage/dashboard.tpl.html',
                    controller: 'ManageController',
                },
            }
        })
        .state('manage.calendar', {
            url: '/cal',
            views: {
                'manage': {
                    templateUrl: 'manage/cal.tpl.html',
                    controller: 'ManageController',
                },
            }
        })
        .state('manage.payments', {
            url: '/payments',
            views: {
                'manage': {
                    templateUrl: 'manage/payments.tpl.html',
                    controller: 'ManageController',
                },
            }
        })
        .state('manage.analytics', {
            url: '/analytics',
            views: {
                'manage': {
                    templateUrl: 'manage/analytics.tpl.html',
                    controller: 'ManageController',
                },
            }
        });
})

/**
 * And of course we define a controller for our route.
 */
.controller('ManageController', function ManageController($scope, $document, $location, $http,
    $log, $state, $stateParams, moment, GlobalService, Social,
    AuthUser, Enum, Organization, Brief, Message, User, Mixin) {

    // Sets the service GlobalServive object to an object in the $scope
    // so it is accessible by the view.

    $scope.globals = GlobalService;
    $scope.Enum = Enum;
    $scope.tasks = {};
    $scope.eventSources = [{
        events: []
    }];
    $scope.activeTasks = [];
    $scope.inactiveTasks = [];
    $scope.finishedTasks = [];

    // temp dashboard variables

    $scope.dashboard = {
        org: {
            assigned: 29,
            assignedGoal: 47,
            completed: 33,
            completedGoal: 61,
            spent: 698,
            spentGoal: 980,
        },
        user: {
            assigned: 11,
            assignedGoal: 24,
            completed: 7,
            completedGoal: 10,
            spent: 170,
            spentGoal: 310,
        },
    };

    // renders the list of events in the calendar view
    // called automatically through ui-calendar

    // Hide calendar buttons if a user is accessing it
    // No access to the generated HTML, need to use jQuery/jqLite
    // to hide that style

    // if($scope.currentUser.role == 'writer') {
    //   $log.log('writer!');
    //   angular.element($('.fc-orgButton-button').css('display','none'));
    //   angular.element($('.fc-userButton-button').css('display','none'));
    // }




    $scope.renderEvent = function(event, element, view) {
        element.find('.fc-time').after("<br/>");
        element.find('.fc-title').after("<div class='progress-meter'><div class='progress-bar' style='width:" + event.finishedTaskCount / event.taskCount * 100.0 + "%'>" + event.status + "<span class='progress-indicator'>" + event.finishedTaskCount + "/" + event.taskCount + "</span></div></div>");
    };

    $scope.dropEvent = function(event, element, view) {
        var movedEvent = Brief.$find(event.briefId).tasks.$find(event.taskId).$then(function() {
            movedEvent.deadline = event.start._d;
            movedEvent.$save(['deadline']);
        });
    };

    $scope.clickEvent = function(event, element, view) {
        $state.go('assignments.edit', {
            assignment: null,
            id: event.briefId
        });
    };

    $scope.payTest = function() {
        $state.go('manage.payments');
    };

    $scope.loadOrgTasks = function() {
        // Removes the events without having to reinitialize
        // or refresh the calendar or dashboard
        $scope.inactiveTasks.splice(0, $scope.inactiveTasks.length);
        $scope.activeTasks.splice(0, $scope.activeTasks.length);
        $scope.finishedTasks.splice(0, $scope.finishedTasks.length);

        // Removes the event sources when switching types
        $scope.eventSources[0].events.splice(0, $scope.eventSources[0].events.length);

        if ($scope.currentOrg) {
            $scope.tasks = $scope.currentOrg.tasks.$refresh().$then(function() {

                $scope.inactiveTasks.splice(0, $scope.inactiveTasks.length);
                $scope.activeTasks.splice(0, $scope.inactiveTasks.length);
                $scope.finishedTasks.splice(0, $scope.inactiveTasks.length);

                var len = $scope.tasks.length;
                for (var i = 0; i < len; i++) {

                    if (!$scope.tasks[i].assignee){
                      $scope.tasks[i].assignee = {picture:''};
                      $scope.tasks[i].assignee.picture = 'http://lorempixel.com/50/50/people/2';
                    }

                    // Divides the tasks fo the dashboard view
                    if ($scope.tasks[i].status.id == 1) {
                        // inactive
                        $scope.inactiveTasks.push($scope.tasks[i]);
                    } else if ($scope.tasks[i].status.id == 2) {
                        // active
                        $scope.activeTasks.push($scope.tasks[i]);
                    } else if ($scope.tasks[i].status.id == 3) {
                        // finished
                        $scope.finishedTasks.push($scope.tasks[i]);
                    }

                    // Pushes the tasks into the predefined calendar event structure
                    var task = $scope.tasks[i];
                    var taskDate = (task.status.id == 3
                                    ? task.modified
                                    : task.deadline || '2015-10-01');
                    $scope.eventSources[0].events.push({
                        title: $scope.tasks[i].taskBrief.title,
                        start: taskDate,
                        //allDay: true,
                        status: $scope.tasks[i].status.label,
                        taskCount: $scope.tasks[i].taskBrief.taskCount,
                        finishedTaskCount: $scope.tasks[i].taskBrief.finishedTaskCount,
                        taskId: $scope.tasks[i].id,
                        briefId: $scope.tasks[i].taskBrief.id,
                        task: $scope.tasks[i],
                        stick: true,
                        editable: task.status.id != 3,
                    });
                }
            }).$then(function() {
                // For troublshoot purposes
                //$log.log($scope.eventSources[0]);
            });

        }
    };

    // Fetches any Tasks
    $scope.loadTasks = function() {

        // Removes the events without having to reinitialize
        // or refresh the calendar or dashboard
        $scope.inactiveTasks.splice(0, $scope.inactiveTasks.length);
        $scope.activeTasks.splice(0, $scope.activeTasks.length);
        $scope.finishedTasks.splice(0, $scope.finishedTasks.length);

        // Removes the eventsources object when switching from Org to User
        $scope.eventSources[0].events.splice(0, $scope.eventSources[0].events.length);

        // Iterates through the task object and inputs it into the eventSources object
        // as well as splits up the tasks into task type for presentation simplicity
        $scope.tasks = $scope.currentUser.tasks.$refresh().$then(function() {
            var len = $scope.tasks.length;
            for (var i = 0; i < len; i++) {

                if (!$scope.tasks[i].assignee){
                  $scope.tasks[i].assignee = {picture:''};
                  $scope.tasks[i].assignee.picture = $scope.currentUser.picture;
                }

                // Divides the tasks fo the dashboard view
                if ($scope.tasks[i].status.id == 1) {
                    // inactive
                    $scope.inactiveTasks.push($scope.tasks[i]);
                } else if ($scope.tasks[i].status.id == 2) {
                    // active
                    $scope.activeTasks.push($scope.tasks[i]);
                } else if ($scope.tasks[i].status.id == 3) {
                    // finished
                    $scope.finishedTasks.push($scope.tasks[i]);
                }

                // Pushes the task object elements into the event object
                var task = $scope.tasks[i];
                    var taskDate = (task.status.id == 3
                                    ? task.modified
                                    : task.deadline || '2015-10-01');
                $scope.eventSources[0].events.push({
                    title: $scope.tasks[i].taskBrief.title,
                    start: taskDate,
                    //allDay: true,
                    status: $scope.tasks[i].status.label,
                    taskCount: $scope.tasks[i].taskBrief.taskCount,
                    finishedTaskCount: $scope.tasks[i].taskBrief.finishedTaskCount,
                    taskId: $scope.tasks[i].id,
                    briefId: $scope.tasks[i].taskBrief.id,
                    task: $scope.tasks[i],
                    stick: true,
                    editable: task.status.id != 3
                });
            }
        }).$then(function() {
            // for troubleshooting
            //$log.log($scope.eventSources);
        });
    };


                // if($scope.tasks[i].assignee) {
                //   User.$find(id).$then(function() {
                //   $scope.tasks[i].userPicture =  this.picture;
                //   });

                // } else {
                //   return 'http://lorempixel.com/50/50/people/2';
                // }

    // initializes the currentOrg and error objects

    $scope.showMsg = function(message, type) {
        Message.showToast(message, type);
    };

    // Sets up the UI-Calender with FullCalender features
    $scope.uiConfig = {
        calendar: {
            selectable: false,
            editable: true,
            height: 'auto',
            customButtons: {
                orgButton: {
                    text: 'Organization',
                    click: function() {
                        $scope.loadOrgTasks();
                    }
                },
                userButton: {
                    text: 'User',
                    click: function() {
                        $scope.loadTasks();
                    }
                }
            },
            header: {
                left: 'prev,next orgButton userButton',
                center: 'title',
                right: 'month,agendaWeek'
            },

            eventRender: $scope.renderEvent,
            eventDataTransform: $scope.transformData,
            eventClick: $scope.clickEvent,
            dayClick: $scope.clickDay,
            eventDrop: $scope.dropEvent
        }
    };

    // Determines which functions to run when the page loads

    $scope.viewAssignment = function(brief,id) {
      $state.go('assignments.edit', {brief:brief,id:id});
    };

    switch ($state.current.name) {
        case 'manage.dashboard':
            $scope.loadTasks();
            break;
        case 'manage.calendar':
            $scope.loadTasks();
            break;


    }


}); // end of ManageController
