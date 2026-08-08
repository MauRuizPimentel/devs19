{
    "name": "AI Recipe Generator",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "summary": "Generate recipes on demand from a dish name using Google's Gemini API",
    "author": "Mosent Group",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/recipe_views.xml",
        "views/recipe_generate_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ia_recipe_generator/static/src/img/recipe_placeholder.svg",
            "ia_recipe_generator/static/src/xml/recipe_preview_widget.xml",
            "ia_recipe_generator/static/src/js/recipe_preview_widget.js",
            "ia_recipe_generator/static/src/scss/recipe_preview_widget.scss",
        ],
    },
    "installable": True,
    "application": False,
}
