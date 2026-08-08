from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

from ..models.gemini_client import GeminiClient


class RecipeGenerateWizard(models.TransientModel):
    _name = "recipe.generate.wizard"
    _description = "Generate Recipe Wizard"

    food_name = fields.Char(string="Food Name", required=True)

    def action_generate_recipe(self):
        self.ensure_one()
        if not self.food_name or not self.food_name.strip():
            raise UserError(_("Please enter a food name before generating a recipe."))

        client = GeminiClient(self.env)
        recipe_data = client.generate_recipe(self.food_name)
        image = client.generate_image(recipe_data["name"])

        values = {
            "name": recipe_data["name"],
            "instructions": recipe_data["instructions"],
            "preparation_time": recipe_data["preparation_time"],
            "difficulty": recipe_data["difficulty"],
        }
        if image:
            values["image"] = image

        recipe = self.env["recipe.recipe"].create(values)

        return {
            "type": "ir.actions.act_window",
            "res_model": "recipe.recipe",
            "res_id": recipe.id,
            "view_mode": "form",
            "target": "current",
        }
