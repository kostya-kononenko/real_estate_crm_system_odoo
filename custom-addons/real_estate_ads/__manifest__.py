{
    "name": "Real Estate",
    "description":"""Real Estate model to show avalible properties""",
    "version": "1.0",
    "author": "Kostiantyn Kononenko",
    "category": "Sales",
    "depends": ["base"],
    "data": [
       "security/ir.model.access.csv",
        "views/property_view.xml",
        "views/property_type_view.xml",
        "views/property_tag_view.xml",
        "views/property_offer_view.xml",
        "views/menu_items.xml",

        # Data files
        "data/estate.property.type.csv",
        "data/estate.property.tag.csv"
    ],
    "installable": True,
    "application": True,
    'license': 'LGPL-3',
}
