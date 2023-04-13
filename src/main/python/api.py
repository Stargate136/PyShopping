"""
TODO :
- Une classe pour les ingredients
- Une classe pour le gestionaire de recettes
- Une classe pour la génération de la liste de courses
"""
from pprint import pprint
from typing import List

from tinydb import TinyDB, Query


# TODO : normaliser les retours des méthodes

class Ingredient:
    """ingredients used in recipes"""

    def __init__(self, name: str, quantity: int, unit: str):
        self.name = name
        self.quantity = quantity
        self.unit = unit

    def __add__(self, other):
        """Check if they are the same ingredients and add the quantities"""
        if self.name != other.name:
            raise ValueError("Ingredients must have the same name to be added")
        elif self.unit != other.unit:
            raise ValueError("Ingredients must have the same unit to be added")
        else:
            return Ingredient(name=self.name,
                              quantity=self.quantity + other.quantity,
                              unit=self.unit)

    def __str__(self):
        return f"{self.name} -> {self.quantity} {self.unit}"

    def __repr__(self):
        return f"Ingredient({self.name}, {self.quantity} {self.unit})"

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_json(cls, data):
        return cls(**data)


class RecipesManager:
    """Recipes manager that use TinyDB to store data"""

    def __init__(self, db):
        self.recipes = db.table("recipes")

    def _add(self, title: str, ingredients: List[Ingredient]):
        """Private method that add an id to the recipe"""
        recipe = self._recipe_converter(recipe={"title": title,
                                               "ingredients": ingredients})
        key = self.recipes.insert(recipe)
        recipe_id = str(key)
        self.recipes.update({"id": recipe_id}, doc_ids=[key])

    @staticmethod
    def _recipe_decoder(recipe: dict):
        recipe["ingredients"] = [Ingredient.from_json(ingredient) for ingredient in recipe["ingredients"]]
        return recipe

    @staticmethod
    def _recipe_converter(recipe: dict):
        recipe["ingredients"] = [ingredient.to_dict() for ingredient in recipe["ingredients"]]
        return recipe

    # PUBLICS METHODS CRUD

    # CREATE
    def add_recipe(self, title: str, ingredients: List[Ingredient]):
        """Add recipe to the database"""
        Recipe = Query()
        existing_recipe = self.recipes.get(Recipe.title == title)
        if existing_recipe:
            title_list = title.split("_")
            if len(title_list) == 1:
                title_list.append(0)
            title_list[1] = str(int(title_list[1]) + 1).zfill(2)
            self.add_recipe(title="_".join(title_list),
                            ingredients=ingredients)
        else:
            self._add(title=title, ingredients=ingredients)

    # READ
    def get_recipe_by_id(self, id):
        Recipe = Query()
        recipe = self.recipes.get(Recipe.id == id)
        if recipe:
            recipe = self._recipe_decoder(recipe)
        return recipe

    def get_recipe_by_title(self, title: str):
        """Get a recipe from the database by title"""
        Recipe = Query()
        recipe = self.recipes.get(Recipe.title == title)
        if recipe:
            recipe = self._recipe_decoder(recipe)
        return recipe

    # UPDATE
    def update_recipe_by_title(self, title: str, ingredients: List[Ingredient]):
        """Update a recipe in the database"""
        Recipe = Query()
        recipe = self._recipe_converter(recipe={"title": title,
                                                "ingredients": ingredients})
        self.recipes.update(recipe, Recipe.title == title)

    # DELETE
    def delete_recipe_by_title(self, title: str):
        """Delete a recipe from the database by title"""
        Recipe = Query()
        self.recipes.remove(Recipe.title == title)

    def delete_recipe_by_id(self, id):
        """Delete a recipe from the database by id"""
        self.recipes.remove(doc_ids=[id])


    def __repr__(self):
        text = ""
        for recipe in self.recipes.all():
            text += f"{recipe['id']} => {recipe['title']}\n"
        return text


class ShoppingList:
    def __init__(self, db_path):
        self.db = TinyDB(db_path, indent=4)
        self.recipes = RecipesManager(self.db)
        self.recipes_list = self.db.table("recipes_list")
        self.shopping_list = self.db.table("shopping_list")

    def add_recipe_by_title(self, title: str, quantity: int = 1):
        """Add recipe to the table shopping_list by title"""
        recipe = self.recipes.get_recipe_by_title(title)
        if recipe:
            recipe = {"recipe_id": recipe["id"],
                      "quantity": quantity}
            self.recipes_list.insert(recipe)
        else:
            raise ValueError(f"Recipe {title} doesn't exist")

    def add_recipe_by_id(self, id, quantity):
        """Add recipe to the table shopping_list by id"""
        recipe = self.recipes.get_recipe_by_id(id)
        if recipe:
            recipe = {"recipe_id": id,
                      "quantity": quantity}
            self.recipes_list.insert(recipe)
            return True
        return False

    def generate(self, file=None):
        """Generate a list of ingredients with quantities"""
        # TODO : permettre d'ajouter plusieurs listes
        self.db.drop_table("shopping_list")
        shopping_list = {}
        for recipe_ref in self.recipes_list.all():
            recipe = self.recipes.get_recipe_by_id(recipe_ref["recipe_id"])
            for ingredient in recipe["ingredients"]:
                key = (ingredient.name, ingredient.unit)
                if key in shopping_list:
                    shopping_list[key] += ingredient.quantity * recipe_ref["quantity"]
                else:
                    shopping_list[key] = ingredient.quantity * recipe_ref["quantity"]

        for key, value in shopping_list.items():
            ingredient = {"name": key[0],
                          "quantity": f"{value} {key[1]}"}
            self.shopping_list.insert(ingredient)

        list_ = [(ingredient["name"], ingredient["quantity"]) for ingredient in self.shopping_list.all()]
        if file:
            with open(file, "w") as f:
                f.writelines([f"{row[0]} => {row[1]}\n" for row in list_])
        return list_


if __name__ == '__main__':
    path = "test.json"
    list_path = "list.txt"

    pasta1 = Ingredient("pasta", 500, "g")
    pasta2 = Ingredient("pasta", 600, "g")
    milk = Ingredient("milk", 1, "l")
    tomato = Ingredient("tomato", 500, "g")

    """pasta1 += pasta2

    manager = RecipesManager(path)

    """

    list_ = ShoppingList(path)
    list_.recipes.add_recipe("pasta bolo", [pasta1, tomato])
    list_.recipes.add_recipe("pasta", [pasta2, milk])

    list_.add_recipe_by_title("pasta bolo")
    list_.add_recipe_by_title("pasta")
    pprint(list_.recipes_list.all())

    print(list_.generate(list_path))
