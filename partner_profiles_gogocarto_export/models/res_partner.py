from odoo import models
import logging


class ResPartner(models.Model):
    """ Inherits partner, adds Gogocarto public fields in the partner form, and functions"""
    _inherit = 'res.partner'

    def _get_gogocarto_domain(self, company_id):
        # To OVERRIDE in sub_modules to customize the partner selection
        res = super(ResPartner, self)._get_gogocarto_domain(company_id)
        res.extend([('is_main_profile', '=', True)])
        return res

    def _get_gogocarto_parser(self, company_id):
        parser = super(ResPartner, self)._get_gogocarto_parser(company_id)
        public_fields = self._get_export_public_fields(company_id)
        public_parser = self._get_generic_parser(public_fields)
        parser.append(("public_profile_id", public_parser))
        return parser

    def _get_export_public_fields(self, company_id):
        CompanySudo = self.env['res.company'].sudo().search([('id', '=', company_id)])
        default_fields = self.env['ir.model.fields'].sudo().search([
            ('model_id', '=', 'res.partner'),
            ('name', 'in', ['id', 'name', 'partner_longitude', 'partner_latitude'])])
        company_fields = CompanySudo.export_gogocarto_public_fields
        export_fields = default_fields | company_fields
        return export_fields
