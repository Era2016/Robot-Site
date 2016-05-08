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

    // Note.mix({
    //     $hooks: {
    //         'before-request': function() {
    //             $scope.errors = {};
    //         },
    //         'after-request-error': function() {
    //             $scope.errors = this.$response.data;
    //         },

    //     }
    // });

// loads the organizations that a particular user is connected to create a job

    // swal({
    //    title: "New Note",
    //    text: "Title:",
    //    type: "input",
    //    inputPlaceholder: "Title of the Note",
    //    text: "Contents",
    //    type: "input",
    //    inputPlaceholder: "Please Type Your Contents here"  
    //    showCancelButton: true,   
    //    closeOnConfirm: false,   
    //    animation: "slide-from-top"  
       
    //  }, 
    //   function(inputValue){   
    //     if (inputValue === false) return false;  
    //     if (inputValue === "") {  
    //        swal.showInputError("You need to write something!"); 
    //            return false 
    //              } 
    //        swal("Nice!", "You wrote: " + inputValue, "success"); 
    //      });

    // $scope.newNoteSwtAlrt = function(){
    //      swal.withForm({
    //         title: "New Note",
    //         text: 'A note for your reminder',
    //         showCancelButton: true,
    //         confirmButtonText: 'Submit',
    //         closeOnConfirm: true,
    //         formFields: [
    //             { id: 'Title', placeholder:'Please add Title here' },
    //             { id: 'Contents', placeholder:'Please add your Contents here' }
    //       ]
    //   }, function(isConfirm) {
    //       // do whatever you want with the form data
    //       console.log(this.swalForm); // { name: 'user name', nickname: 'what the user sends' }
    //       });
     //   title: "New Note",
     //   type: "input",
     //   inputPlaceholder: "Title of the Note",
     //   type: "input",
     //   inputPlaceholder: "Please Type Your Contents here", 
     //   showCancelButton: true,   
     //   closeOnConfirm: false,   
     //   animation: "slide-from-top"  
       
     // }, 
     //  function(inputValue){   
     //    if (inputValue === false) return false;  
     //    if (inputValue === "") {  
     //       swal.showInputError("You need to write something!"); 
     //           return false 
     //             } 
     //       swal("Nice!", "You wrote: " + inputValue, "success"); 
     //     });

      // };

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
         
        //  $log.log('storage notes', $scope.$storage.noteId);
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

    //   SweetAlert.swal({
    //    title: "Are you sure?",
    //    text: "Your will not be able to recover this note!",
    //    type: "warning",
    //    showCancelButton: true,
    //    confirmButtonColor: "#DD6B55",
    //    confirmButtonText: "Delete",
    //    cancelButtonText: "Cancel",
    //    closeOnConfirm: false,
    //    closeOnCancel: true }, 
    // function(isConfirm){ 
    //    if (isConfirm) {
    //     // $log.log($scope.$storage.notes); 
    //     // $log.log(noteid);
    //       $log.log($scope.$storage.notes.splice(1, 1));   
    //       SweetAlert.swal("Deleted!", "Your note has been deleted.", "success");
    //       } 
    //    });
      };

    // $scope.saveNote = function() {
    //   $scope.$storage.notes.push($scope.currentNote);
    //   $scope.currentNote={};
    // };
}); // end of JobController

