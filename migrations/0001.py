import models

def forward ():
    models.DB.create_tables([models.Users, models.Comments, models.Posts])

if __name__ == '__main__':
    forward()