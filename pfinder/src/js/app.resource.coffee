app = angular.module 'pfinder.app.resource', ['pfinder.api']

app.controller 'AppController', ['$scope', 'Post', ($scope, Post) ->
    $scope.posts = Post.query()
]
