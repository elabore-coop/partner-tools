# Copyright 2020 Lokavaluto ()
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from odoo import http, tools, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalPositionProfile(CustomerPortal):

    def _position_get_page_view_values(self, position, access_token, **kwargs):
        values = {
            "page_name": "position",
            "position": position,
        }
        return self._get_page_view_values(
            position, access_token, values, "my_positions_history", False, **kwargs
        )

    def _details_position_form_validate(self, data, position_id):
        error = dict()
        error_message = []
        # email validation
        if data.get("email") and not tools.single_email_re.match(data.get("email")):
            error["email"] = "error"
            error_message.append(
                _("Invalid Email! Please enter a valid email address.")
            )
        return error, error_message

    def _get_position_profile_fields(self):
        '''Provides all the fields that must fill the structure's position profile of the user.
        All of them MUST start with "position_".'''
        fields = [
            "function",
            "phone",
            "email",
            "edit_structure_profiles",
        ]
        return fields

    def _get_position_boolean_fields(self):
        '''Provides the fields for which we must check the presence
        in form's kw to know the value to save in the partner field.'''
        fields = ["edit_structure_profiles"]
        return fields

    def _transform_fields(self, kw, profile_fields):
        '''Transforms kw's values in res_partner fields and values'''
        return {key: kw[key] for key in profile_fields if key in kw}

    def _get_page_saving_position_values(self, kw):
        profile_fields = self._get_position_profile_fields()
        values = self._transform_fields(kw, profile_fields)
        # Boolean fields are not returned in "kw" if their value in the form is False.
        # Then we have to check their presence to determine which value  to save in the partner.
        boolean_fields = self._get_position_boolean_fields()
        for key in boolean_fields:
            values.update(
                {
                    key: kw.get(key, "off") == "on"
                }
            )
        return values

    @http.route(
        ["/my/position/<int:position_id>", "/my/position/save"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_position(
        self,position_id=None, access_token=None, redirect=None, **kw
    ):
        # The following condition is to transform profile_id to an int, as it is sent as a string from the templace "portal_my_profile"
        # TODO: find a better way to retrieve the profile_id at form submit step
        if not isinstance(position_id, int):
            position_id = int(position_id)

        # Check that the user has the right to see this profile
        try:
            position_sudo = self._document_check_access(
                "res.partner", position_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my/positions")

        position_profile = request.env["res.partner"].browse(position_id)

        values = self._position_get_page_view_values(position_sudo, access_token, **kw)
        values.update(
            {
                "error": {},
                "error_message": [],
            }
        )
        if kw and request.httprequest.method == "POST":
            # the user has clicked in the Save button to save new data
            error, error_message = self._details_position_form_validate(kw, position_id)
            values.update({"error": error, "error_message": error_message})
            values.update(kw)
            if not error:
                # Update position profile
                new_values = self._get_page_saving_position_values(kw)
                position_profile.sudo().write(new_values)
                # End of updates
                if redirect:
                    return request.redirect(redirect)
                return request.redirect("/my/positions")

        # This is just the form page opening. We send all the data needed for the form fields
        values.update(
            {
                "position_id": position_id, # Sent in order to retrieve it at submit time
                "position": position_profile,
                "redirect": "/my/position/" + str(position_id) + "?success=True"
            }
        )
        return request.render("partner_profiles_portal.portal_position", values)
