Super-Blog
==========

Author: Yixia Mao

A Blogging Service System

Supported Features:

1. The system can handle multiple users and each user is able to create one or more blogs.

	Notice: please login use your Gmail account.

2. A user can select a blog that they own and write a post to that blog. A post consists of a title and a body.

3. Blogs can be viewed without an account or login. When viewing a blog, it will show at most 10 posts on a page, with a link to go to the next page of older posts.

4. When multiple posts are shown on the same page (the standard blog view), each post will display the content capped at 500 characters. Each post will have a "permalink" that, when followed, shows the complete content of the post on its own page.

	Notice: Click "more..." link of every to see post details, including edit post, delete post and see full post if content exceeds 500 characters.

5. Posts are stored along with a timestamp when the post was created. Posts can be edited, in which case the modification time is stored (and the creation time is unchanged); these timestamps will be shown at the end of the posts. The form presented to a user to edit a post has the original contents (title and body) filled in by default.

	Notice: modified time is at the end of the post, tagged as "last modified at".

6. The author of a post can give the post zero or more tags, like "tech" or "new york".

	Notice: this requires users to separate tags using ";" when creating or editing post.

7. Posts can be searched for by clicking on a tag, which means only posts with the given tag are displayed on the page. The list of tags is generated from the set of posts that have been stored, and will be displayed on the main page of the blog.

	Notice: you can try out this feature either clicking tag from tag list on main page or clicking tags of the posts.

8. When posts contain links (text that begins with http:// or https://), they will be displayed as HTML links when viewed. If a link ends with .jpg, .png, or .gif, it will be displayed inline rather than as a link.

9. Images can be uploaded. These will be available via a permalink after uploaded, and can be referenced using links in the posts.

	Notice: this feature is in Album after you login.

10. Each blog will have an RSS link, that dumps an entire blog in XML format (see wiki page for example).

	Notice: this feature is in every blog page.


Additional point:
Branch turnOfRss turns off feature RSS.


Future work:

1. Add search feature
2. Add comment feature
3. Connect to SNS (such as facebook)
4. Add “like” feature


Design and Development:

This project backend was written in Python. Front end UI used Bootstrap framework and, thanks for Twitter Bootstrap development team that greatly easy my UI work. In addition, HTML rendering used Jinja2 templates.

This project was deployed on Google App Engine, and used its data store as database.

The design can be divided into parts: Blog module and Album module. 
Blog module consists of Blog model and Post model. Posts compose Blog, and Blogs compose user Profile.
Album module consists of uploaded images. This is currently only support user private album.

All the logic and model parts are in blog.py
All the HTML templates stored in /templates directory
Static CSS and Bootstrap js files stored in /static directory


Contact:
Please contact me at yixia.mao@nyu.edu if you have any questions regarding above features and/or project design.

