import datetime
import os
import peewee
import bcrypt
from playhouse.db_url import connect
from playhouse.fields import PasswordField
import markdown2

DB = connect(
    os.environ.get(
        'DATABASE_URL',
        'postgres://localhost:5432/blog'
  )
)

class BaseModel (peewee.Model):
    class Meta:
        database = DB

class Author (BaseModel):
    email = peewee.CharField(null=False, unique=True)
    username = peewee.CharField(null=False, unique=True)
    password = PasswordField(null=False) # Needs constraint > 7 
    likes = peewee.IntegerField(default=0)

    def __str__ (self):
        return self.name

class Comment (BaseModel):
    author = peewee.ForeignKeyField(Author, null=False)
    comment = peewee.TextField(null=False)
    created = peewee.DateTimeField(
                default=datetime.datetime.utcnow)

    def html(self):
        return markdown2.markdown(self.body)

    def __str__(self):
        return self.id

class Post (BaseModel):
    author = peewee.ForeignKeyField(Author, null=False)
    comment = peewee.ForeignKeyField(Comment, null=False)
    title = peewee.CharField(max_length=60, null=False)
    category = peewee.CharField(max_length=60, null=False)
    post = peewee.TextField(null=False)
    likes = peewee.IntegerField() # Defaults at 0, not NULL
    created = peewee.DateTimeField(
                default=datetime.datetime.utcnow)

    def html(self):
        return markdown2.markdown(self.body)

    def __str__(self):
        return self.id

