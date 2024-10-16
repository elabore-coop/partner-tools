# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    
    _inherit = 'res.partner'

    comcom_ids = fields.Many2many('res.country.comcom')