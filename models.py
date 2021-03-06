import datetime
import os
import peewee
import bcrypt
from playhouse.db_url import connect
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

class Users (BaseModel):
    email = peewee.CharField(null=False, unique=True)
    username = peewee.CharField(null=False, unique=False)
    hashed_password = peewee.CharField(null=False)

class Posts (BaseModel):
    user = peewee.ForeignKeyField(Users, null=False)
    title = peewee.CharField(max_length=60, null=False)
    category = peewee.CharField(max_length=60, null=False)
    post = peewee.TextField(null=False)
    created = peewee.DateTimeField(
                default=datetime.datetime.utcnow)

    def html(self):
        return markdown2.markdown(self.body)

class Comments (BaseModel):
    user = peewee.ForeignKeyField(Users, null=False)
    post = peewee.ForeignKeyField(Posts, null=False)
    comment = peewee.TextField(null=False)
    created = peewee.DateTimeField(
                default=datetime.datetime.utcnow)

    def html(self):
        return markdown2.markdown(self.body)

class Likes (BaseModel):
    user = peewee.ForeignKeyField(Users, null=True)
    post = peewee.ForeignKeyField(Posts, null=True)
    created = peewee.DateTimeField(
                default=datetime.datetime.utcnow)