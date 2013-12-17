super-blog
==========

A Blogging Systems Service

Supported Features:

1. The system can handle multiple users and each user is able to create one or more blogs.

2. A user can select a blog that they own and write a post to that blog. A post consists of a title and a body.

3. Blogs can be viewed without an account or login. When viewing a blog, it will show at most 10 posts on a page, with a link to go to the next page of older posts.

4. When multiple posts are shown on the same page (the standard blog view), each post will display the content capped at 500 characters. Each post will have a "permalink" that, when followed, shows the complete content of the post on its own page.

5. Posts are stored along with a timestamp when the post was created. Posts can be edited, in which case the modification time is stored (and the creation time is unchanged); these timestamps will be shown at the end of the posts. The form presented to a user to edit a post has the original contents (title and body) filled in by default.

6. The author of a post can give the post zero or more tags, like "tech" or "new york".

7. Posts can be searched for by clicking on a tag, which means only posts with the given tag are displayed on the page. The list of tags is generated from the set of posts that have been stored, and will be displayed on the main page of the blog.

8. When posts contain links (text that begins with http:// or https://), they will be displayed as HTML links when viewed. If a link ends with .jpg, .png, or .gif, it will be displayed inline rather than as a link.

9. Images can be uploaded.  These will be available via a permalink after uploaded, and can be referenced using links in the posts.

10. Each blog will have an RSS link, that dumps an entire blog in XML format (see wiki page for example).
