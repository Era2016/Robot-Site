bolt.factory('GlobalService', function (moment) {
    // var savedData = {};
    // // this is a service that enables the passing of data from one view to another
    // function set(data) {savedData = data;}
    // function get() {return savedData;}
    // return {set:set, get:get};
    var day = moment();

    var vars = {
        is_authenticated: false,
        day: day
    };

    return vars;
});

bolt.filter('dateFormatter', function($filter) {
    return function(date) {
        return $filter('date')(date, 'dd MMM yyyy');
    };
});

bolt.filter('errorFormatter', function($filter) {
    return function(errors) {
        return angular.isArray(errors) ? errors[0] : errors;
    };
});

bolt.factory('Social', function($http) {
    var Social = {
        twitter: function(url) {
            var promise = $http.jsonp('http://urls.api.twitter.com/1/urls/count.json?url='+url+'&callback=JSON_CALLBACK').then(function(response){
                return response.data;
            });
            return promise;
        },
        facebook: function(url) {
            var promise = $http.jsonp('https://graph.facebook.com/?id='+url+'&callback=JSON_CALLBACK').then(function(response){
                return response.data;
            });
            return promise;
        }

    };
    return Social;
});

bolt.factory('Utils', function(moment) {
    var utils = {
        toCamelCase: function(str) {
            return str.
                replace(/([\:\-\_]+(.))/g, function(_, separator, letter, offset) {
                    return offset ? letter.toUpperCase() : letter;
                });
        },
        toCamelCaseDict: function(dict) {
            var ret = {};
            for (var prop in dict)
                if (dict.hasOwnProperty(prop))
                    ret[utils.toCamelCase(prop)] = dict[prop];
            return ret;
        },
        copyModelInfo: function(restModel) {
            var copy = {}, responseData, prop, val;
            if (restModel.$response && restModel.$response.data &&
                restModel.$response.data.id) {
                responseData = restModel.$response.data;
                for (prop in responseData)
                    if (responseData.hasOwnProperty(prop)) {
                        val = restModel[prop];
                        if (angular.isArray(val))
                            copy[prop] = val.slice();
                        else
                            copy[prop] = val;
                    }
            }
            else {
                for (prop in restModel)
                    if (restModel.hasOwnProperty(prop) && !prop.startsWith('$')) {
                        // $ defines private properties
                        val = restModel[prop];
                        if (angular.isArray(val))
                            copy[prop] = val.slice();
                        else
                            copy[prop] = val;
                    }
            }
            return copy;
        },
        restoreModelInfo: function(restModel, copy) {
            var prop;
            for (prop in copy)
                if (copy.hasOwnProperty(prop))
                    restModel[prop] = copy[prop];
        },
        decodeRestAPIDate: function(dateStr) {
            return dateStr ? new Date(dateStr) : null;
        },
        encodeRestAPIDate: function(date) {
            if (!date)
                return null;

            var yyyy = date.getFullYear().toString();
            var mm = (date.getMonth()+1).toString(); // getMonth() is zero-based
            if (mm.length < 2) mm = '0' + mm;
            var dd  = date.getDate().toString();
            if (dd.length < 2) dd = '0' + dd;
            return [yyyy, mm, dd].join('-');
        },
        decodeRestAPIDateTime: function(timeStr) {
            return timeStr ? new Date(timeStr) : null;
        },
        encodeRestAPIDateTime: function(time) {
            return time ? time.toISOString() : null;
        },
        encodeURL: function(str) {
            if (!str.startsWith('http://') && !str.startsWith('https://')) {
                return 'https://' + str;
            }
            return str;
        }
    };
    return utils;
});

// This makes message sending a service/factory. You just need to send the message to it.
bolt.factory('Message', function ($mdToast,$document) {
    return {
        //type can be normal, warning, error, success
        showToast: function(message,type) {
            $mdToast.show({
                template:'<div class="alert '+ type +' message">'+message+'<a ng-click="closeMsg()" class="'+ type +'"><i class="u-pull-right fa fa-times-circle" style="padding:6px;"></i></a></div>',
                controller: 'AppController',
                //templateUrl: 'toast-template.html',
                parent : $document[0].querySelector('.msg-wrapper'),
                hideDelay: 4000,
                position: 'fit'
            });
            return 1;
        },
        closeToast: function() {
            $mdToast.hide();
            return 1;
        }
    };
});

bolt.factory('Mixin', function(Utils, Message) {
    return {
        RestErrorMixin: {
            observeRestErrorEvents: function(restModelClass) {
                var $scope = this;
                restModelClass.addObserverHooks($scope, {
                    'before-request': function() {
                        $scope.errors = {};
                    },
                    'after-request-error': function() {
                        if (!$scope.errors)
                            $scope.errors = {};

                        var responseErrors = this.$response.data;
                        // field errors are stored in array { username: ["required"]}
                        // global errors are stored as string { detail: "permission denided" }

                        // Display global error as flash message
                        if (typeof responseErrors.detail == 'string')
                            Message.showToast(responseErrors.detail, 'error');

                        angular.extend($scope.errors, Utils.toCamelCaseDict(this.$response.data));
                    }
                });
                $scope.$on('$destroy', function() {
                    restModelClass.removeObserverHooks($scope, ['before-request', 'after-request-error']);
                });
            }
        },
        PaginationMixin: {
            // default pagination setting
            paginationPageNumber : 1,
            paginationTotalCount: 0, // will be updated after 1st request
            paginationItemsPerPage: 20,

            observePaginationEvents: function(restModelClass) {
                var $scope = this;
                restModelClass.addObserverHooks($scope, {
                    'after-fetch-many': function() {
                        $scope.paginationPageNumber = this.$paginationGetPageNumber();
                        $scope.paginationTotalCount = this.$paginationGetTotalCount();
                        $scope.paginationItemsPerPage = this.$paginationGetItemsPerPage();
                    }
                });
                $scope.$on('$destroy', function() {
                    restModelClass.removeObserverHooks($scope, ['after-fetch-many']);
                });
            }
        },
        RestModelTimestampMixin: {
            created: {
                decode: Utils.decodeRestAPIDateTime,
            },
            modified: {
                decode: Utils.decodeRestAPIDateTime,
            }
        },
        RestModelBackgroundSaveMixin: {
            $extend: {
                Record: {
                    $backgroundSave: function() {
                        this._backgroundSave = true;
                        this.$save().$always(function() {
                            this._backgroundSave = false;
                        });
                        return this;
                    },
                    $isBackgroundSave: function() {
                        if (this.hasOwnProperty('_backgroundSave'))
                            return this._backgroundSave;
                        return false;
                    }
                },
                Model: {
                    decode: function(_record, _raw, _mask) {
                        //console.log(_record);
                        if (!_record.$isBackgroundSave()) {
                            this.$super(_record, _raw, _mask);
                        }
                    }
                }
            }
        }
    };
});

bolt.factory('Enum', function(Utils) {
    function Enum(values) {
        var prop, enumValue, self = this;

        // Make a separate property to store all the values to use in ng-repeat
        this.values = $.map(values, function(val, index) {
            return val;
        });

        // Copy over enum value for other usage, i.e. Enum.UserGender.MALE
        for (prop in values)
            if (values.hasOwnProperty(prop)) {
                this[prop] = values[prop];
            }

        this.getId = function(enumValue) {
            var ret = null;
            if (enumValue)
                return enumValue.id;
            return ret;
        };

        this.getEnum = function(id) {
            var ret = null;
            $.each(self.values, function(i, enumValue) {
                if (enumValue.id == id) {
                    ret = enumValue;
                    return false;
                }
            });
            return ret;
        };

        this.getIds = function(enumValues) {
            var ret = [];
            if (enumValues) {
                $.each(enumValues, function(i, val) {
                    var enumId = self.getId(val);
                    if (enumId)
                        ret.push(enumId);
                });
            }
            return ret;
        };

        this.getEnums = function(ids) {
            var ret = [];
            if (ids) {
                $.each(ids, function(i, enumId) {
                    var enumVal = self.getEnum(enumId);
                    if (enumVal)
                        ret.push(enumVal);
                });
            }
            return ret;
        };
    }

    return {
        UserGender: new Enum({
            MALE: { id: 1, label: "Male"},
            FEMALE: { id: 2, label: "Female"}
        }),
        TaskStatus: new Enum({
            INACTIVE: { id: 1, label: "Inactive"},
            ACTIVE: { id: 2, label: "Active"},
            FINISHED: { id:3, label: "Finished"}
        }),
        ApplicationStatus: new Enum({
            PENDING: { id: 1, label: "Applied"},
            REJECTED: { id: 2, label: "Rejected"},
            ACCEPTED: { id: 3, label: "Hired"}
        }),
        ArticleStatus: new Enum({
            EDITING: { id: 1, label: "Writing"},
            REVIEWING: { id: 2, label: "Under Review"},
            ACCEPTED: { id: 3, label: "Accepted"}
        }),
        TaskType: new Enum({
            WRITING: { id: 1, label: "Write"},
            ACCEPTING: { id: 2, label: "Review"},
            EDITING: { id: 3, label: "Edit"}
        }),
        WritingContentType: new Enum({
            SHORT_BLOG_POST: { id: 1, label: 'Short Blog Post'},
            LONG_BLOG_POST: { id: 2, label: 'Long Blog Post'},
            WEBSITE_PAGE: { id: 3, label: 'Website Page'},
            ARTICLE: { id: 4, label: 'Article'},
            PRESS_RELEASE: { id: 5, label: 'Press Release'},
        }),
        WritingGoal: new Enum({
            GENERATE_CLICKS: { id: 1, label: "Generate Clicks"},
            PROVIDE_INFORMED_ANALYSIS: { id: 2, label: "Provide Informed Analysis"},
            BUILD_THOUGHT_LEADERSHIP: { id: 3, label: "Build Thought Leadership"},
            REPURPOSE_EXISTING_WRITING: { id: 4, label: "Repurpose Existing Writing"},
            PROMOTE_TOPIC: { id: 5, label: "Promote A Topic"},
            EDUCATE_INSTRUCT: { id: 6, label: "Educate & Instruct"},
        }),
        WritingStyle: new Enum({
            AUTHORATIATIVE: { id: 1, label: "Authoratiative"},
            FORMAL: { id: 2, label: "Formal"},
            INSTRUCTIONAL: { id: 3, label: "Instructional"},
            VIRAL: { id: 4, label: "Viral"},
            CASUAL: { id: 5, label: "Casual"},
            WITTY: { id: 6, label: "Witty"},
        }),
        WritingPointOfView: new Enum({
            FIRST_PERSON: { id: 1, label: "1st Person"},
            SECOND_PERSON: { id: 2, label: "2nd Person"},
            THIRD_PERSON: { id: 3, label: "3rd Person"},
        }),
        NotificationVerb: new Enum({
            JOB_POSTED: {id:'posted', label: 'posted'},
            APPLICATION_APPLIED: {id:'applied', label: 'applied'},
            APPLICATION_ACCEPTED: {id:'accepted', label: 'accepted'},
            APPLICATION_REJECTED: {id:'rejected', label: 'rejected'},
            TASK_COMPLETED: {id:'completed', label: 'completed'},
            TASK_RETURNED: {id:'returned', label: 'returned'},
            TASK_ASSIGNED: {id:'assigned', label: 'assigned'},
        }),
        Category: new Enum({
            ART_DESIGN: { id:1, label: "Art & Design"},
            BUSINESS: { id:2, label: "Business"},
            EDUCATION: { id:3, label: "Education"},
            ENTERTAINMENT: { id:4, label: "Entertainment"},
            FOOD_BEVERAGE: { id:5, label: "Food & Beverage"},
            HEALTHCARE_SCIENCES: { id:6, label: "Healthcare & Sciences"},
            LIFESTYLE_TRAVEL: { id:7, label: "Lifestyle & Travel"},
            PUBLISHING_JOURNALISM: { id:8, label: "Publishing & Journalism"},
            SOFTWARE_TECHNOLOGY: { id:9, label: "Software & Technology"},
            SPORT_FITNESS: { id:10, label: "Sport & Fitness"},
        }),
        UserRole: new Enum({
            EMPLOYEE: {id:1, label:"Business"},
            FREELANCER: {id:2 , label:"Writer"}
        }),
        OrganizationRole: new Enum({
            OWNER:{id:1, label:"Owner"},
            EMPLOYEE:{id:2, label:"Employee"}
        }),
        CanView: new Enum({
            INTERNAL: {id:1, label:"Internal"},
            EXTERNAL: {id:2 , label:"External"}
        })
    };
});

bolt.factory('ImportedArticle', function(restmod, Enum) {
    return restmod.model();
});

bolt.factory('User', function(restmod, Enum) {
    return restmod.model('/users').mix({
        orgs: { hasMany: 'Organization' },
        jobs: { hasMany: 'Job' },
        applications: { hasMany: 'Application' },
        articles: { hasMany: 'ImportedArticle' },
        portfolios: { hasMany: 'Portfolio' },
        tasks: { hasMany: 'Task'},
        notifications: { hasMany: 'Notification' },
        organizationUser:{belongsTo:'OrganizationUser'},
        gender: {
            decode: Enum.UserGender.getEnum,
            encode: Enum.UserGender.getId
        },
        role: {
            decode: Enum.UserRole.getEnum,
            encode: Enum.UserRole.getId
        },
        $extend: {
            Record: {
                $setProfilePicture: function(picture) {
                    return this.$action(function() {
                        var url = this.$url() + '/set-picture';
                        var request = {
                            method: 'POST',
                            url: url,
                            headers: {'Content-Type': undefined}
                        };
                        request.transformRequest = [function(data) {
                            var formData = new FormData();
                            formData.append('picture', picture, picture.fileName || picture.name);
                            return formData;
                        }];

                        this.$send(request).$then(function() {
                            console.log(this.$response.data.picture);
                            this.picture = this.$response.data.picture;
                        });
                    });
                }
            }
        }
    });
});

bolt.factory('Notification', function(restmod, Utils) {
    return restmod.model().mix({
        timestamp: {
            decode: Utils.decodeRestAPIDateTime,
            encode: Utils.encodeRestAPIDateTime
        },
        actor: { hasOne: 'User' },
        $extend: {
            Collection: {
                $unreadCount: function() {
                    return this.$metadata.unread_count;
                },
                $markAllAsRead: function() {
                    return this.$action(function() {
                        var url = this.$url() + '/mark-read';
                        this.$send({method: 'POST', url: url});
                    });
                },
                $fetchNewNotifications: function() {
                    if (this.length) {
                        var latestNotification = this[0];
                        return this.$fetch({min_id: latestNotification.id});
                    }
                    else {
                        return this.$fetch();
                    }
                },
                $decode: function(_raw, _mask) {
                    // FIXME: private api, needs check for every library update
                    // notification fetch should append new item to the beginning
                    // instead of to the end of the collection
                    for(var i = 0, l = _raw.length; i < l; i++) {
                        this.$buildRaw(_raw[i], _mask).$moveTo(i).$reveal(); // build and disclose every item.
                    }

                    this.$dispatch('after-feed-many', [_raw]);
                    return this;
                },
            },
        }
    });
});

bolt.factory('Organization', function(restmod, Mixin, Utils) {
    return restmod.model('/orgs').mix(Mixin.RestModelTimestampMixin,
                                      {
                                          tasks: { hasMany: 'Task'},
                                          organizationUser:{belongsTo:'OrganizationUser'},
                                          $extend: {
                                              Record: {
                                                  $setProfilePicture: function(picture) {
                                                      return this.$action(function() {
                                                          var url = this.$url() + '/set-picture';
                                                          var request = {
                                                              method: 'POST',
                                                              url: url,
                                                              headers: {'Content-Type': undefined}
                                                          };
                                                          request.transformRequest = [function(data) {
                                                              var formData = new FormData();
                                                              formData.append('picture', picture, picture.fileName || picture.name);
                                                              return formData;
                                                          }];

                                                          this.$send(request).$then(function() {
                                                              this.picture = this.$response.data.picture;
                                                          });
                                                      });
                                                  },
                                                  $getEmployee: function() {
                                                      return this.$action(function() {
                                                          var url = this.$url() +'/employee';
                                                          var request = {
                                                              method: 'GET',
                                                              url: url,
                                                              headers: {'Content-Type': undefined}
                                                          };
                                                          this.$send(request).$then(function() {
                                                              //console.log(this.$response.data);
                                                              //return  this.$response.data;
                                                              return  this.$response.data;
                                                          });
                                                      });
                                                  }
                                              }
                                          }

                                      }

                                     );
});

bolt.factory('Task', function(restmod, Mixin, Enum, Utils) {
    return restmod.model().mix(Mixin.RestModelTimestampMixin,
                               Mixin.RestModelBackgroundSaveMixin,
                               {
                                   status: {
                                       decode: Enum.TaskStatus.getEnum,
                                       encode: Enum.TaskStatus.getId,
                                   },
                                   type: {
                                       decode: Enum.TaskType.getEnum,
                                       encode: Enum.TaskType.getId
                                   },
                                   deadline: {
                                       decode: Utils.decodeRestAPIDate,
                                       encode: Utils.encodeRestAPIDate
                                   },
                                   contentType: {
                                       decode: Enum.WritingContentType.getEnum,
                                       encode: Enum.WritingContentType.getId
                                   },
                                   goal: {
                                       decode: Enum.WritingGoal.getEnum,
                                       encode: Enum.WritingGoal.getId
                                   },
                                   style: {
                                       decode: Enum.WritingStyle.getEnum,
                                       encode: Enum.WritingStyle.getId
                                   },
                                   pointOfView: {
                                       decode: Enum.WritingPointOfView.getEnum,
                                       encode: Enum.WritingPointOfView.getId
                                   },
                                   jobs: { hasMany: 'Job' },
                                   assignee: { hasOne: 'User' }
                               }
                              );
});

bolt.factory('Brief', function(restmod,  Mixin, Utils, Enum){
    return restmod.model('/briefs')
        .mix({})
        .mix(Mixin.RestModelTimestampMixin,
             Mixin.RestModelBackgroundSaveMixin,
             {
                 deadline: {
                     decode: Utils.decodeRestAPIDate,
                     encode: Utils.encodeRestAPIDate
                 },
                 categories: {
                     decode: Enum.Category.getEnums,
                     encode: Enum.Category.getIds
                 },

                 tasks: {
                     hasMany: 'Task'
                 },
                 /*
                   comments: {
                   hasMany: 'Comment'
                   },
                   */
                   article: {
                   hasOne: 'Article'
                   },

                 $extend: {
                     Record: {
                         $save: function() {
                             var ret = this.$super();
                             if (this.published && !this.$isBackgroundSave())
                                 this.$error(function() {
                                     this.published = false;
                                 });
                             return ret;
                         },
                         // added
                         $setProfilePicture: function(picture) {
                             return this.$action(function() {
                                 var url = this.$url() + '/set-picture';
                                 var request = {
                                     method: 'POST',
                                     url: url,
                                     headers: {'Content-Type': undefined}
                                 };
                                 request.transformRequest = [function(data) {
                                     var formData = new FormData();
                                     formData.append('picture', picture, picture.fileName || picture.name);
                                     return formData;
                                 }];

                                 this.$send(request).$then(function() {
                                     console.log(this.$response.data.picture);
                                     this.picture = this.$response.data.picture;
                                 });
                             });
                         },


                         // added
                     }
                 }
             }
            );
});

bolt.factory('Comment', function(restmod, Utils, Mixin) {
    return restmod.model().mix(Mixin.RestModelTimestampMixin,
                               {
                                   created: {
                                       decode: Utils.decodeRestAPIDateTime,
                                   },
                                   modified: {
                                       decode: Utils.decodeRestAPIDateTime,
                                   },
                                   brief: {
                                       belongsTo: 'Brief'
                                   }
                               });
});


bolt.factory('Article', function(restmod, Enum, Mixin, Utils) {
    return restmod.model('/articles').mix(Mixin.RestModelTimestampMixin,
                                          Mixin.RestModelBackgroundSaveMixin,
                                          {
                                              // removed this for saving articles (they are a part of a brief and noe its own /)
                                              //return restmod.model('/articles').mix(Mixin.RestModelTimestampMixin, {
                                              status: {
                                                  decode: Enum.ArticleStatus.getEnum,
                                                  encode: Enum.ArticleStatus.getId
                                              },

                                          });
});

bolt.factory('Job', function(restmod, Mixin, Utils, Enum) {
    return restmod.model('/jobs').mix(Mixin.RestModelBackgroundSaveMixin, {
        closingDate: {
            decode: Utils.decodeRestAPIDate,
            encode: Utils.encodeRestAPIDate
        },
        deadline: {
            decode: Utils.decodeRestAPIDate,
            encode: Utils.encodeRestAPIDate
        },
        contentType: {
            decode: Enum.WritingContentType.getEnum,
            encode: Enum.WritingContentType.getId
        },
        goal: {
            decode: Enum.WritingGoal.getEnum,
            encode: Enum.WritingGoal.getId
        },
        style: {
            decode: Enum.WritingStyle.getEnum,
            encode: Enum.WritingStyle.getId
        },
        canView:{
            decode: Enum.CanView.getEnum,
            encode: Enum.CanView.getId
        },
        pointOfView: {
            decode: Enum.WritingPointOfView.getEnum,
            encode: Enum.WritingPointOfView.getId
        },
        categories: {
            decode: Enum.Category.getEnums,
            encode: Enum.Category.getIds
        },

        applications: { hasMany:'Application' },
        task: { belongsTo: 'Task' },


    });
});

bolt.factory('Application', function(restmod, Enum, Mixin, Utils) {
    return restmod.model().mix(Mixin.RestModelTimestampMixin, {
        status: {
            decode: Enum.ApplicationStatus.getEnum,
            encode: Enum.ApplicationStatus.getId
        },
        job: {belongsTo: 'Job'}
    });
});

bolt.factory('Portfolio', function(restmod, Mixin, Utils) {
    return restmod.model('/portfolios').mix(Mixin.RestModelTimestampMixin);
});


bolt.factory('OrganizationUser', function(restmod, Mixin, Enum, Utils) {
    return restmod.model('/orguser').mix(Mixin.RestModelTimestampMixin, {
        //user: {hasOne:'User', key:'user'},
        //organization: {hasOne:'Organization', key:'organization'},
        user: 0,
        organization: 0,
        user_role: { // Here, find out how to change this to the above value.
            decode: Enum.OrganizationRole.getEnum,
            encode: Enum.OrganizationRole.getId,
            key:'user_role'
        },

    });
});
