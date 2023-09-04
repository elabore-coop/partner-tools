from odoo import models, fields


class Company(models.Model):
    _inherit = "res.company"

    export_gogocarto_public_fields = fields.Many2many(
        'ir.model.fields',
        relation='ir_model_fields_gogocarto_public',
        domain=[
            ('model_id', '=', 'res.partner'),
            ('name', 'not in', ['id', 'name', 'partner_longitude', 'partner_latitude'])
        ]
    )
