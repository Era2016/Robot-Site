angular.module( 'bolt.notes', [
  'bolt',
  'ui.router',
  'ngResource',
  'restmod',
  'ngStorage',
  //'oitozero.ngSweetAlert',
  'ngMaterial',

 

])

.config(function config( $stateProvider ) {
  $stateProvider
  .state('notes',{url:'/notes',
      views: {'main':{ templateUrl: 'notes/notes.tpl.html',controller: 'NoteController'}
      },
      data:{ pageTitle: 'Notes' }
    })
  ;
})

.controller('NoteController', function NoteController($scope, $location, 

    $http, $log, $filter, $state, $stateParams, GlobalService, AuthUser, Enum, Job, User, $mdDialog, $localStorage){

    


    $scope.globals = GlobalService;
    $scope.$storage = $localStorage;
// initializes the currentOrg and error objects
    if(!$scope.$storage.notes) {
      $scope.currentNote = {};
      $scope.$storage.notes = [{}];
  
      $scope.$storage.noteId = 0;
   }

    $scope.editing = false;
    $scope.errors = {};
    $scope.Enum = Enum;

    $scope.newNoteMaterial = function(ev) {
        
       
        $mdDialog.show({
          controller: NoteController,
          template: '<div class="container"><md-dialog aria-label="New Note"> <form> <md-toolbar> <div class="md-toolbar-tools"> <h2>New Note</h2><!-- <md-button class="md-icon-button" ng-click="cancel()"> <md-icon md-svg-src="img/icons/ic_close_24px.svg" aria-label="Close dialog"></md-icon> </md-button> --> </div></md-toolbar> <md-dialog-content style="max-width:800px;max-height:810px; "> <div> <md-content layout-padding> <md-input-container flex> <label>Title</label> <input ng-model="currentNote.title"> </md-input-container> <md-input-container flex> <label>Content</label> <textarea ng-model="currentNote.content" columns="1" md-maxlength="250"></textarea> </md-input-container> </div></md-dialog-content> <div class="md-actions" layout="row"> <md-button class="md-raised md-primary" ng-click="cancel()" > Cancel </md-button> <md-button class="md-raised md-primary" ng-click="saveNote(currentNote)" style="margin-right:20px;" > Save </md-button> </div></md-content> </form></md-dialog></div>',
          parent: angular.element(document.body),
          targetEvent: ev,
          clickOutsideToClose:true
        })
        .then(function() {
          $scope.editing = true;
          $scope.$storage.noteId += 1;
       //   $log.log('storage notes changed', $scope.$storage.noteId);
          $scope.currentNote = { id:$scope.$storage.noteId, title:'', content:''};
          $scope.currentNote={};
      });
    };

    $scope.hide = function() {
        $mdDialog.hide();
    };
    $scope.cancel = function() {
        $mdDialog.cancel();
    };
    
    $scope.saveNote = function(currentNote) {
         
        $scope.$storage.noteId += 1;
        $scope.currentNote = { id:$scope.$storage.noteId ,title:$scope.currentNote.title, content:$scope.currentNote.content};
        $scope.$storage.notes.push($scope.currentNote);
        $mdDialog.hide();
    };

    

    $scope.newNote = function() {
      $scope.editing = true;
      $scope.currentNote = { id:$scope.$storage.noteId, title:'',content:''};
      $scope.$storage.noteId += 1;
    };
    $scope.resetNotes = function() {
      $scope.$storage.$reset();
      $scope.currentNote = {};
      $scope.$storage.notes = [{}];
    };

    $scope.deleteNote = function(noteid) {

      };

    // $scope.saveNote = function() {
    //   $scope.$storage.notes.push($scope.currentNote);
    //   $scope.currentNote={};
    // };
}); // end of JobController

