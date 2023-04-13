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

    def print_recipes(self):
        """Return a string with recipes for print"""
        text = ""
        for recipe in self.recipes.all():
            text += f"{recipe['id']} => {recipe['title']}\n"
        return text


class ShoppingList:
    """Class used to generate shopping list"""
    def __init__(self, db_path):
        self.db = TinyDB(db_path, indent=4)
        self.recipes_manager = RecipesManager(self.db)
        self.recipes_list = self.db.table("recipes_list")
        self.shopping_list = self.db.table("shopping_list")

    def _add_recipe(self, recipe, quantity):
        recipe = {"recipe_id": recipe["id"],
                  "quantity": quantity}
        key = self.recipes_list.insert(recipe)
        entry_id = str(key)
        self.recipes_list.update({"id": entry_id}, doc_ids=[key])

    # PUBLICS METHODS CRUD FOR TABLE recipes_list

    # CREATE
    def add_recipe_by_title(self, title: str, quantity: int = 1):
        """Add recipe to the table recipes_list by title"""
        recipe = self.recipes_manager.get_recipe_by_title(title)
        if recipe:
            self._add_recipe(recipe=recipe, quantity=quantity)
            return True
        return False

    def add_recipe_by_id(self, id, quantity):
        """Add recipe to the table recipes_list by id"""
        recipe = self.recipes_manager.get_recipe_by_id(id)
        if recipe:
            self._add_recipe(recipe=recipe, quantity=quantity)
            return True
        return False

    # READ
    def get_recipes_by_title(self, title):
        """Get recipes to the table recipes_list by title"""
        Recipe = Query()
        recipe = self.recipes_manager.get_recipe_by_title(title)
        if recipe:
            recipe_refs = self.recipes_list.search(Recipe.id == recipe["id"])
            return recipe_refs
        return []

    def get_recipes_by_id(self, id):
        Recipe = Query()
        recipe_ref = self.recipes_list.search(Recipe.id == id)
        return recipe_ref

    # UPDATE
    def update_recipe_by_title(self, title, quantity):
        """Update a recipe from the table recipes_list by title"""
        Recipe = Query()
        recipe = self.recipes_manager.get_recipe_by_title(title)
        if recipe:
            recipe_ref = self.recipes_list.get(doc_id=recipe["id"])
            recipe_ref.update({"quantity": quantity})
            return True
        return False

    def update_recipe_by_id(self, id, quantity):
        """Update a recipe from the table recipes_list by id"""
        self.recipes_list.update({"quantity": quantity}, doc_ids=[id])

    # DELETE
    def delete_recipe_by_title(self, title: str):
        """Delete a recipe from the table recipes_list by title"""
        Recipe = Query()
        recipe = self.recipes_manager.get(Recipe.title == title)
        if recipe:
            self.recipes_list.remove(doc_ids=recipe["id"])
            return True
        return False

    def delete_recipe_by_id(self, id):
        """Delete a recipe from the table recipes_list by id"""
        self.recipes_list.remove(doc_ids=[id])

    def generate(self, file=None):
        """Generate a list of ingredients with quantities"""
        # TODO : permettre d'ajouter plusieurs listes
        self.db.drop_table("shopping_list")
        shopping_list = {}
        for recipe_ref in self.recipes_list.all():
            recipe = self.recipes_manager.get_recipe_by_id(recipe_ref["recipe_id"])
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

    def print_recipes(self):
        """Return a string with recipes for print"""
        text = ""
        for recipe in self.recipes_list.all():
            id = recipe['id']
            name = self.recipes_manager.get_recipe_by_id(recipe["recipe_id"])["name"]
            text += f"{id} => {name}\n"


class ConsoleApp:
    def __init__(self, db_path):
        self.shopping_list = ShoppingList(db_path=db_path)
        self.recipe_manager = self.shopping_list.recipes_manager

    # CHOICES METHODS

    # Database

    # 1
    def add_recipe_to_db(self):
        print("Ajout d'une recette à la base de données")
        title = input("Entrez le titre de la recette: ")
        ingredients = []
        save = True
        while True:
            ingredient_name = input("Entrez le nom de l'ingrédient ('s' pour sauvegarder, 'q' pour quitter): ")
            if ingredient_name.lower() == "s":
                break
            elif ingredient_name.lower() == "q":
                save = False
                break
            quantity = input("Entrez la quantité: ")
            unit = input("Entrez l'unité: ")
            ingredient = Ingredient(ingredient_name, quantity, unit)
            ingredients.append(ingredient)
            print("Ingrédient ajouté")

        if save:
            self.recipe_manager.add_recipe(title, ingredients)
            print("Recette ajoutée.")
        else:
            print("Recette non sauvegardée")

    # 2
    def delete_recipe_from_db(self):
        print("Suppression d'une recette de la base de données")
        print(self.recipe_manager.print_recipes())
        recipe_id = input("Entrez l'ID de la recette à supprimer: ")
        self.recipe_manager.delete_recipe_by_id(int(recipe_id))
        print("Recette supprimée de la base de données.")

    def show_recipes_from_db(self):
        print("Recettes de la base de données")
        print(self.recipe_manager.print_recipes())
        input("Appuyez sue Entrée pour continuer")

    # Shopping list

    # 4
    def add_recipe_to_list(self):
        print("Ajout d'une recette à la liste de courses")
        print(self.recipe_manager.print_recipes())
        recipe_id = input("Entrez l'ID de la recette: ")
        quantity = int(input("Entrez la quantité: "))
        self.shopping_list.add_recipe_by_id(recipe_id, quantity)
        print("Recette ajoutée à la liste de courses.")

    # 5
    def delete_recipe_from_list(self):
        print("Suppression d'une recette de liste de courses")
        print(self.shopping_list.print_recipes())
        recipe_id = input("Entrez l'ID de la recette à supprimer: ")
        self.shopping_list.delete_recipe_by_id(recipe_id)
        print("Recette supprimée de la liste de courses.")

    # 6
    def show_recipes_from_list(self):
        print("Recettes de la liste de courses")
        print(self.shopping_list.print_recipes())
        input("Appuyez sue Entrée pour continuer")

    # 7
    def generate_shopping_list(self):
        print("Génération de la liste de courses")
        path = input("Entrez le nom du fichier ou enregistrer la liste de courses (optionnel) : ")
        list_ = self.shopping_list.generate(path + ".txt" if path else None)
        print("Liste de courses générée")
        print("\n".join(list_))

    # END OF CHOICES

    def run(self):
        """Principal method to launch console mode app"""
        while True:
            print("=== PyShopping ===")
            print("1. Ajouter une recette à la base de donnée")
            print("2. Supprimer une recette de la base de donnée")
            print("3. Afficher les de la base de donnée")
            print("4. Ajouter une recette à la liste de courses")
            print("5. Supprimer une recette de la liste de courses")
            print("6. Afficher les recettes de la liste de courses")
            print("7. Générer la liste de courses")
            print("8. Quitter")
            choice = input("Entrez votre choix (1-6): ")
            # Database
            if choice == "1":
                self.add_recipe_to_db()
            elif choice == "2":
                self.delete_recipe_from_db()
            elif choice == "3":
                self.show_recipes_from_db()
            # Shopping list
            elif choice == "4":
                self.add_recipe_to_list()
            elif choice == "5":
                self.delete_recipe_from_list()
            elif choice == "6":
                self.show_recipes_from_list()
            # Generate
            elif choice == "7":
                self.generate_shopping_list()
            # Quit
            elif choice == "8":
                print("Merci d'utiliser PyShopping. Au revoir!")
                break
            else:
                print("Choix invalide. Veuillez choisir un numéro entre 1 et 6.")



if __name__ == '__main__':
    path = "test.json"
    list_path = "list.txt"

    app = ConsoleApp(path)
    app.run()

    '''pasta1 = Ingredient("pasta", 500, "g")
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

    print(list_.generate(list_path))'''
