import os
import re
from string import letters

import webapp2
import jinja2
import time

from google.appengine.ext import db
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Wrapper on RequestHandler
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

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

class Post(db.Model):
    author = db.StringProperty(required = True)
    blog_name = db.StringProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    # tags = db.StringProperty(repeated=True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

class Blog(db.Model):
    blog_name = db.StringProperty(required = True)
    author = db.StringProperty(required = True)


class MainPage(BlogHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")
        blogs_query = db.GqlQuery("SELECT * FROM Blog")
        blogs = []
        for b in blogs_query.run():
            blogs.append(b)

        isLogin = False
        if users.get_current_user():
            isLogin = users.get_current_user().nickname()

        login_value = login(self)
        self.render('front.html', posts = posts, blogs = blogs, url = login_value[0], url_linktext = login_value[1], isLogin = isLogin)

class Profile(BlogHandler):
    def get(self):
        author = self.request.get('author')
        blogs_query = db.GqlQuery("SELECT * FROM Blog WHERE author = :1", author)
        blogs = []
        for b in blogs_query.run():
            blogs.append(b)
        login_value = login(self)
        self.render('profile.html', blogs = blogs, author = author, url = login_value[0], url_linktext = login_value[1])

class BlogPage(BlogHandler):
    def get(self):
        blog_name = self.request.get('blog_name')
        blog_query = db.GqlQuery("SELECT * FROM Blog WHERE blog_name = :1", blog_name)
        blog = blog_query.get()
        author = blog.author

        # check if current user is blog owner
        isOwner = False
        if users.get_current_user():
            if users.get_current_user().nickname() == author:
                isOwner = True

        posts = db.GqlQuery("SELECT * FROM Post WHERE blog_name = :1 ORDER BY created DESC LIMIT 10", blog_name)
        login_value = login(self)
        self.render('blog.html', blog_name = blog_name, author = author, posts = posts, url = login_value[0], url_linktext = login_value[1], isOwner = isOwner)


class PostPage(BlogHandler):
    def get(self):
        post_id = self.request.get('post_id')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        blog_name = post.blog_name

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post, blog_name = blog_name)

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

class NewPost(BlogHandler):

    def get(self):
        self.render("newpost.html")
        
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        author = str(users.get_current_user().nickname())
        blog_name = self.request.get('blog_name')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content, author = author, blog_name = blog_name)
            p.put()
            self.redirect('/post?post_id=%s' % str(p.key().id()))
        else:
            error = "Please type in subject and content!"
            self.render("newpost.html", subject=subject, content=content, author = author, error=error)

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/profile', Profile),
                               ('/blog', BlogPage),
                               ('/post', PostPage),
                               ('/newblog', NewBlog),
                               ('/newpost', NewPost),
                               ],
                              debug=True)
