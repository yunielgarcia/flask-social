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
            with DATABASE.transaction():
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

    def following(self):
        """the user we are following"""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """the user following the current user"""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
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


class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE
        indexes = (
            (('from_user', 'to_user'), True),
        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()
