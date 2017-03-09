# Multi-User Blog

This sets up a simple Multi-User blog on the Google App Engine.

To see this in action, visit [https://fullstack-158702.appspot.com/blog](https://fullstack-158702.appspot.com/blog) 

## Functionality

The following functionality is supported

1. User creation, authentication
2. Users can create posts
3. The post title can be clicked to go to the permalink page
4. Users can edit and delete posts
5. Users can comment on both their own and others' posts
6. Users can delete posts that they have created
7. Users can like others' posts. If a user has already liked a post, the text "Liked!" is displayed. If the current post is of the same user, no "Like" is available even though the number of likes is visible
8. Users can edit and delete their own comments. If the functionality is available, it is displayed below the comment
9. Clicking on the "Thumbs up" emoji gives a nice popup that displays the list of users that has liked a post

Parts 1 and 2 were provided as starter code, and the rest has been added by me.

The UI design is such that if an option is not relevant to a user, it is not displayed:

1. No "Like" option for a user on their own post
2. No "Edit" or "Delete" option if the user does not have permission for the current post or comment

## Issues

There are still some issues:

1. The blog displays posts created before the ReferenceProperty system was used, so some posts don't have a username. HOwever, all posts created henceforth will have it. I could not figure out how to delete the db or make changes to the DB on Google App Engine
2. It looks okay, but the looks across the blog could be much improved
3. There is no support for images, haha

