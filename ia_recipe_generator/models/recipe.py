from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

from .default_recipe_image import DEFAULT_RECIPE_IMAGE_BASE64


class Recipe(models.Model):
    _name = "recipe.recipe"
    _description = "Recipe"

    name = fields.Char(string="Name", required=True)
    instructions = fields.Html(string="Preparation Instructions")
    preparation_time = fields.Integer(string="Preparation Time (min)")
    difficulty = fields.Selection(
        [
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
        ],
        string="Difficulty",
        required=True,
        default="easy",
    )
    image = fields.Image(string="Image", default=DEFAULT_RECIPE_IMAGE_BASE64)

    @api.constrains("preparation_time")
    def _check_preparation_time(self):
        for recipe in self:
            if recipe.preparation_time < 0:
                raise ValidationError(_("Preparation time cannot be negative."))
