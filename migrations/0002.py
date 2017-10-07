import sys
import models
import peewee
from playhouse.migrate import migrate, PostgresqlMigrator

def forward ():
    models.DB.create_tables([models.Author])
    author = peewee.ForeignKeyField(
        models.Author, null=True, to_field=models.Author.id)
    migrator = PostgresqlMigrator(models.DB)
    migrate(
        migrator.add_column('post', 'author_id', author),
    )

def backward ():
    migrator = PostgresqlMigrator(models.DB)
    migrate(
        migrator.drop_column('post', 'author_id'),
    )
    models.Author.drop_table()

if __name__ == '__main__':
    if 'back' in sys.argv:
        backward()
    else:
        forward()