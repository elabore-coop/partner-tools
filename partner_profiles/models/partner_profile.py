# Copyright 2022 Elabore (https://elabore.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class PartnerProfile(models.Model):
    _name = "partner.profile"
    _description = "Partner profile to differentiate the attached partner entries"

    name = fields.Char(string="Name", required=True, translate=True, readonly=False)
    ref = fields.Char(string="Ref", required=True, translate=False, readonly=False)

    # TODO: block unlink method.
