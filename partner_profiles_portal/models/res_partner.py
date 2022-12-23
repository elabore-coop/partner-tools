# Copyright 2022 Elabore (https://elabore.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = "res.partner"

    edit_structure_main_profile = fields.Boolean(
        string=_("Manage structure's main profile")
    )
    edit_structure_public_profile = fields.Boolean(
        string=_("Manage structure's public profile")
    )
    can_edit_main_profile_ids = fields.Many2many(
        "res.partner",
        relation="res_partner_main_profile_rel",
        column1="partner_id",
        column2="profile_id",
        store=True,
        compute="_compute_can_edit",
        string="Can edit main profile",
    )
    can_edit_public_profile_ids = fields.Many2many(
        "res.partner",
        relation="res_partner_public_profile_rel",
        column1="partner_id",
        column2="profile_id",
        store=True,
        compute="_compute_can_edit",
        string="Can edit public profile",
    )

    @api.depends(
        "other_contact_ids",
        "other_contact_ids.edit_structure_main_profile",
        "other_contact_ids.edit_structure_public_profile",
        "child_ids",
        "child_ids.edit_structure_main_profile",
        "child_ids.edit_structure_public_profile",
    )
    def _compute_can_edit(self):
        for partner in self:
            partner.can_edit_main_profile_ids = partner.child_ids.filtered(
                "edit_structure_main_profile"
            ).mapped("contact_id")
            partner.can_edit_public_profile_ids = partner.child_ids.filtered(
                "edit_structure_public_profile"
            ).mapped("contact_id")