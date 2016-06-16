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
    $scope.eventSources = [{
        events: []
    }];

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

    $scope.loadOrgTasks = function() {
        // Removes the events without having to reinitialize
        // or refresh the calendar or dashboard
        // I am keeping this in case any of you guys want to use it.
    };

    $scope.loadNotifications = function(){
        // you can modify this function
    };


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
                        $scope.loadNotifications();
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

    // modify later 
    switch ($state.current.name) {
        case 'manage.dashboard':
            //$scope.loadTasks();
            break;
        case 'manage.calendar':
            //$scope.loadTasks();
            break;


    }


})

///////// grid controller


.controller('GridController', function ManageController($scope, $document, $location, $http, $log,$state, $stateParams, moment, GlobalService, Social,
 AuthUser, Enum, Organization, Brief, Message, User, Mixin) {

        /*
          Grid is about recommendation
         */
        $scope.gridInit = function(){
            console.log('haha, grid initiating');
        }



    }) // end of Grid Controller

// dynamic tile grid
.controller('gridListDemoCtrl', function($scope) {

    this.tiles = buildGridModel({
            icon : "avatar:svg-",
            title: "Svg-",
            background: ""
          });

    function buildGridModel(tileTmpl){
      var it, results = [ ];

      for (var j=0; j<11; j++) {

        it = angular.extend({},tileTmpl);
        it.icon  = it.icon + (j+1);
        it.title = it.title + (j+1);
        it.span  = { row : 1, col : 1 };

        switch(j+1) {
          case 1:
            it.background = "red";
            it.span.row = it.span.col = 2;
            break;
          case 2: it.background = "green";         break;
          case 3: it.background = "darkBlue";      break;
          case 4:
            it.background = "blue";
            it.span.col = 2;
            break;

          case 5:
            it.background = "yellow";
            it.span.row = it.span.col = 2;
            break;

          case 6: it.background = "pink";          break;
          case 7: it.background = "darkBlue";      break;
          case 8: it.background = "purple";        break;
          case 9: it.background = "deepBlue";      break;
          case 10: it.background = "lightPurple";  break;
          case 11: it.background = "yellow";       break;
        }

        results.push(it);
      }
      return results;
    }
  })
  .config( function( $mdIconProvider ){
    $mdIconProvider.iconSet("avatar", 'icons/avatar-icons.svg', 128);
  });





; // end of ManageController
