# Copyright 2022 Elabore (https://elabore.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = "res.partner"

    edit_structure_profiles = fields.Boolean(
        string="Manage structure's profiles"
    )
    can_edit_structure_profiles_ids = fields.Many2many(
        "res.partner",
        relation="res_partner_main_profile_rel",
        column1="partner_id",
        column2="profile_id",
        store=True,
        compute="_compute_can_read_edit",
        string="Can edit struture profiles",
    )
    child_main_contact_ids = fields.Many2many(
        "res.partner",
        relation="res_partner_child_contacts_rel",
        column1="partner_id",
        column2="profile_id",
        store=True,
        compute="_compute_can_read_edit",
        string="Can read structure profiles",
    )
    odoo_user_id = fields.Many2one(
        "res.users",
        compute="_compute_odoo_user_id",
        string="Associated Odoo user",
        store=True,
    )

    @api.depends(
        "other_contact_ids",
        "other_contact_ids.edit_structure_profiles",
        "structure_position_ids",
        "structure_position_ids.edit_structure_profiles",
    )
    def _compute_can_read_edit(self):
        for partner in self:
            partner.can_edit_structure_profiles_ids = partner.structure_position_ids.filtered(
                "edit_structure_profiles"
            ).mapped("contact_id")
            partner.child_main_contact_ids = partner.structure_position_ids.mapped("contact_id")

    @api.depends("user_ids")
    def _compute_odoo_user_id(self):
        for partner in self:
            partner.odoo_user_id = self.env["res.users"].search(
                [("partner_id", "=", partner.id)], limit=1
            )