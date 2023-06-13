# Copyright 2020 Lokavaluto ()
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortalMyPositions(CustomerPortal):

    def _get_domain_my_positions(self, user):
        if user.partner_id.structure_position_ids:
            return [("id", "in", user.partner_id.structure_position_ids.ids), 
                    ("is_company", "=", False),
                    ("is_position_profile", "=", True),
            ]
        else:
            return None

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortalMyPositions, self)._prepare_portal_layout_values()
        domain = self._get_domain_my_structures(request.env.user)
        values["structure_count"] = request.env["res.partner"].search_count(domain) if domain else 0
        return values

    @http.route(
        ["/my/positions", "/my/positions/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_positions(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        position = request.env["res.partner"]
        domain = self._get_domain_my_positions(request.env.user)

        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name"},
            "parent_id": {"label": _("Company"), "order": "parent_id"},
        }
        if not sortby:
            sortby = "name"
        order = searchbar_sortings[sortby]["order"]

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups("res.partner", domain)

        # structures count
        position_count = position.search_count(domain) if domain else 0
        # pager
        pager = portal_pager(
            url="/my/positions",
            url_args={"sortby": sortby},
            total=position_count,
            page=page,
            step=self._items_per_page,
        )

        # content according to pager and archive selected
        positions = position.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        ) if domain else None
        request.session["my_positions_history"] = positions.ids[:100] if positions else None

        values.update(
            {
                "positions": positions,
                "page_name": "position",
                "archive_groups": archive_groups,
                "default_url": "/my/positions",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("partner_profiles_portal.portal_my_positions", values)