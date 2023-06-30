# post.py
from orm import Model, Database

class Post(Model):

    text = str  # other datatypes: int, float

    def __init__(self, text):
        self.text = text

db = Database('db.sqlite')

Post.db = db
# post = Post('Hola maria').save()
# print(post.id)  # auto generated id 1

objects = Post.manager(db)
print(objects.get(2))
db.commit()

