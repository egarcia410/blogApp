import sys
import models
import peewee
from playhouse.migrate import migrate, PostgresqlMigrator

def forward ():
    models.DB.create_tables([models.Comment])
    comment = peewee.ForeignKeyField(
        models.Comment, null=True, to_field=models.Comment.id)
    migrator = PostgresqlMigrator(models.DB)
    migrate(
        migrator.add_column('post', 'comment_id', comment),
    )

def backward ():
    migrator = PostgresqlMigrator(models.DB)
    migrate(
        migrator.drop_column('post', 'comment_id'),
    )
    models.Author.drop_table()

if __name__ == '__main__':
    if 'back' in sys.argv:
        backward()
    else:
        forward()