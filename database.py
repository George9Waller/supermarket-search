from datetime import datetime
from peewee import SqliteDatabase, Model, PrimaryKeyField, DateTimeField, CharField, FloatField, TextField, ManyToManyField, BooleanField

db = SqliteDatabase('supermarket_search.db')

class BaseModel(Model):
    id = PrimaryKeyField()
    created = DateTimeField(default=datetime.now)
    modified = DateTimeField()

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)


class Category(BaseModel):
    sainsburys_id = CharField()
    name = CharField()


class Ingredient(BaseModel):
    name = CharField(unique=True)


class Product(BaseModel):
    sainsburys_id = CharField()
    name = CharField()
    price = FloatField()
    average_rating = FloatField(null=True)
    description = TextField()
    brand = CharField()
    detail_url = CharField()
    is_available = BooleanField(default=True)
    categories = ManyToManyField(Category, backref='products')
    weight_in_g = FloatField(null=True)
    kcal_per_100g = FloatField()
    fat_per_100g = FloatField()
    saturates_per_100g = FloatField()
    carbs_per_100g = FloatField()
    sugar_per_100g = FloatField()
    fibre_per_100g = FloatField()
    protein_per_100g = FloatField()
    salt_per_100g = FloatField()
    ingredients = ManyToManyField(Ingredient, backref='products')
