# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResCountryComcom(models.Model):
    
    _name = 'res.country.comcom'

    name = fields.Text('Nom')