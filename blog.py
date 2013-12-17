import os
import re
import webapp2
import jinja2
import time

from google.appengine.ext import db
from google.appengine.api import users
from string import letters
from sets import Set

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Wrapper on RequestHandler for passing parameters into jinja template easier
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# helper method for checking whether user already login or not, and return corresponding Google account url and display text
def login(class_name):
    if users.get_current_user():
        url = users.create_logout_url(class_name.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(class_name.request.uri)
        url_linktext = 'Login'
    return [url, url_linktext]

def blog_key(blog_name = 'default'):
    return db.Key.from_path('Blog', blog_name)

# Convert url link and img link to HTML format
def contentParser(mystr):
    m = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', mystr)
    result = mystr
    for i in m:
        if i[-4:] == '.jpg' or i[-4:] == '.png' or i[-4:] == '.gif':
            result = result.replace(i, '<img src="' + i + '">')
        else:
            result = result.replace(i, '<a href="' + i + '">' + i + '</a>')
    return result

##Database Design
# Post DB Model
class Post(db.Model):
    author = db.StringProperty(required = True)
    blog_name = db.StringProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    tags = db.StringListProperty(indexed = True)

    def render(self):
        self._render_text = contentParser(self.content).replace('\n', '<br>')
        return render_str("post.html", subject = self.subject, author = self.author, created = self.created, _render_text = self._render_text, last_modified = self.last_modified, tags = self.tags)

    def render_digest(self):
        self.digest = contentParser(self.content[0:500]).replace('\n', '<br>')
        return render_str("post.html", subject = self.subject, author = self.author, created = self.created, _render_text = self.digest, last_modified = self.last_modified, tags = self.tags)

# Blog DB Model
class Blog(db.Model):
    blog_name = db.StringProperty(required = True, indexed=True)
    author = db.StringProperty(required = True)

# Album DB Model
class Album(db.Model):
    author = db.StringProperty(required = True)
    image = db.BlobProperty(required = True)
    image_name = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


##Action Handler
# MainPage, index page
class MainPage(BlogHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")
        blogs_query = db.GqlQuery("SELECT * FROM Blog")
        blogs = []
        for b in blogs_query.run():
            blogs.append(b)

        tags_all = []
        for p in posts:
            for t in p.tags:
                if t:
                    tags_all.append(t)
        tags_set = Set(tags_all)

        # check if user has logged in
        isLogin = False
        if users.get_current_user():
            isLogin = users.get_current_user().nickname()

        login_value = login(self)
        self.render('front.html', posts = posts, blogs = blogs, tags_set = tags_set, url = login_value[0], url_linktext = login_value[1], isLogin = isLogin)

# User profile, contains all the blog list of user
class Profile(BlogHandler):
    def get(self):
        author = self.request.get('author')
        blogs_query = db.GqlQuery("SELECT * FROM Blog WHERE author = :1", author)
        blogs = []
        for b in blogs_query.run():
            blogs.append(b)

        # check if user has logged in and is owner
        isLogin = False
        isOwner = False
        if users.get_current_user():
            isLogin = users.get_current_user().nickname()
            if isLogin == author:
                isOwner = True

        login_value = login(self)
        self.render('profile.html', blogs = blogs, author = author, url = login_value[0], url_linktext = login_value[1], isLogin = isLogin, isOwner = isOwner)

# Blog page, contains post list, RSS, create new post
class BlogPage(BlogHandler):
    def get(self):
        blog_name = self.request.get('blog_name')
        blog_query = db.GqlQuery("SELECT * FROM Blog WHERE blog_name = :1", blog_name)
        blog = blog_query.get()
        author = blog.author

        # check if user has logged in and is owner
        isLogin = False
        isOwner = False
        if users.get_current_user():
            isLogin = users.get_current_user().nickname()
            if isLogin == author:
                isOwner = True

        count = int(self.request.get('page')) 
        next_count = count+1
        posts_all = db.GqlQuery("SELECT * FROM Post WHERE blog_name = :1 ORDER BY created DESC", blog_name)
        posts = []

        length = 0
        for p in posts_all:
            length += 1

        # find posts display list according to page number
        isLastPage = False
        if count * 10 > length:
            isLastPage = True
            for i in range((count-1)*10, (count-1)*10 + length%10):
                posts.append(posts_all[i])
        else:
            for i in range((count-1)*10, count*10):
                posts.append(posts_all[i])

        login_value = login(self)
        self.render('blog.html', blog_name = blog_name, author = author, posts = posts, isLastPage = isLastPage, next_count = next_count, url = login_value[0], url_linktext = login_value[1], isLogin = isLogin, isOwner = isOwner)

# Post page, contains edit post and delete post
class PostPage(BlogHandler):
    def get(self):
        post_id = self.request.get('post_id')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        blog_name = post.blog_name
        author = post.author

        # check if user has logged in and is owner
        isLogin = False
        isOwner = False
        if users.get_current_user():
            isLogin = users.get_current_user().nickname()
            if isLogin == author:
                isOwner = True

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post_id = post_id, post = post, blog_name = blog_name, isLogin = isLogin, isOwner = isOwner)

# Create new blog handler
class NewBlog(BlogHandler):
    def get(self):
        self.render("newblog.html")

    def post(self):
        blog_name = self.request.get('blog_name')
        author = str(users.get_current_user().nickname())

        if blog_name:
            b = Blog(blog_name = blog_name, author = author)
            b.put()
            time.sleep(1)
            self.redirect('/profile?author=%s' % author)
        else:
            error = "Please type in blog name!"
            self.render("newblog.html", blog_name = blog_name, author = author, error=error)

# helper method for spliting input tags string into tags
def splitTags(tags_string):
    tags = []
    if tags_string:
        split = tags_string.split(';')
        for s in split:
            tags.append(s.strip(' \t\n\r'))
    return tags

# Create new post and tags
class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")
        
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        tags_string = self.request.get('tags')
        tags = splitTags(tags_string)
        author = str(users.get_current_user().nickname())
        blog_name = self.request.get('blog_name')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content, tags = tags, author = author, blog_name = blog_name)
            p.put()
            self.redirect('/post?post_id=%s' % str(p.key().id()))
        else:
            error = "Please type in subject and content!"
            self.render("newpost.html", subject=subject, content=content, tags = tags, author = author, error=error)

# Edit post handler, and update post information in Database
class EditPost(BlogHandler):
    def get(self):
        post_id = self.request.get('post_id')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        subject = post.subject
        content = post.content
        tags = post.tags

        # convert tags list to plain text string
        tags_string = ""
        if tags:
            for t in tags:
                tags_string += t + '; '

        self.render("newpost.html", subject = subject, content = content, tags = tags_string)

    def post(self):
        post_id = self.request.get('post_id')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        subject = self.request.get('subject')
        content = self.request.get('content')
        tags_string = self.request.get('tags')
        tags = splitTags(tags_string)
        author = str(users.get_current_user().nickname())
        blog_name = self.request.get('blog_name')

        if subject and content:
            post.subject = subject
            post.content = content
            post.tags = tags
            post.put()
            self.redirect('/post?post_id=%s' % str(post.key().id()))
        else:
            error = "Please type in subject and content!"
            self.render("newpost.html", subject=subject, content=content, author = author, tags = tags, error=error)

# Delete post handler, and delete post in Database
class DelPost(BlogHandler):
    def get(self):
        post_id = self.request.get('post_id')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        blog_name = post.blog_name
        db.delete(key)
        time.sleep(1)
        self.redirect('/blog?blog_name=%s' % blog_name)

# Display all posts belong to a tag category
class TagPost(BlogHandler):
    def get(self):
        tag = self.request.get('tag')
        posts = db.GqlQuery("SELECT * FROM Post WHERE tags = :1 ORDER BY created DESC", tag)
        self.render("tagpost.html", posts = posts, tag = tag)

# User album page, contains list of links to uploaded images 
class AlbumPage(BlogHandler):
    def get(self):
        author = self.request.get('author')
        images = db.GqlQuery("SELECT * FROM Album WHERE author = :1 ORDER BY created DESC", author)

        # check if user has logged in and is owner
        isLogin = False
        isOwner = False
        if users.get_current_user():
            isLogin = users.get_current_user().nickname()
            if isLogin == author:
                isOwner = True

        login_value = login(self)
        self.render('album.html', images = images, author = author, url = login_value[0], url_linktext = login_value[1], isLogin = isLogin, isOwner = isOwner)

# Display one image
class ImagePage(BlogHandler):
    def get(self):
        image_id = self.request.get('image_id')
        key = db.Key.from_path('Album', int(image_id))
        image = db.get(key)
        image_name = image.image_name
        author = image.author

        # check if user has logged in and is owner
        isLogin = False
        isOwner = False
        if users.get_current_user():
            isLogin = users.get_current_user().nickname()
            if isLogin == author:
                isOwner = True

        if not image:
            self.error(404)
            return

        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(image.image)

# Upload new image
class NewImage(BlogHandler):
    def get(self):
        self.render('newimage.html')
        
    def post(self):
        image_name = self.request.get('image_name')
        image = self.request.get('img')
        author = str(users.get_current_user().nickname())

        if image_name and image:
            i = Album(image_name = image_name, image = image, author = author)
            i.put()
            time.sleep(1)
            self.redirect('/album?author=%s' % author)
        else:
            error = "Please upload your image!"
            self.render("newimage.html", image_name=image_name, image=image, author = author, error=error)

# RSS of blog
class BlogRSS(BlogHandler):
    def get(self):
        blog_name = self.request.get('blog_name')
        blog_query = db.GqlQuery("SELECT * FROM Blog WHERE blog_name = :1", blog_name)
        blog = blog_query.get()
        author = blog.author
        posts = db.GqlQuery("SELECT * FROM Post WHERE blog_name = :1 ORDER BY created DESC", blog_name)
        self.render('RSS.xml', blog = blog, posts = posts)

class Contact(BlogHandler):
    def get(self):
        self.render('about.html')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/profile', Profile),
                               ('/blog', BlogPage),
                               ('/post', PostPage),
                               ('/newblog', NewBlog),
                               ('/newpost', NewPost),
                               ('/editpost', EditPost),
                               ('/delpost', DelPost),
                               ('/tagpost', TagPost),
                               ('/album', AlbumPage),
                               ('/image', ImagePage),
                               ('/newimage', NewImage),
                               ('/blogRSS', BlogRSS),
                               ('/contact', Contact),
                               ],
                              debug=True)
