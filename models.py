from peewee import *
import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('social.db')


class User(UserMixin, Model):  # From more to less specific
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)  # no now() otherwise will have the date when the file
    # is loaded
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        # And since order_by is a tuple (you can use a list if you want),
        # we have to include that trailing comma if there's only one tuple member.
        order_by = ('-joined_at',)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=admin
            )
        except IntegrityError:  # Meaning a field already exits
            raise ValueError("User already exists")

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user == self)
        )


class Post(Model):
    timestamp = DateTimeField(
        default=datetime.datetime.now)
    user = ForeignKeyField(
        model=User,
        backref='posts'
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User], safe=True)
    DATABASE.close()
