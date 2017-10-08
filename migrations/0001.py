import models

def forward ():
    models.DB.create_tables([models.Users, models.Posts, models.Comments, models.Likes])

if __name__ == '__main__':
    forward()