from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def sync_admin_and_public_data(self):
        super(ResPartner, self).sync_admin_and_public_data()
        for partner in self:
            if partner.is_main_profile and partner.public_profile_id:
                main_partner = partner
                public_partner = partner.public_profile_id
            elif partner.is_public_profile and partner.contact_id:
                main_partner = partner.contact_id
                public_partner = partner

            values = {
                "manual_geolocate": main_partner.manual_geolocate,
                "partner_latitude": main_partner.partner_latitude,
                "partner_longitude": main_partner.partner_longitude,
            }
            public_partner.write(values)