# Copyright 2022 Elabore (https://elabore.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = "res.partner"

    to_migrate = fields.Boolean()
    partner_profile = fields.Many2one(
        "partner.profile",
        string="Partner profile",
        required=False,
        translate=False,
        readonly=False,
    )
    contact_id = fields.Many2one(ondelete="cascade")
    is_main_profile = fields.Boolean(compute="_compute_profile_booleans", store=True)
    is_public_profile = fields.Boolean(compute="_compute_profile_booleans", store=True)
    is_position_profile = fields.Boolean(
        compute="_compute_profile_booleans", store=True
    )
    has_position = fields.Boolean(compute="_compute_has_position", store=True)

    # If current partner is Main partner, this field indicates what its public profile is.
    public_profile_id = fields.Many2one(
        "res.partner",
        compute="_compute_public_profile_id",
        string="Public profile",
        store=True,
    )

    # If current partner is Main partner, this field indicates what its position profiles are.
    other_contact_ids = fields.One2many(
        domain=[("is_position_profile", "=", True)]
    )

    structure_position_ids = fields.One2many('res.partner', 'parent_id', string="Structure's positions", domain=[('active', '=', True), ('is_position_profile', '=', True)])

    @api.depends("partner_profile", "other_contact_ids")
    def _compute_profile_booleans(self):
        for partner in self:
            partner.is_main_profile = (
                partner.partner_profile.ref == "partner_profile_main"
            )
            partner.is_public_profile = (
                partner.partner_profile.ref == "partner_profile_public"
            )
            partner.is_position_profile = (
                partner.partner_profile.ref == "partner_profile_position"
            )

    @api.depends("other_contact_ids")
    def _compute_has_position(self):
        for partner in self:
            partner.has_position = len(partner.other_contact_ids) > 0

    @api.depends("partner_profile", "contact_id")
    def _compute_public_profile_id(self):
        for partner in self:
            if partner.is_main_profile:
                partner.public_profile_id = self.env["res.partner"].search(
                    [
                        ("contact_id", "=", partner.id),
                        ("is_public_profile", "=", True),
                    ],
                    limit=1,
                )

    @api.onchange("type")
    def _onchange_type(self):
        self.contact_type = "standalone"
        self.partner_profile = False
        if self.type == "contact" and self.parent_id:
            _logger.debug("Contact type: attached")
            # A contact with parent_id is partner_profile=Position, and contact_type=attached
            position_profile = self.env.ref("partner_profiles.partner_profile_position")
            self.contact_type = "attached"
            self.partner_profile = position_profile.id

    @api.onchange("is_company")
    def _onchange_is_company(self):
        for partner in self:
            if partner.is_main_profile:
                if partner.has_position or partner.child_ids.filtered(lambda c: c.is_position_profile):
                    raise UserError("You can not modify the partner company type when the parner has postion profiles associated. Please remove the position profiles before retrying.")
                if partner.public_profile_id:
                    # public_partner = self.env["res.partner"].browse(partner.public_profile_id)[0]
                    values = {
                        "is_company": partner.is_company,
                    }
                    partner.public_profile_id.sudo().write(values)

    @api.model
    def create(self, vals):
        """Assume if not type, default is contact"""
        vals["type"] = vals.get("type", "contact")
        profile_position = self.env.ref("partner_profiles.partner_profile_position").id
        profile_main = self.env.ref("partner_profiles.partner_profile_main").id
        if vals["type"] == "contact":
            """When creating, if partner_profile is not defined by a previous process, the defaut value is Main"""
            if not vals.get("partner_profile"):
                vals["partner_profile"] = profile_main
            # If we create a partner type position search if one main exist (via email matching) else create one.
            if vals["partner_profile"] == profile_position and not vals.get("contact_id"):
                existing_main = self.env["res.partner"].search([('is_company', '=', False),('partner_profile', '=', profile_main),('email', '=', vals["email"])])      
                if existing_main:
                    vals["contact_id"] = existing_main.id
                else:
                    main_vals = vals.copy()
                    main_vals["partner_profile"] = profile_main
                    main_vals["parent_id"] = False
                    main_res = super(res_partner, self).create(main_vals)
                    main_res.create_public_profile()
                    vals["contact_id"] = main_res.id
            res = super(res_partner, self).create(vals)
            # Creation of the public profile
            if (
                res.partner_profile.ref == "partner_profile_main" #TODO: replace by check on boolean is_main_profile ? Is this boolean computed at this step of the process?
                and not res.public_profile_id
            ):
                res.create_public_profile()
            if res.partner_profile.ref == "partner_profile_public": #TODO: replace by check on boolean is_public_profile ? Is this boolean computed at this step of the process?
                # Public profile can't be customer or supplier. Only main or position profiles can
                res.customer = False
                res.supplier = False
        else:
            res = super(res_partner, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        for partner in self:
            if partner.is_company:
                # Delete position profiles linked to the company main profile
                child_ids = self.env["res.partner"].search([("parent_id", "=", partner.id), ("is_position_profile", "=", True)])
                for child in child_ids:
                        child.unlink()
        return super(res_partner, self).unlink()

    @api.multi
    def write(self, vals):
        super(res_partner, self).write(vals)
        if "active" in vals and not "sync_active" in vals:
            self._sync_active_profiles()

    def _sync_active_profiles(self):
        """Synchronize the active fields values between all the profiles of a partner.
        Change in main profile is synchronized in public and position profiles.
        Change in public profile is NOT synchronized in main and public profiles.
        Change in position profile is NOT synchronized in main and public profiles."""
        for partner in self:
            if partner.is_main_profile:
                # Sync public profile active value with main one
                public_profile = partner.public_profile_id
                if public_profile and (public_profile.active != partner.active):
                   public_profile.write({"active": partner.active, "sync_active": True})

                # Sync position profiles active value with main one
                positions = self.env["res.partner"].search(
                    [
                        ("is_position_profile", "=", True),
                        ("active", "!=", partner.active),
                        '|',
                        ("contact_id", "=", partner.id),
                        ("parent_id", "=", partner.id)
                    ]
                )
                if len(positions) > 0:
                    for position in positions:
                        position.write({"active": partner.active, "sync_active": True})

    @api.model
    def search_position_partners(self, profile):
        if profile:
            position_partners = self.env["res.partner"].search(
                [("contact_id", "=", self.id), ("partner_profile", "=", profile)]
            )
        else:
            position_partners = self.env["res.partner"].search(
                [("contact_id", "=", self.id)]
            )
        return position_partners

    def _get_field_value(self, fname):
        field = self._fields[fname]
        if field.type == "many2one":
            return self[fname].id
        elif field.type == "one2many":
            return None
        elif field.type == "many2many":
            return [(6, 0, self[fname].ids)]
        else:
            return self[fname]

    def _get_public_profile_fields(self):
        # Return the fields to copy in the public profile when it is created.
        # The data copied depend on the partner's type: we consider the company data as public,
        # whereas the personal data shouldn't be public by default.
        if self.is_company:
            fields = [
                "name",
                "phone",
                "mobile",
                "email",
                "website",
                "street",
                "street2",
                "city",
                "country_id",
                "zip",
                "is_company",
            ]
        else:
            fields = ["name"]
        return fields

    @api.multi
    def create_public_profile(self):
        profile = self.env.ref("partner_profiles.partner_profile_public")
        for partner in self:
            _logger.debug("Create public profile [%s] %s" % (partner.id, partner.name))
            # Check if a public partner already exists
            partner._compute_public_profile_id()
            if not partner.public_profile_id:
                values = {
                    "type": "other",
                    "contact_id": partner.id,
                    "partner_profile": profile.id,
                    "company_id": partner.company_id.id,
                }
                public_fields = partner._get_public_profile_fields()
                for field_name in public_fields:
                    values[field_name] = partner._get_field_value(field_name)
                partner.create(values)
                partner._compute_public_profile_id()

    def _contact_fields(self):
        """ Returns the list of contact fields that are synced from the parent
        when a partner is attached to him. """
        return ['title']

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ Remove public profile partners from the name_search results"""
        if not args:
            args = [("is_public_profile", "=", False)]
        else:
            args.append(("is_public_profile", "=", False))
        return super(res_partner, self).name_search(name, args, operator, limit)

    ##################################################################################
    ## Planned actions
    ##################################################################################

    @api.model
    def _cron_generate_missing_public_profiles(self):
        partners = self.search(
            [("is_main_profile", "=", True), ("public_profile_id", "=", False)]
        )
        for partner in partners:
            partner.create_public_profile()

    def _get_concerned_partners_search_values(
        self, 
        id=False, 
        is_company=False, 
        active=True,
        with_parent=False,
    ):
        search_values = [
            ("is_company", "=", is_company),
            ("active", "=", active),
            ("partner_profile", "=", False)
        ]
        if id:
            search_values.append(("id", "=", id))
        if with_parent and not is_company:
            search_values.append(("parent_id", "!=", False))
        elif not is_company:
            search_values.append(("parent_id", "=", False))
        return search_values

    @api.model
    def _migration_create_pro_profiles(self, limit=None, id=False):
        partner_profile_main = self.env.ref("partner_profiles.partner_profile_main")

        # Company migration
        search_values = self._get_concerned_partners_search_values(
            id,
            is_company=True,
        )
        partners = self.env["res.partner"].search(search_values, limit=limit)
        _logger.debug("Company migration count: %s" % len(partners)) 
        if partners:
            partners.write(
                {
                    "partner_profile": partner_profile_main.id,
                }
            )
            partners.create_public_profile()
        _logger.debug("### End migration ###")

    @api.model
    def _migration_person_without_parent(self, limit=None, id=False):
        partner_profile_main = self.env.ref("partner_profiles.partner_profile_main")
        
        # Person migration without parent_id
        search_values = self._get_concerned_partners_search_values(id)
        partners = self.env["res.partner"].search(search_values, limit=limit)
        _logger.debug("Person without parent migration count: %s" % len(partners))
        if partners:
            partners.write(
                {
                    "partner_profile": partner_profile_main.id,
                }
            )
            _logger.debug("Create public profiles")
            partners.create_public_profile()
        _logger.debug("### End migration ###")

    def _get_main_partner_search_values(self, partner):
        return [
            ("active", "=", True),
            ("is_main_profile", "=", True),
            ("is_company", "=", False),
            "|",
            ("name", "=", partner.name),
            "&",
            ("email", "!=", False),
            ("email", "=", partner.email),
        ]
        
    @api.model
    def _migration_person_with_parent_and_existing_main(
        self, limit=None, id=False
    ):
        partner_profile_position = self.env.ref("partner_profiles.partner_profile_position")

        # Person migration with parent_id
        search_values = self._get_concerned_partners_search_values(
            id,
            with_parent=True,
        )
        partners = self.env["res.partner"].search(search_values, limit=limit)
        _logger.debug("Person migration with parent_id - migration count: %s" % len(partners))
        count = 0
        for partner in partners:
            _logger.debug("count: [%s] : %s" % (count, partner.name))
            existing_main_partner = self.env["res.partner"].search(
                self._get_main_partner_search_values(partner),
                limit=1,
            )
            if existing_main_partner:
                _logger.debug("UPDATE Position")
                partner.write(
                    {
                        "contact_id": existing_main_partner.id,
                        "partner_profile": partner_profile_position.id,
                    }
                )
            count += 1
        _logger.debug("### End migration ###")

    def _get_create_main_partner_values(self, partner):
        partner_profile_main = self.env.ref("partner_profiles.partner_profile_main")
        return {
            "partner_profile": partner_profile_main.id,
            "company_id": partner.company_id.id,
            "parent_id": False,
            "name": partner.name,
        }

    @api.model
    def _migration_person_with_parent_not_existing_main(
        self, limit=None, id=False
    ):

        partners = self.env["res.partner"]
        partner_profile_position = self.env.ref("partner_profiles.partner_profile_position")

        # Person migration with parent_id
        search_values = self._get_concerned_partners_search_values(
            id,
            with_parent=True,
        )
        partners = self.env["res.partner"].search(search_values, limit=limit)
        _logger.debug("Person migration with parent_id - migration count: %s" % len(partners))

        count = 0
        for partner in partners:
            _logger.debug("count: [%s] : %s" % (count, partner.name))
            existing_main_partner = self.env["res.partner"].search(
                self._get_main_partner_search_values(partner),
                limit=1,
            )
            if not existing_main_partner:
                default_values = self._get_create_main_partner_values(partner)
                try:
                    main_partner = partner.copy(default=default_values)
                except Exception as e:
                    _logger.debug("Email exist ! try with empty email")
                    default_values["email"] = ""
                    main_partner = partner.copy(default=default_values)

                _logger.debug(
                    "count: [%s] %s -> [%s] %s "
                    % (partner.id, partner.name, main_partner.id, main_partner.name)
                )
                partner.write(
                    {
                        "partner_profile": partner_profile_position.id,
                        "contact_id": main_partner.id,
                        "type": "other",
                    }
                )
            count += 1
        _logger.debug("Last clean")