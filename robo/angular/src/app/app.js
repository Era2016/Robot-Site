var bolt = angular.module('bolt', [
        'ngAnimate',
        'ngMaterial',
        'templates-app',
        'templates-common',
        'ngCookies',
        'ngResource',
        'ngStorage',
        'ngRoute',
        'ui.router',
        'restmod',
        'angularMoment',
        'ngFileUpload',
        'angularUtils.directives.dirPagination',
        'bolt.user',
        'bolt.org',
        'bolt.briefs',
        'bolt.jobs',
        'bolt.manage',
        'bolt.create',
        'bolt.applications',
        'bolt.notes',
        'bolt.assignments',
        'angular-loading-bar',
        'ui.utils.masks',
        'infinite-scroll'
    ])
    .config(function($mdThemingProvider) {

        $mdThemingProvider.definePalette('boltColorPalette', {
            '50': 'F3F8FD', //blues
            '100': 'D2E5F8',
            '200': 'A5CAF2',
            '300': '77B0EB',
            '400': '4A95E5',
            '500': '3389E2',
            '600': '1D7BDE',
            '700': '1764B6',
            '800': '155CA7',
            '900': '134E8F',
            'A100': 'F6F6F6', // light grey
            'A200': 'DBDADB',
            'A400': 'B7B5B7',
            'A700': '929192',
            'contrastDefaultColor': 'light', // whether, by default, text (contrast)
            // on this palette should be dark or light
            'contrastDarkColors': ['50', '100', //hues which contrast should be 'dark' by default
                '200', '300', '400', 'A100'
            ],
            'contrastLightColors': undefined // could also specify this if default was 'dark'
        });
        $mdThemingProvider.theme('default').primaryPalette('boltColorPalette');

        $mdThemingProvider.definePalette('altColorPalette', {
            '50': 'F6FCFC', // teals
            '100': 'DCF2F3',
            '200': 'B9E5E6',
            '300': '85D2D4',
            '400': '95D8DA',
            '500': '72CBCD',
            '600': '4FBEC1',
            '700': '409B9F',
            '800': '3B8E91',
            '900': '32787C',
            'A100': '929192', //dark grey
            'A200': '6E6C6E',
            'A400': '4A474A',
            'A700': '3B383B',
            'contrastDefaultColor': 'light', // whether, by default, text (contrast)
            // on this palette should be dark or light
            'contrastDarkColors': ['50', '100', //hues which contrast should be 'dark' by default
                '200', '300', '400', 'A100'
            ],
            'contrastLightColors': undefined // could also specify this if default was 'dark'
        });
        $mdThemingProvider.theme('default').accentPalette('altColorPalette');

        //$mdThemingProvider.theme('altTheme').primaryPalette('altColorPalette');
    })

.config(function(restmodProvider) {
    restmodProvider.rebase('AMSApi', 'DefaultPacker', {
        errors: {
            mask: true
        }, // response errors will be bind to this
        $config: {
            urlPrefix: '/api/v1',
            plural: 'results' // json property name for list/collection
        },
        $hooks: {
            'before-request': function(_req) {
                _req.url += '.json';
                this.$setErrors({});
            },
            'after-request-error': function() {
                this.$setErrors(this.$response.data);
            }
        },
        $extend: {
            Model: {
                unpack: function(_resource, _raw) {
                    if (_resource.$isCollection)
                        return this.$super(_resource, _raw);
                    return _raw;
                },
                addObserverHooks: function(observer, hooks) {
                    // Note: duplicated hooks for the same observer is not supported appropriately
                    var prop, restmodHooks;
                    // Should not really add property to 'this'
                    var observerHooks = this._observerHooks = this._observerHooks || {}; // map event key -> list of functions

                    function makeHook(prop) {
                        return function() {
                            var that = this,
                                thatArguments = arguments;
                            $.each(observerHooks[prop], function(i, hook) {
                                hook.call(that, thatArguments);
                            });
                        };
                    }

                    function wrapObserverHook(hook) {
                        var wrappedHook = function() {
                            hook.call(this, arguments);
                        };
                        wrappedHook._observer = observer;
                        return wrappedHook;
                    }

                    for (prop in hooks)
                        if (hooks.hasOwnProperty(prop)) {
                            if (!observerHooks.hasOwnProperty(prop)) {
                                observerHooks[prop] = [];
                                restmodHooks = {};
                                restmodHooks[prop] = makeHook(prop);
                                this.mix({
                                    $hooks: restmodHooks
                                });
                            }
                            observerHooks[prop].push(wrapObserverHook(hooks[prop]));
                        }
                },
                removeObserverHooks: function(observer, keys) {
                    var that = this;
                    $.each(keys, function(i, prop) {
                        if (that._observerHooks.hasOwnProperty(prop)) {
                            var hooks = that._observerHooks[prop];
                            that._observerHooks[prop] = $.grep(hooks, function(hook) {
                                return hook._observer != observer;
                            });
                        }
                    });
                }
            },
            Collection: {
                $paginationGetPageNumber: function() {
                    return this.$metadata.page;
                },
                $paginationGetTotalCount: function() {
                    return this.$metadata.count;
                },
                $paginationGetItemsPerPage: function() {
                    return this.$metadata.items_per_page;
                }
            },
            Resource: {
                $success: function(func) {
                    return this.$then(func);
                },
                $error: function(func) {
                    return this.$then(null, func);
                },
                $setErrors: function(errors) {
                    function toCamelCase(str) {
                        return str.
                        replace(/([\:\-\_]+(.))/g, function(_, separator, letter, offset) {
                            return offset ? letter.toUpperCase() : letter;
                        });
                    }

                    function toCamelCaseDict(dict) {
                        var ret = {};
                        for (var prop in dict)
                            if (dict.hasOwnProperty(prop))
                                ret[toCamelCase(prop)] = dict[prop];
                        return ret;
                    }
                    this.errors = toCamelCaseDict(errors);
                }
            }
        }
    });
})

// configureation for the loading bar
.config(['cfpLoadingBarProvider', function(cfpLoadingBarProvider) {
    cfpLoadingBarProvider.includeSpinner = false;
    cfpLoadingBarProvider.latencyThreshold = 2000;
    //cfpLoadingBarProvider.barTemplate = '';
}])

.config(function AppConfig($stateProvider, $urlRouterProvider, $interpolateProvider,
    $httpProvider, $resourceProvider, $locationProvider) {
    // Allows us to remove hashtag. Does not work with IE less than IE10
    $locationProvider.html5Mode(true);
    // Allows us to use both django and angular templates
    $interpolateProvider.startSymbol("{[{").endSymbol("}]}");
    // Passes CSRF token to angular to use in headers
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    // Recommended for working with django
    $resourceProvider.defaults.stripTrailingSlashes = false;
    // this is using ui-router, rather than ngRoute.
    $urlRouterProvider.otherwise("/manage");

    $httpProvider.defaults.useXDomain = true;
    $httpProvider.defaults.withCredentials = true;
    //delete $httpProvider.defaults.headers.common["X-Requested-With"];
    $httpProvider.defaults.headers.common["Accept"] = "application/json";
    $httpProvider.defaults.headers.common["Content-Type"] = "application/json";


})

.run(function run($rootScope, $location) {
    $rootScope.location = $location;
})

.controller('AppController', function AppController($scope, $rootScope, $location,
    $http, $log, $stateParams, $state, $mdToast, $document,
    AuthUser, Enum, Message, GlobalService, User, $timeout, $mdSidenav, $mdUtil
) {

    $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams) {
        if (angular.isDefined(toState.data.pageTitle)) {
            $scope.pageTitle = 'Connverse | ' + toState.data.pageTitle;
        }
    });

    // sets the service GlobalServive object to an object in the $scope
    // so it is accessible by the view.
    $scope.globals = GlobalService;

    $scope.initialize = function(is_authenticated) {
        $scope.isLoading = false;
        $scope.Enum = Enum;
        $scope.isOrg = 0;

        $scope.currentUser = User.$find(AuthUser.getUser().id).$then(function() {
            $scope.currentUser.role = Enum.UserRole.getEnum(AuthUser.getUser().role);
            $scope.isOrg = $scope.currentUser.role.id == 1 ? 1 : 0;
            var orgs = $scope.currentUser.orgs.$refresh().$then(function() {
                $scope.currentOrg = orgs[0];
            });
        });
        $scope.globals.is_authenticated = is_authenticated;
    };

    $scope.closeMsg = function() {
        Message.closeToast();
    };
    // defines both the menu and the submenu behavior depending on the
    // role and the location of the browser, what is active or not

    $scope.subMenuClass = function(page) {
        // Sets the CSS style of the navigation menu depending on the role
        var currentLocation = $location.path().substring(1).replace(/\/.*/, '');
        var result = ((page.indexOf(currentLocation) != -1));
        return result ? "active" : "inactive";
    };

    // Side Navigation

    $scope.toggleRight = buildToggler('right');

    function buildToggler(navID) {
        var debounceFn = $mdUtil.debounce(function() {
            $mdSidenav(navID)
                .toggle()
                .then(function() {
                    //$log.debug("toggle " + navID + " is done");
                });
        }, 200);

        return debounceFn;
    }

    $scope.closeSideNav = function() {
        $mdSidenav('right').close()
            .then(function() {
                //$log.debug("close RIGHT is done");
            });
    };

});
