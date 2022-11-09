# Copyright 2020 Lokavaluto ()
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, tools, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalPartnerProfile(CustomerPortal):

    def _profile_get_page_view_values(self, profile, access_token, **kwargs):
        values = {
            "page_name": "profile",
            "profile": profile,
        }
        return self._get_page_view_values(
            profile, access_token, values, "my_profiles_history", False, **kwargs
        )

    def _details_profile_form_validate(self, data, profile_id):
        error = dict()
        error_message = []
        # nickname uniqueness
        if data.get("nickname") and request.env["res.partner"].sudo().search(
            [
                ("name", "=", data.get("nickname")),
                ("partner_profile.ref", "=", "partner_profile_public"),
                ("id", "!=", profile_id),
            ]
        ):
            error["nickname"] = "error"
            error_message.append(
                _("This nickname is already used, please find an other idea.")
            )

        # email validation
        if data.get("email") and not tools.single_email_re.match(data.get("email")):
            error["email"] = "error"
            error_message.append(
                _("Invalid Email! Please enter a valid email address.")
            )
        return error, error_message

    def _get_profile_fields(self):
        fields = [
            "nickname",
            "function",
            "phone",
            "mobile",
            "email",
            "website_url",
            "street",
            "street2",
            "city",
            "country_id",
            "zipcode",
        ]
        return fields

    def _get_page_saving_values(self, profile, kw):
        profile_fields = self._get_profile_fields()
        values = {key: kw[key] for key in profile_fields if key in kw}
        values.update(
            {
                "name": values.pop("nickname", profile.name),
                "zip": values.pop("zipcode", ""),
                "website": values.pop("website_url", ""),
            }
        )
        return values

    def _get_page_opening_values(self):
        # Just retrieve the values to display for Selection fields
        countries = request.env["res.country"].sudo().search([])
        values = {
            "countries": countries,
        }
        return values

    @http.route(
        ["/my/profile/<int:profile_id>", "/my/profile/save"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_profile(
        self, profile_id=None, access_token=None, redirect=None, **kw
    ):
        # The following condition is to transform profile_id to an int, as it is sent as a string from the templace "portal_my_profile"
        # TODO: find a better way to retrieve the profile_id at form submit step
        if not isinstance(profile_id, int):
            profile_id = int(profile_id)

        # Check that the user has the right to see this profile
        try:
            profile_sudo = self._document_check_access(
                "res.partner", profile_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my/profiles")

        values = self._profile_get_page_view_values(profile_sudo, access_token, **kw)
        values.update(
            {
                "error": {},
                "error_message": [],
            }
        )
        if kw and request.httprequest.method == "POST":
            # the user has clicked in the Save button to save new data
            error, error_message = self._details_profile_form_validate(kw, profile_id)
            values.update({"error": error, "error_message": error_message})
            values.update(kw)
            if not error:
                profile = request.env["res.partner"].browse(profile_id)
                values = self._get_page_saving_values(profile, kw)
                profile.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect("/my/profiles")

        # This is just the form page opening. We send all the data needed for the form fields
        values.update(self._get_page_opening_values())
        values.update(
            {
                "profile_id": profile_id, # Sent in order to retrieve it at submit time
                "redirect": redirect
            }
        )
        return request.render("partner_profiles_portal.portal_my_profile", values)
