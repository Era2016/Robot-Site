angular.module( 'bolt.assignments', [
  'bolt',
  'ui.router',
  'ngResource',
  'restmod',
  'angular-medium-editor',
  'nlpCompromise',
])

.config(function config( $stateProvider,$urlRouterProvider ) {

  // go to profile as default
  $urlRouterProvider.when('/assignments', '/assignments/list');


  $stateProvider
  .state('assignments',{url:'/assignments',
      views: {'main':{ templateUrl: 'assignments/assignments.tpl.html',controller: ''}
      },
      data:{ pageTitle: 'Assignments' }
    })
  .state('assignments.edit',{url:'^/assignments/:id/edit',
      views: {'assignments':{ templateUrl: 'assignments/edit.tpl.html',controller: 'AssignmentController',},
      },
      params:{brief:{}}
    })
  .state('assignments.list',{url:'/list',
      views: {'assignments':{ templateUrl: 'assignments/list.tpl.html',controller: 'AssignmentController',},
      }})
  ;
})
/**
 * And of course we define a controller for our route.
 */
.controller('AssignmentController', function AssignmentController($scope, $location,
    $http, $log, $filter, $state, $timeout, $stateParams, GlobalService,
    AuthUser, Enum, User, Article, Application, Comment, Brief, Mixin, nlp, Message){

    angular.extend($scope, Mixin.RestErrorMixin);

    // sets the service GlobalServive object to an object in the $scope
    // so it is accessible by the view.

    $scope.globals = GlobalService;

    //
    // At this moment task and assignment are synonyms!
    //

    $scope.errors = {};
    $scope.assignments = {};
    $scope.comments = [];
    //$scope.currentComment = new Comment;
    // current active task
    $scope.activeTask = {};
    //variables for the assignment/task list
    $scope.activeTasks = [];
    $scope.inactiveTasks = [];
    $scope.finishedTasks = [];
    $scope.articlePicture = null;

    $scope.currentAssignment = {};
    $scope.currentAssignment.id = $stateParams.assId;
    $scope.Enum = Enum;
    $scope.observeRestErrorEvents(Article);

    $scope.canEditAssignment = false;
    $scope.autoSaving = false;
    $scope.lastSaveTime = null;
    var autoSaveTimeout, titleWatcher, contentWatcher;

    $scope.bindOptions = {};

    $scope.$watch('articlePicture', function() {
        if ($scope.articlePicture && $scope.articlePicture.$error) {
            Message.showToast('File too large ' + Math.round($scope.articlePicture.size / 100000) / 10 +
                ' MB: max ' + $scope.articlePicture.$errorParam + '', 'error', $scope);
        }
    });

    $scope.setArticlePicture = function(pic) {

        console.log("Here here!");
        // here is gonna be a dirty change, will fix i later.
        if ($scope.articlePicture && !$scope.articlePicture.$error) {
            // $scope.currentAssignment.$setProfilePicture($scope.articlePicture)
            // Remember here have a collision with currentBrief
            // Cause the picture should be inside the currentAssignment
            $scope.currentBrief.$setProfilePicture($scope.articlePicture)
                .$then(function() {
                    console.log($scope.articlePicture);
                  $scope.articlePicture = null;
                });
        }
    };

    $scope.$watch('canEditAssignment', function() {
        $scope.bindOptions = {
          disableEditing: !$scope.canEditAssignment
        };
    });

    $scope.$watch('currentAssignment.content', function(text) {
        if(!text) {
            $scope.wordCount = 0;
        }
        else {
            var matches = text.match(/[^\s\n\r]+/g);
            $scope.wordCount = matches ? matches.length : 0;
        }
    });

    $scope.loadAssignments = function (){
      $scope.assignments = $scope.currentUser.tasks.$refresh()
            .$then(function() {
                console.log("Starting to log.");
          var len = $scope.assignments.length;
          for (var i = 0; i < len; i++ ) {
              if($scope.assignments[i].status.id == 1) {
                // inactive
                $scope.inactiveTasks.push($scope.assignments[i]);
              } else if ($scope.assignments[i].status.id == 2) {
                // active
                $scope.activeTasks.push($scope.assignments[i]);
              } else if ($scope.assignments[i].status.id == 3) {
                // finished
                $scope.finishedTasks.push($scope.assignments[i]);
              }
          }
      });
    };

    $scope.loadComments = function(){
        $scope.comments = $scope.currentBrief.comments.$refresh()
        .$then(function(){
          //$log.log('finished pulling comments');
        });
    };

    $scope.saveComment = function(){

       $scope.currentBrief.comments.$build({content:$scope.currentComment}).$save().$then(function(){
          $scope.currentComment = null;
          $scope.loadComments();
          //$log.log('finished adding a comment');
        });
    };

    $scope.loadCurrentAssignment = function(brief,briefId){
      //$log.log(brief);
      //$log.log(briefId);
    if(brief.id){
        $scope.currentBrief = Brief.$find(brief.id).$then(function(){
            console.log("Trying to load current brief");
            console.log($scope.currentBrief);
            $scope.articlePicture = $scope.currentBrief.picture;
        //$scope.loadComments(); // load Comments
            $scope.currentAssignment = $scope.currentBrief.article.$refresh();
            console.log($scope.currentAssignment);
        $scope.canEditAssignment =
            $scope.currentBrief.currentAssignee == $scope.currentUser.id;
        if ($scope.canEditAssignment) {
            $scope.currentAssignment.$then(function() {
              $scope.autoSaveAssignment();
            });
        }
        $scope.tasks = $scope.currentBrief.tasks.$refresh().$then(function(){
          var len = $scope.tasks.length;
          for (var i = 0; i < len; i++ ) {
              if($scope.tasks[i].status.id == 2) {
                $scope.activeTask = $scope.tasks[i];
              }
          }
        });
      });
    } else {
      $scope.currentBrief = Brief.$find(briefId).$then(function(){
        $scope.loadComments(); // load Comments
        $scope.currentAssignment = $scope.currentBrief.article.$refresh();
        $scope.canEditAssignment =
            $scope.currentBrief.currentAssignee == $scope.currentUser.id;
        if ($scope.canEditAssignment) {
            $scope.currentAssignment.$then(function() {
              $scope.autoSaveAssignment();
            });
        }
        $scope.tasks = $scope.currentBrief.tasks.$refresh().$then(function(){
          var len = $scope.tasks.length;
          for (var i = 0; i < len; i++ ) {
              if($scope.tasks[i].status.label == 'Active') {
                $scope.activeTask = $scope.tasks[i];
              }
          }
        });
      });
    }
    };

    $scope.autoSaveAssignment = function() {
      function autoSave(oldValue, newValue) {
        if (newValue != oldValue) {
          if (!autoSaveTimeout)
            autoSaveTimeout = $timeout($scope.performAutoSave, 5 * 1000);
        }
      }
      titleWatcher = $scope.$watch('currentAssignment.title', autoSave);
      contentWatcher = $scope.$watch('currentAssignment.content', autoSave);
    };

    $scope.stopAutoSaveAssignment = function() {
      if (titleWatcher) {
        titleWatcher();
        titleWatcher = null;
      }
      if (contentWatcher) {
        contentWatcher();
        contentWatcher = null;
      }
    };

    $scope.performAutoSave = function() {
      $scope.autoSaving = true;
      $scope.currentAssignment.$backgroundSave().$success(function() {
        $scope.lastSaveTime = Date.now();
      }).$always(function() {
        $scope.autoSaving = false;
        autoSaveTimeout = null;
      });
    };

    $scope.checkCanEditAssignment = function() {
      $scope.canEditAssignment = 1;//$scope.currentAssignment.assignee == $scope.currentUser.id;
    };

    $scope.saveCurrentAssignment = function(){
        $scope.currentAssignment.$save();
    };

    $scope.submitCurrentAssignment = function() {
        $scope.currentAssignment.$save().$then(function() {
          $scope.activeTask.status = Enum.TaskStatus.FINISHED;
          $scope.activeTask.$save().$then(function() {
            Message.showToast('Article submitted for review', 'success');
            $scope.canEditAssignment = false;
            $scope.stopAutoSaveAssignment();
          });
        });
    };

    $scope.rejectCurrentAssignment = function() {
        $scope.currentAssignment.$save().$then(function() {
            $scope.activeTask.status = Enum.TaskStatus.INACTIVE;
            $scope.activeTask.$save().$then(function() {
              Message.showToast('Article sent back for revision', 'success');
              $scope.canEditAssignment = false;
              $scope.stopAutoSaveAssignment();
            });
        });
    };

    $scope.acceptCurrentAssignment = function() {
        $scope.currentAssignment.$save().$then(function() {
            $scope.activeTask.status = Enum.TaskStatus.FINISHED;
            $scope.activeTask.$save().$then(function() {
              Message.showToast('Article accepted', 'success');
              $scope.canEditAssignment = false;
              $scope.stopAutoSaveAssignment();
            });
        });
    };

    $scope.viewAssignment = function(brief,id) {
      $state.go('assignments.edit', {brief:brief,id:id});
    };
// ui-tree commands

      $scope.remove = function (scope) {
        scope.remove();
      };

      $scope.toggle = function (scope) {
        scope.toggle();
      };

      $scope.moveLastToTheBeginning = function () {
        var a = $scope.data.pop();
        $scope.data.splice(0, 0, a);
      };

      $scope.newSubItem = function (scope) {
        var nodeData = scope.$modelValue;
        nodeData.nodes.push({
          id: nodeData.id * 10 + nodeData.nodes.length,
          title: nodeData.title + '.' + (nodeData.nodes.length + 1),
          nodes: []
        });
      };

      $scope.collapseAll = function () {
        $scope.$broadcast('collapseAll');
      };

      $scope.expandAll = function () {
        $scope.$broadcast('expandAll');
      };

      $scope.nouns = null;
      $scope.adjectives = null;
      $scope.adverbs = null;
      $scope.verbs = null;
      $scope.values = null;



    $scope.$watch('currentAssignment.content', function() {
      if (!$scope.currentAssignment.content) {
    $scope.nouns = null;
    $scope.adjectives = null;
    $scope.adverbs = null;
    $scope.verbs = null;
    $scope.values = null;
        return;
      }

      $scope.pos = nlp.pos($scope.currentAssignment.content.replace(/(<([^>]+)>)/ig,"").replace(/&(nbsp|amp|quot|lt|gt);/g,""));

      $scope.nouns = $scope.pos.nouns().map(function(ele) {
        return ele.normalised;
      });
      //$scope.nouns = _.uniq($scope.nlp.nouns);
      $scope.nouns = $scope.nouns.join(', ');

    });
// this determines which functions to run when the page loads

    switch ($state.current.name) {
        case 'assignments.edit':
            $scope.loadCurrentAssignment($stateParams.brief,$stateParams.id);
            break;

        case 'assignments.list':
            $scope.loadAssignments();
            break;
    }

}); // end of AssignmentController
