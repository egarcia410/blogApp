import os
import tornado.ioloop
import tornado.web
import tornado.log

from dotenv import load_dotenv
from models import Post, Author, Comment
from validate_email_address import validate_email
from jinja2 import \
  Environment, PackageLoader, select_autoescape

load_dotenv('.env')

PORT = int(os.environ.get('PORT', '8000'))

ENV = Environment(
    loader=PackageLoader('blog', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

class LoggedIn()

class TemplateHandler(tornado.web.RequestHandler):
    def render_template (self, tpl, context):
        template = ENV.get_template(tpl)
        self.write(template.render(**context))

class MainHandler(TemplateHandler):
    def get (self):
        posts = Post.select().order_by(
            Post.created.desc())
        self.render_template("home.html", {'posts': posts})

class LoginHandler(TemplateHandler):
    def get (self):
        self.render_template("signup.html", {})

    def post (self):
        email = self.get_body_argument('email')
        username = self.get_body_argument('username')
        password = self.get_body_argument('password')
        passwordConfirm = self.get_body_argument('passwordConfirm')
        messages = {}
        if Author.select(Author.username).exists() or not validate_email(email) :
            print(validate_email(email), "VALIDATE EMAIL")
            messages['1'] = 'Invalid username/password'
        if password != passwordConfirm:
            messages['2'] = 'Passwords do not match'
        if len(password) < 8:
            messages['3'] = 'Password is too short, must be greater than 8 characters'
        if messages:
            print(messages, 'MESSAGES')
            return self.render_template("signup.html", messages) # Display error messages
        Author.create(email=email, username=username, password=password)
        messages['4'] = 'Login Successfull!'
        print(messages)
        return self.render_template('home.html', messages)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/signup", LoginHandler),
        (r"/static/(.*)", 
        tornado.web.StaticFileHandler, {'path': 'static'}),
    ], autoreload=True)

if __name__ == "__main__":
    tornado.log.enable_pretty_logging()
    app = make_app()
    app.listen(PORT, print('Creating magic on port {}'.format(PORT)))
    tornado.ioloop.IOLoop.current().start()

# http://www.tornadoweb.org/en/stable/guide/security.html
# Use cookies

# FOR FUTURE ADDITION - CREATE USER LOGIN & AUTHENTICATION
# class GAuthLoginHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
#     @tornado.gen.coroutine
#     def get(self):
#         if self.get_current_user():
#             self.redirect('/')
#             return

#         if self.get_argument('code', False):
#             user = yield self.get_authenticated_user(redirect_uri=settings.google_redirect_url,
#                 code=self.get_argument('code'))
#             if not user:
#                 self.clear_all_cookies() 
#                 raise tornado.web.HTTPError(500, 'Google authentication failed')

#             access_token = str(user['access_token'])
#             http_client = self.get_auth_http_client()
#             response =  yield http_client.fetch('https://www.googleapis.com/oauth2/v1/userinfo?access_token='+access_token)
#             if not response:
#                 self.clear_all_cookies() 
#                 raise tornado.web.HTTPError(500, 'Google authentication failed')
#             user = json.loads(response.body)
#             # save user here, save to cookie or database
#             self.set_secure_cookie('trakr', user['email']) 
#             self.redirect('/')
#             return

#         elif self.get_secure_cookie('trakr'):
#             self.redirect('/products')
#             return

#         else:
#             yield self.authorize_redirect(
#                 redirect_uri=settings.google_redirect_url,
#                 client_id=self.settings['google_oauth']['key'],
#                 scope=['email'],
#                 response_type='code',
#                 extra_params={'approval_prompt': 'auto'})
