from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    manual_geolocate = fields.Boolean('Geolocate yourself')

    @api.multi
    def geo_localize(self):
        partners = self.filtered(lambda a: a.manual_geolocate == False)
        return super(ResPartner, partners).geo_localize()