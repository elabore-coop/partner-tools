# Copyright 2020 Lokavaluto ()
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from odoo import http, tools, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalStructureProfile(CustomerPortal):

    def _structure_get_page_view_values(self, structure, access_token, **kwargs):
        values = {
            "page_name": "structure",
            "structure": structure,
        }
        return self._get_page_view_values(
            structure, access_token, values, "my_structures_history", False, **kwargs
        )

    def _details_structure_form_validate(self, data, structure_id):
        error = dict()
        error_message = []
        # public name uniqueness
        if data.get("public_name") and request.env["res.partner"].sudo().search(
            [
                ("name", "=", data.get("public_name")),
                ("is_public_profile", "=", True),
                ("contact_id", "!=", structure_id),
            ]
        ):
            error["public_name"] = "error"
            error_message.append(
                _("This public name is already used, please find an other idea.")
            )

        # email validation
        if data.get("email") and not tools.single_email_re.match(data.get("email")):
            error["email"] = "error"
            error_message.append(
                _("Invalid Email! Please enter a valid email address.")
            )
        return error, error_message

    def _get_main_profile_fields(self):
        '''Provides all the fields that must fill the structure's main profile.
        All of them MUST start with "main_".'''
        fields = [
            "main_name",
            "main_street",
            "main_street2",
            "main_zip",
            "main_city",
            "main_country_id",
            "main_phone",
            "main_mobile",
            "main_email",
            "main_website",
        ]
        return fields

    def _get_main_boolean_structure_fields(self):
        '''Provides the fields for which we must check the presence
        in form's kw to know the value to save in the partner field.
        All of them MUST start with "main_".'''
        fields = []
        return fields

    def _get_public_profile_fields(self):
        '''Provides all the fields that must fill the structure's public profile.
        All of them MUST start with "public_".'''
        fields = [
            "public_name",
            "public_street2",
            "public_street",
            "public_zip",
            "public_city",
            "public_phone",
            "public_mobile",
            "public_email",
            "public_website",
        ]
        return fields

    def _get_public_boolean_structure_fields(self):
        '''Provides the fields for which we must check the presence
        in form's kw to know the value to save in the partner field.
        All of them MUST start with "public_".'''
        fields = []
        return fields

    def _get_position_profile_fields(self):
        '''Provides all the fields that must fill the structure's position profile of the user.
        All of them MUST start with "position_".'''
        fields = [
            "position_function",
            "position_phone",
            "position_email",
        ]
        return fields

    def _get_position_boolean_structure_fields(self):
        '''Provides the fields for which we must check the presence
        in form's kw to know the value to save in the partner field.
        All of them MUST start with "position_".'''
        fields = []
        return fields

    def _transform_in_res_partner_fields(self, kw, profile_fields, prefix=""):
        '''Transforms kw's values in res_partner fields and values'''
        return {key[len(prefix):]: kw[key] for key in profile_fields if key in kw}

    def _add_boolean_values(self, values, kw, boolean_fields, prefix=""):
        for key in boolean_fields:
            values.update(
                {
                    key[len(prefix):]: kw.get(key, "off") == "on",
                }
            )
        return values

    def _get_page_saving_main_structure_values(self, kw):
        profile_fields = self._get_main_profile_fields()
        values = self._transform_in_res_partner_fields(kw, profile_fields, "main_")
        boolean_fields = self._get_main_boolean_structure_fields()
        values = self._add_boolean_values(values, kw, boolean_fields, "main_")
        if 'logo' in kw:
            image = kw.get('logo')
            if image:
                image = image.read()
                image = base64.b64encode(image)
                values.update({
                    'image': image
                })
        return values

    def _get_page_saving_public_structure_values(self, kw):
        profile_fields = self._get_public_profile_fields()
        values = self._transform_in_res_partner_fields(kw, profile_fields, "public_")
        boolean_fields = self._get_public_boolean_structure_fields()
        values = self._add_boolean_values(values, kw, boolean_fields, "public_")
        return values

    def _get_page_saving_position_structure_values(self, kw):
        profile_fields = self._get_position_profile_fields()
        values = self._transform_in_res_partner_fields(kw, profile_fields, "position_")
        boolean_fields = self._get_position_boolean_structure_fields()
        values = self._add_boolean_values(values, kw, boolean_fields, "position_")
        return values

    def _get_page_opening_values(self):
        # Just retrieve the values to display for Selection fields
        countries = request.env["res.country"].sudo().search([])
        values = {
            "countries": countries,
        }
        return values

    @http.route(
        ["/my/structure/<int:structure_id>", "/my/structure/save"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_structure(
        self,structure_id=None, access_token=None, redirect=None, **kw
    ):
        # The following condition is to transform profile_id to an int, as it is sent as a string from the templace "portal_my_profile"
        # TODO: find a better way to retrieve the profile_id at form submit step
        if not isinstance(structure_id, int):
            structure_id = int(structure_id)

        # Check that the user has the right to see this profile
        try:
            structure_sudo = self._document_check_access(
                "res.partner", structure_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my/structures")

        Partner = request.env["res.partner"]
        partner_id = request.env.user.partner_id
        main_profile = Partner.browse(structure_id)
        public_profile = Partner.browse(main_profile.public_profile_id.id)
        position_profile = Partner.search(
            [
                ("parent_id", "=", structure_id), 
                ("contact_id", "=", partner_id.id),
                ("is_position_profile", "=", True),
                ("active", "=", True)
            ],
            limit=1
        )[0]

        values = self._structure_get_page_view_values(structure_sudo, access_token, **kw)
        values.update(
            {
                "error": {},
                "error_message": [],
            }
        )
        if kw and request.httprequest.method == "POST":
            # the user has clicked in the Save button to save new data
            error, error_message = self._details_structure_form_validate(kw, structure_id)
            values.update({"error": error, "error_message": error_message})
            values.update(kw)
            if not error:
                # Update main profile
                new_values = self._get_page_saving_main_structure_values(kw)
                main_profile.sudo().write(new_values)
                # Update public profile
                new_values = self._get_page_saving_public_structure_values(kw)
                public_profile.sudo().write(new_values)
                # Update position profile
                new_values = self._get_page_saving_position_structure_values(kw)
                position_profile.sudo().write(new_values)
                # End of updates
                if redirect:
                    return request.redirect(redirect)
                return request.redirect("/my/structures")

        # This is just the form page opening. We send all the data needed for the form fields
        can_edit_structure = partner_id in main_profile.can_edit_structure_profiles_ids
        values.update(self._get_page_opening_values())
        values.update(
            {
                "structure_id": structure_id, # Sent in order to retrieve it at submit time
                "public_profile": public_profile,
                "position_profile": position_profile,
                "can_edit_structure": can_edit_structure,
                "redirect": "/my/structure/" + str(structure_id) + "?success=True"
            }
        )
        return request.render("partner_profiles_portal.portal_structure", values)
