# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models



class ResPartner(models.Model):
    _inherit = 'res.partner'

    skill_ids = fields.Many2many('res.partner.skill', string='Skills')