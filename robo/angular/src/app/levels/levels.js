angular.module('bolt.level',[
    'bolt',
    'ui.router',
    'ngResource',
    'restmod',
    'ngMaterial',
])

.config(function config($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.when('/level', '/level/info');
    $stateProvider
        .state('level', {
            url: '/level',
            views: {
                'main': {
                    templateUrl: 'levels/level.tpl.html',
                    controller: '',
                },
            },
            data: {
                pageTitle: 'Level'
            }
        })
        .state('level.info', {
            url: '/info',
            views: {
                'level': {
                    templateUrl: 'levels/info.tpl.html',
                    controller: 'LevelController',
                },
            }
        })
        .state('level.competition', {
            url: '/competition',
            views: {
                'level': {
                    templateUrl: 'levels/competition.tpl.html',
                    controller: 'LevelController',
                },
            }
        })
    ;
})        

.controller('LevelController', function LevelController($scope, $location,
    $http, $log, $state, $stateParams, GlobalService, Social, AuthUser, $mdDialog,
    Enum, User, Portfolio, Mixin, Utils, Message){
    //angular.extend($scope, Mixin.RestErrorMixin);
    $scope.globals = GlobalService;
    $scope.isOrg = 0;
    $scope.level = 1;
    console.log("something is happening");

    $scope.checkLevel = function(){
        $scope.level = 2;
    }
})
