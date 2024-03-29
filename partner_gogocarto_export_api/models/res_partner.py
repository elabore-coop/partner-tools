from odoo import models, fields


class ResPartner(models.Model):
    """ Inherits partner, adds Gogocarto fields in the partner form, and functions"""
    _inherit = 'res.partner'

    in_gogocarto = fields.Boolean('Export to Gogocarto')

    def _get_gogocarto_domain(self, company_id):
        # To OVERRIDE in sub_modules to customize the partner selection
        return [('in_gogocarto', '=', True)]

    def _get_generic_parser(self, fields):
        parser = []
        for field in fields:
            if field.ttype in [
                    "boolean",
                    "char",
                    "integer",
                    "monetary",
                    "text",
                    "selection",
                    "float",
                    "date_time",
                    "date",
                    "html"]:
                parser.append(field.name)
            elif field.ttype in ["many2one", "one2many", "many2many"]:
                parser.append((field.name, ['id', 'name']))
            elif field.ttype == "binary":
                continue
            else:
                continue
        return parser

    def _get_gogocarto_parser(self, company_id):
        fields = self._get_export_fields(company_id)
        parser = self._get_generic_parser(fields)
        return parser

    def _get_export_fields(self, company_id):
        CompanySudo = self.env['res.company'].sudo().search([('id', '=', company_id)])
        default_fields = self.env['ir.model.fields'].sudo().search([
            ('model_id', '=', 'res.partner'),
            ('name', 'in', ['id', 'name', 'partner_longitude', 'partner_latitude'])])
        company_fields = CompanySudo.export_gogocarto_fields
        export_fields = default_fields | company_fields
        return export_fields
