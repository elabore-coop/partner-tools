# Copyright 2022 Elabore (https://elabore.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class CreatePositionProfile(models.TransientModel):
    _inherit = "create.position.profile"

    edit_structure_profiles = fields.Boolean(
        string="Manage structure's profiles"
    )    

    def _compute_position_profile_values(self):
        values = super(CreatePositionProfile, self)._compute_position_profile_values()
        values.update(
            {
                "edit_structure_profiles": self.edit_structure_profiles
            }
        )
        return values