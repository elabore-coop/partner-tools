# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Partner Skills',
    'summary': "Add skill managment on partners",
    'version': "16.0.1.0.0",
    'author': "Clément Thomas",
    'license': "AGPL-3",
    'maintainer': 'Elabore',
    'category': 'Partner Tools',
    'website': 'https://odoo-community.org/',
    'depends': ['contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_skill_views.xml',
        'views/res_partner_views.xml',
    ],
    'auto_install': False,
    'installable': True,
}
