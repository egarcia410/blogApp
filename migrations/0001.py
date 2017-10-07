import models

def forward ():
    models.DB.create_tables([models.Author, models.Comment, models.Post])

if __name__ == '__main__':
    forward()