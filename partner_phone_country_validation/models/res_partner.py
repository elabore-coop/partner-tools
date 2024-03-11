from odoo import api, models, _
from odoo.addons.partner_phone_country_validation.tools.get_country_from_phone_number import get_country_from_phone_number
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.validation.mixin']

    @api.constrains('country_id')
    def _check_country_id(self):
        if not self.country_id and self.phone:
            raise ValidationError(_('You must set a country for the phone number'))

    @api.onchange('phone', 'country_id', 'company_id')
    def _onchange_phone_validation(self):
        # If no country is found, we define the country based on the beginning of the number
        if not self.country_id and self.phone:
            self.country_id = self.env['res.country'].search(
                [('code', '=', get_country_from_phone_number(self.phone))], limit=1
            )
        if self.phone:
            if self.phone.startswith("00") or self.phone.startswith('+'):
                return
            self.phone = self.phone_format(self.phone)

    @api.onchange('mobile', 'country_id', 'company_id')
    def _onchange_mobile_validation(self):
        # If no country is found, we define the country based on the beginning of the number
        if not self.country_id and self.mobile:
            self.country_id = self.env['res.country'].search(
                [('code', '=', get_country_from_phone_number(self.mobile))], limit=1
            )
        if self.mobile:            
            if self.mobile.startswith("00") or self.mobile.startswith('+'):
                return
            self.mobile = self.phone_format(self.mobile)
