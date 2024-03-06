# Copyright 2022 Elabore (https://elabore.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class CreatePositionProfile(models.TransientModel):
    _name = "create.position.profile"
    _description = "create Position Profile"

    @api.model
    def _default_is_company(self):
        return self.env['res.partner'].browse(self._context.get('active_ids')).is_company

    @api.model
    def _default_structure_id(self):
        current_partner_id = self.env['res.partner'].browse(self._context.get('active_ids'))
        if current_partner_id.is_company:
            return current_partner_id.id
        else:
            return None

    @api.model
    def _default_partner_id(self):
        current_partner_id = self.env['res.partner'].browse(self._context.get('active_ids'))
        if not current_partner_id.is_company:
            return current_partner_id.id
        else:
            return None

    is_company = fields.Boolean('Is Company', default=_default_is_company)
    structure_id = fields.Many2one('res.partner', string='Structure', domain="[('is_company', '=', True), ('is_main_profile', '=', True)]", default=_default_structure_id )
    partner_id = fields.Many2one('res.partner', string='Person', domain="[('is_company', '=', False), ('is_main_profile', '=', True)]", default=_default_partner_id)
    function = fields.Char('Function')
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    comment = fields.Text('Notes')

    def _compute_position_profile_values(self):
        values= {
            "contact_id": self.partner_id.id,
            "parent_id": self.structure_id.id,
            "function": self.function,
            "name": self.partner_id.name,
            "phone": self.phone,
            "email": self.email,
            "comment" : self.comment,
            "partner_profile": self.env.ref("partner_profiles.partner_profile_position").id
        }
        return values


    def create_position_profile(self):
        values = self._compute_position_profile_values()
        position_partner_id = self.env["res.partner"].create(values)
        view = self.env.ref("base.view_partner_form")
        return {
                "name": "Position Partner created",
                "view_type": "form",
                "view_mode": "form",
                "view_id": view.id,
                "res_model": "res.partner",
                "type": "ir.actions.act_window",
                "res_id": position_partner_id.id,
                "context": self.env.context,
            }