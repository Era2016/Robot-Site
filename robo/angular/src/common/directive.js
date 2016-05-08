// https://github.com/angular-ui/ui-router/issues/1431#issuecomment-133485979
// this directive adds an active class if the parent..

bolt.directive('uiSrefActiveIf', ['$state', function($state) {
    return {
        restrict: "A",
        controller: ['$scope', '$element', '$attrs', function ($scope, $element, $attrs) {
            var state = $attrs.uiSrefActiveIf;

            function update() {
                if ( $state.includes(state) || $state.is(state) ) {
                    $element.addClass("active");
                } else {
                    $element.removeClass("active");
                }
            }

            $scope.$on('$stateChangeSuccess', update);
            update();
        }]
    };
}]);


bolt.directive('img', function () {
    return {
        restrict: 'E',        
        link: function (scope, element, attrs) {     
            element.error(function () {
                var url = '/static/assets/img/logo-transparent.png';
                element.prop('src', url);
            });
        }
    };
});

bolt.directive('ngAutoExpand', function() {
        return {
            restrict: 'A',
            link: function( $scope, elem, attrs) {
                elem.bind('keyup', function($event) {
                    var element = $event.target;

                    $(element).height(0);
                    var height = $(element)[0].scrollHeight;

                    // 8 is for the padding
                    if (height < 20) {
                        height = 28;
                    }
                    $(element).height(height-8);
                });

                // Expand the textarea as soon as it is added to the DOM
                setTimeout( function() {
                    var element = elem;

                    $(element).height(0);
                    var height = $(element)[0].scrollHeight;

                    // 8 is for the padding
                    if (height < 20) {
                        height = 28;
                    }
                    $(element).height(height-8);
                }, 0);
            }
        };
});

bolt.directive('highlight', function() {
    var component = function(scope, element, attrs) {
        
        if (!attrs.highlightClass) {
            attrs.highlightClass = 'angular-highlight';
        }
        
        var replacer = function(match, item) {
            return '<span class="'+attrs.highlightClass+'">'+match+'</span>';
        };
        var tokenize = function(keywords) {
            keywords = keywords.replace(new RegExp(',$','g'), '').split(',');
            var i;
            var l = keywords.length;
            for (i=0;i<l;i++) {
                keywords[i] = '\\W'+keywords[i].replace(new RegExp('^ | $','g'), '')+'\\W';
            }
            return keywords;
        };
        
        scope.$watch('keywords', function() {
            //console.log("scope.keywords",scope.keywords);
            if (!scope.keywords || scope.keywords === '') {
                element.html(scope.highlight);
                return false;
            }
            
            
            var tokenized   = tokenize(scope.keywords);
            var regex       = new RegExp(tokenized.join('|'), 'gmi');
            
            console.log("regex",regex);
            
            // Find the words
            var html = scope.highlight.replace(regex, replacer);
            
            element.html(html);
        });
    };
    return {
        link:           component,
        replace:        false,
        scope:          {
            highlight:  '=',
            keywords:   '='
        }
    };
});
