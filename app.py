import os
import bcrypt
import tornado.ioloop
import tornado.web
import tornado.log
import tornado.escape

from dotenv import load_dotenv
from models import Posts, Users, Comments, Likes
from validate_email_address import validate_email
from jinja2 import \
  Environment, PackageLoader, select_autoescape

load_dotenv('.env')

PORT = int(os.environ.get('PORT', '8000'))

ENV = Environment(
    loader=PackageLoader('blog', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)    

class TemplateHandler(tornado.web.RequestHandler):
    def render_template (self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))

    # checks if user exists
    def user_exists(self, email):
        return bool(Users.select().where(Users.email == email))

    # authentication to determine current user available in every request handler
    def get_current_user(self):
        user_id = self.get_secure_cookie("blog_user")
        if not user_id: return None
        return Users.select().where(Users.id == int(user_id)).get()

class MainHandler(TemplateHandler):
    def get (self):
        posts = Posts.select().order_by(
            Posts.created.desc())
        if self.current_user:
            loggedInUser = self.current_user
            return self.render_template("home.html", {'posts': posts, 'loggedInUser': loggedInUser})
        return self.render_template("home.html", {'posts': posts})

class SignupHandler(TemplateHandler):
    """Sign up page to create user"""
    def get (self):
        loggedInUser = self.current_user
        if not loggedInUser:
            return self.render_template("signup.html", {'loggedInUser': loggedInUser})
        return self.redirect("/")

    def post (self):
        email = self.get_body_argument('email')
        username = self.get_body_argument('username')
        password = self.get_body_argument('password')
        passwordConfirm = self.get_body_argument('passwordConfirm')
        messages = []
        user = self.user_exists(email)
        # Validations
        # if user exists
        if user:
            messages.append("Email already exists")
        # if email invalid format
        if not validate_email(email):
            messages.append("Invalid email address")
        # checks if username is not an empty string
        if username == "":
            messages.append("Input username")
        # checks if passwords match
        if password != passwordConfirm:
            messages.append("Passwords do not match")
        # checks password length is valid
        if len(password) < 8:
            messages.append("Password length must by greater than 7")
        # if errors occured, display errors and redirect to signup
        if messages:
            return self.render_template("signup.html", {'messages': tuple(messages)})
        # create hashed & salted user password
        # tornado.escape.utf8 converts string to byte string
        # https://github.com/pyca/bcrypt#password-hashing
        hashed_password = bcrypt.hashpw(tornado.escape.utf8(password), bcrypt.gensalt())
        # create user
        user = Users.create(email=email, username=username, hashed_password=hashed_password)
        self.set_secure_cookie("blog_user", str(user.id))
        return self.redirect("/")

class LoginHandler(TemplateHandler):
    """Login in user"""
    def get (self):
        self.render_template("login.html", {})

    def post (self):
        email = self.get_body_argument('email')
        password = self.get_body_argument('password')
        user = self.user_exists(email)
        messages = []
        # if user does not exist
        if not user:
            messages.append("Invalid Email/Password")
            return self.render_template("login.html", {'messages': tuple(messages)})
        user = Users.get(Users.email == email)
        # https://github.com/pyca/bcrypt#password-hashing
        matched = bcrypt.checkpw(tornado.escape.utf8(password), 
                            tornado.escape.utf8(user.hashed_password))
        # if incorrect password
        if not matched:
            messages.append("Invalid Email/Password")
            return self.render_template("login.html", {'messages': tuple(messages)})
        # Log in user
        self.set_secure_cookie("blog_user", str(user.id))
        return self.redirect("/")

class LogoutHandler(TemplateHandler):
    def post(self):
        self.clear_cookie("blog_user")
        messages = "Logged Out Succesfully!"
        return self.redirect("/")

class CreatePostHandler(TemplateHandler):
    @tornado.web.authenticated
    def get(self):
        return self.render_template("create_post.html", {})

    @tornado.web.authenticated
    def post(self):
        title = self.get_body_argument('title')  
        category = self.get_body_argument('category')  
        post = self.get_body_argument('post')
        messages = []
        if title == "" or category == "" or post == "":
            messages.append("PLEASE FILL OUT ALL FIELDS")
            return self.render_template("create_post.html", {'messages': tuple(messages)})
        user = self.current_user
        Posts.create(user_id=user.id, title=title, category=category, post=post)
        messages.append("POST CREATED!")
        return self.render_template("create_post.html", {'messages': tuple(messages)})

class PostHandler(TemplateHandler):
    def get(self, slug):
        post = Posts.select().where(Posts.id == slug)
        if post:
            post = Posts.select().where(Posts.id == slug).get()
            comments = Comments.select().where(Comments.post_id == slug).order_by(Comments.created.desc())
            # number of likes
            likes = Likes.select().where(Likes.post_id == slug).count() 
            loggedInUser = self.current_user
            return self.render_template("post.html", {'post': post, 'comments': comments, 'likes': likes, 'loggedInUser': loggedInUser})
        return self.redirect("/")

class CommentHandler(TemplateHandler):
    @tornado.web.authenticated
    def get(self, slug):
        return self.redirect("/post/{}".format(slug))

    @tornado.web.authenticated
    def post(self, slug):
        comment = self.get_body_argument('comment')
        if comment == "":
            return self.redirect('/post/{}'.format(slug))
        user = self.current_user
        Comments.create(user_id=user.id, post_id=slug, comment=comment)
        return self.redirect("/post/{}".format(slug))

class LikeHandler(TemplateHandler):
    @tornado.web.authenticated
    def get(self, slug):
        return self.redirect("/post/{}".format(slug))

    @tornado.web.authenticated
    def post(self, slug):
        user = self.current_user
        likes = Likes.select().where(Likes.post_id == slug)
        if likes:
            # Do not allow more than one like for one post
            likes = Likes.select().where(Likes.post_id == slug).get()
            if likes.user_id == user.id:
                return self.redirect("/post/{}".format(slug))
        # If you are creator of post, can not like it
        post = Posts.select().where(Posts.id == slug).get()
        if post.user_id == user.id:
            return self.redirect("/post/{}".format(slug))
        # Create like 
        Likes.create(user_id=user.id, post_id=slug)
        return self.redirect("/post/{}".format(slug))

class AuthorHandler(TemplateHandler):
    def get(self, slug):
        user = Users.select().where(Users.id == slug)
        if user:
            # Retrieve users post, comment, and like history 
            posts = Posts.select().where(Posts.user_id == slug)
            if posts:
                posts = (Posts.select().where(Posts.user_id == slug).order_by(Posts.created.desc()))
            comments = Comments.select().where(Comments.user_id == slug)
            if comments:
                comments = (Comments.select().where(Comments.user_id == slug).order_by(Comments.created.desc()))
            likes = Likes.select().where(Likes.user_id == slug)
            if likes:
                likes = (Likes.select().where(Likes.user_id == slug).order_by(Likes.created.desc()))
            numPosts = Posts.select().where(Posts.user_id == slug).count()
            numComments = Comments.select().where(Comments.user_id == slug).count()
            numLikes = Likes.select().where(Likes.user_id == slug).count()
            return self.render_template("author.html", {'posts': posts, 'numPosts': numPosts, 
                                                        'numComments': numComments, 'numLikes': numLikes, 
                                                        'comments': comments, 'likes': likes} )
        return self.redirect("/")

class EditPostHandler(TemplateHandler):
    @tornado.web.authenticated
    def get(self, slug):
        post = Posts.select().where(Posts.id == slug)
        if post:
            post = Posts.select().where(Posts.id == slug).get()
            user = self.current_user
            # Only allow the creator of the post access to edit 
            if post.user_id == user.id:
                return self.render_template("edit_post.html", {'post': post})
        return self.redirect("/")

    @tornado.web.authenticated
    def post(self, slug):
        post = Posts.select().where(Posts.id == slug)
        if post:
            post = Posts.select().where(Posts.id == slug).get()
            loggedInUser = self.current_user
            print(post.id, 'post id')
            # Only allow the creator of the post access to edit 
            if post.user_id == loggedInUser.id:
                title = self.get_body_argument('title')
                category = self.get_body_argument('category')
                post = self.get_body_argument('post')
                # Edit Post 

                Posts.update(title=title, category=category, post=post).where(Posts.id == slug).execute()
                return self.redirect("/post/" + slug)
        return self.redirect("/")

class DeletePostHandler(TemplateHandler):
    @tornado.web.authenticated
    def get(self, slug):
        return self.redirect("/")

    @tornado.web.authenticated
    def post(self, slug):
        post = Posts.select().where(Posts.id == slug)
        print('FIRST')
        if post:
            post = Posts.select().where(Posts.id == slug).get()
            user = self.current_user
            print('HELLO')
            # Only allow the creator of the post access to edit 
            if post.user_id == user.id:
                print(post, 'POST')
                post.delete_instance(recursive=True, delete_nullable=True)
        return self.redirect("/")          
    

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/signup", SignupHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/post", CreatePostHandler),
        (r"/post/(.*)", PostHandler),
        (r"/comment/(.*)", CommentHandler),
        (r"/like/(.*)",  LikeHandler),
        (r"/author/(.*)", AuthorHandler),
        (r"/post-edit/(.*)", EditPostHandler),
        (r"/post-delete/(.*)", DeletePostHandler),
        (r"/static/(.*)", 
        tornado.web.StaticFileHandler, {'path': 'static'}),
    ], autoreload=True,
        cookie_secret="SECRET",
        login_url="/login")

if __name__ == "__main__":
    tornado.log.enable_pretty_logging()
    app = make_app()
    app.listen(PORT, print('Creating magic on port {}'.format(PORT)))
    tornado.ioloop.IOLoop.current().start()

