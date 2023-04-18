# -*- coding: utf-8 -*-
import base64
from odoo import tools
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortalMyProfile(CustomerPortal):

    def _get_mandatory_main_fields(self):
        return  ["main_name", "main_email"]

    def _get_optional_main_fields(self):
        return  ["main_street", "main_street2", "main_city", "main_country_id", "main_phone", "main_mobile", "main_zip", "main_state_id", "main_website"]

    def _get_mandatory_public_fields(self):
        return ["public_name"]

    def _get_optional_public_fields(self):
        return ["public_email", "public_street", "public_street2", "public_city", "public_phone", "public_mobile", "public_zip", "public_website"]

    def _get_special_fields(self):
        return ["main_logo"]

    def _transform_in_partner_fields(self, kw, profile_fields, prefix=""):
        '''Transforms kw's values in res_partner fields and values'''
        return {key[len(prefix):]: kw[key] for key in profile_fields if key in kw}

    def _retrieve_main_values(self, data):
        main_fields = self._get_mandatory_main_fields() + self._get_optional_main_fields()
        values = self._transform_in_partner_fields(data, main_fields, "main_")
        if 'main_logo' in data:
            image = data.get('main_logo')
            if image:
                image = image.read()
                image = base64.b64encode(image)
                values.update({
                    'image': image
                })
        return values

    def _retrieve_public_values(self, data):
        public_fields = self._get_mandatory_public_fields() + self._get_optional_public_fields()
        values = self._transform_in_partner_fields(data, public_fields, "public_")
        return values

    def _get_page_opening_values(self):
        # Just retrieve the values to display for Selection fields
        countries = request.env["res.country"].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        values = {
            "countries": countries,
            'states': states,
        }
        return values

    @route(["/my/account"], type="http", auth="user", website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        partner = user.partner_id
        public_partner = partner.public_profile_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                # Save main profile values
                values = self._retrieve_main_values(post)
                partner.sudo().write(values)
                # Save public profile values
                public_values = self._retrieve_public_values(post)
                if len(public_values) > 0:
                    public_partner.sudo().write(public_values)
                # Email change generates a change of user's login
                if post.get("main_email", user.login) != user.login:
                    user.login = post["main_email"]
                    return request.redirect("/web/session/logout")
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        values.update(self._get_page_opening_values())
        values.update({
            'partner': partner,
            'public_partner': public_partner,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': "/my/account?success=True",
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
                    
        return response



    def details_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self._get_mandatory_main_fields() + self._get_mandatory_public_fields():
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('main_email') and not tools.single_email_re.match(data.get('main_email')):
            error["main_email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))
        if data.get('public_email') and not tools.single_email_re.match(data.get('public_email')):
            error["public_email"] = 'error'
            error_message.append(_('Invalid Public Email! Please enter a valid public email address.'))

        # public name uniqueness
        if data.get("public_name") and request.env["res.partner"].sudo().search(
            [
                ("name", "=", data.get("public_name")),
                ("is_public_profile", "=", True),
                ("contact_id", "!=", request.env.user.partner_id.id),
            ]
        ):
            error["public_name"] = "error"
            error_message.append(
                _("This public name is already used, please find an other idea.")
            )

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append('Some required fields are empty.')

        unknown = [k for k in data if k not in self._get_mandatory_main_fields() + self._get_optional_main_fields() + self._get_mandatory_public_fields() + self._get_optional_public_fields() + self._get_special_fields()]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message