import os
import bcrypt
import tornado.ioloop
import tornado.web
import tornado.log
import tornado.escape

from dotenv import load_dotenv
from models import Posts, Users, Comments
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
        self.render_template("home.html", {'posts': posts})

class SignupHandler(TemplateHandler):
    """Sign up page to create user"""
    def get (self):
        self.render_template("signup.html", {})

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
            messages.append("Please fill out all fields")
            return self.render_template("create_post.html", {'messages': tuple(messages)})
        user = self.current_user
        Posts.create(user_id=user.id, title=title, category=category, post=post)
        messages.append("Created Post!")
        return self.render_template("create_post.html", {'messages': tuple(messages)})

class PostHandler(TemplateHandler):
    def get(self, slug):
        post = Posts.select().where(Posts.id == slug)
        if post:
            post = Posts.select().where(Posts.id == slug).get()
            comments = Comments.select().where(Comments.post_id == slug).order_by(Comments.created.desc())
            loggedInUser = self.get_current_user
            return self.render_template("post.html", {'post': post, 'comments': comments, 'loggedInUser': loggedInUser})
        return self.redirect("/")

    @tornado.web.authenticated
    def post(self, slug):
        comment = self.get_body_argument('comment')
        if comment == "":
            return self.redirect('/post/{}'.format(slug))
        user = self.current_user
        # change to user, not author later
        Comments.create(author_id=user.id, post_id=slug, comment=comment)
        return self.redirect("/post/{}".format(slug))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/signup", SignupHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/post", CreatePostHandler),
        (r"/post/(.*)", PostHandler),
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

