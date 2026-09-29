{
    'name': 'Empleados - Nuevos campos',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Employees',
    'summary': 'CURP, catálogo de puesto y modalidad en el formulario de empleados',
    'description': """
Agrega la pestaña Nuevos campos al formulario de empleados
y el catálogo catPuiesto (many2one) en el menú de Empleados.
    """,
    'author': 'Samuel',
    'license': 'LGPL-3',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_cat_puesto_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
}
