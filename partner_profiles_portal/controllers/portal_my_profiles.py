# Copyright 2020 Lokavaluto ()
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortalMyProfiles(CustomerPortal):

    def _get_domain_my_profiles(self, user):
        if user.partner_id.other_contact_ids:
            main_profile_ids = user.partner_id.other_contact_ids.filtered(
                "edit_structure_main_profile"
            ).mapped("parent_id")
            public_profile_ids = user.partner_id.other_contact_ids.filtered(
                "edit_structure_public_profile"
            ).mapped("parent_id.public_profile_id")
            return [
                "|",
                "|",
                ("contact_id", "=", user.partner_id.id),
                ("id", "in", main_profile_ids.ids),
                ("id", "in", public_profile_ids.ids),
            ]
        else:
            return [("contact_id", "=", user.partner_id.id)]

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortalMyProfiles, self)._prepare_portal_layout_values()
        values["profile_count"] = request.env["res.partner"].search_count(
            self._get_domain_my_profiles(request.env.user)
        )
        return values

    @http.route(
        ["/my/profiles", "/my/profiles/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_profiles(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        profile = request.env["res.partner"]
        domain = self._get_domain_my_profiles(request.env.user)

        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name"},
            "partner_profile": {"label": _("Profile Type"), "order": "partner_profile"},
            "parent_id": {"label": _("Company"), "order": "parent_id"},
        }
        if not sortby:
            sortby = "name"
        order = searchbar_sortings[sortby]["order"]

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups("res.partner", domain)

        # profiles count
        profile_count = profile.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/profiles",
            url_args={"sortby": sortby},
            total=profile_count,
            page=page,
            step=self._items_per_page,
        )

        # content according to pager and archive selected
        profiles = profile.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        )
        request.session["my_profiles_history"] = profiles.ids[:100]

        values.update(
            {
                "profiles": profiles,
                "page_name": "profile",
                "archive_groups": archive_groups,
                "default_url": "/my/profiles",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("partner_profiles_portal.portal_my_profiles", values)