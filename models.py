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
    username = peewee.CharField(null=False, unique=True)
    hashed_password = peewee.CharField(null=False)
    likes = peewee.IntegerField(default=0)

    def __str__ (self):
        return self.name

class Comments (BaseModel):
    author = peewee.ForeignKeyField(Users, null=False)
    comment = peewee.TextField(null=False)
    created = peewee.DateTimeField(
                default=datetime.datetime.utcnow)

    def html(self):
        return markdown2.markdown(self.body)

    def __str__(self):
        return self.id

class Posts (BaseModel):
    author = peewee.ForeignKeyField(Users, null=False)
    comment = peewee.ForeignKeyField(Comments, null=False)
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

