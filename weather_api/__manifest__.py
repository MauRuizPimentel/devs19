{
    "name": "Weather API",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "summary": "On-demand current weather lookup via OpenWeatherMap",
    "author": "Mosent Group",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "wizards/weather_lookup_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "weather_api/static/src/xml/weather_result_widget.xml",
            "weather_api/static/src/js/weather_result_widget.js",
            "weather_api/static/src/scss/weather_result_widget.scss",
        ],
    },
    "installable": True,
    "application": False,
}
