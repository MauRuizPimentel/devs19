{
    "name": "Contact Card Extend",
    "version": "19.0.1.0.0",
    "category": "Contacts",
    "summary": "Adds birthdate/age to contacts with a corporate contact card widget",
    "author": "Mosent Group",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "data/ir_cron_data.xml",
        "views/res_partner_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "res_partner_extend/static/src/xml/contact_card.xml",
            "res_partner_extend/static/src/js/contact_card.js",
            "res_partner_extend/static/src/scss/contact_card.scss",
        ],
    },
    "installable": True,
    "application": False,
}
