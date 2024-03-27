from odoo import api, models, _
from odoo.addons.partner_phone_country_validation.tools.get_country_from_phone_number import get_country_from_phone_number
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.validation.mixin']

    @api.constrains('country_id','phone','mobile')
    def _check_country_id(self):
        if not self.country_id and (self.phone or self.mobile):
            raise ValidationError(_('You must set a country for the phone number'))
        
    @api.onchange('country_id')
    def _onchange_country(self):
        self.format_mobile_from_country()
        self.format_phone_from_country()

    def format_phone_from_country(self):
        if self.phone:
            if not self.phone.startswith("00") and not self.phone.startswith('+'):                
                self.phone = self.phone_format(self.phone)

    def format_mobile_from_country(self):
        if self.mobile:
            if not self.mobile.startswith("00") and not self.mobile.startswith('+'):                
                self.mobile = self.phone_format(self.mobile)

    def set_country_from_phone_number(self, phone_number):
        country = self.env['res.country'].search(
            [('code', '=', get_country_from_phone_number(phone_number))], limit=1
        )
        if not country and not self.country_id:
            self.country_id = self.env.company.country_id
        if country and not self.country_id:
            self.country_id = country

    @api.onchange('phone')
    def _onchange_phone_validation(self):
        # If no country is found, we define the country based on the beginning of the number
        if self.phone:
            self.set_country_from_phone_number(self.phone)
            self.format_phone_from_country()
        

    @api.onchange('mobile')
    def _onchange_mobile_validation(self):
        # If no country is found, we define the country based on the beginning of the number
        if self.mobile:
            self.set_country_from_phone_number(self.mobile)
            self.format_mobile_from_country()