# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Partner Comcom',
    'summary': "Ajoute la communauté de commune commme champ du partnenaire",
    'version': "16.0.1.0.0",
    'author': "Elabore",
    'license': "AGPL-3",
    'maintainer': 'Clément Thomas',
    'category': 'Extra Tools',
    'website': 'https://odoo-community.org/',
    'depends': ['contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_country_comcom_views.xml',
    ],
    'auto_install': False,
    'installable': True,
}
