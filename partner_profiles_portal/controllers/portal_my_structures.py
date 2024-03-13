# Copyright 2020 Lokavaluto ()
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields as odoo_fields
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortalMyStructures(CustomerPortal):

    def _get_domain_my_structures(self, user):
        if user.partner_id.other_contact_ids:
            main_structure_ids = user.partner_id.other_contact_ids.mapped("parent_id")
            return [("id", "in", main_structure_ids.ids), 
                    ("is_company", "=", True)
            ]
        else:
            return None

    def _get_archive_groups(self, model, domain=None, fields=None, groupby="create_date", order="create_date desc"):
        if not model:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'create_date']
        groups = []
        for group in request.env[model]._read_group_raw(domain, fields=fields, groupby=groupby, orderby=order):
            dates, label = group[groupby]
            date_begin, date_end = dates.split('/')
            groups.append({
                'date_begin': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_begin)),
                'date_end': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_end)),
                'name': label,
                'item_count': group[groupby + '_count']
            })
        return groups

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortalMyStructures, self)._prepare_portal_layout_values()
        domain = self._get_domain_my_structures(request.env.user)
        values["structure_count"] = request.env["res.partner"].search_count(domain) if domain else 0
        return values

    @http.route(
        ["/my/structures", "/my/structures/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_structures(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        structure = request.env["res.partner"]
        domain = self._get_domain_my_structures(request.env.user)

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
        structure_count = structure.search_count(domain) if domain else 0
        # pager
        pager = portal_pager(
            url="/my/structures",
            url_args={"sortby": sortby},
            total=structure_count,
            page=page,
            step=self._items_per_page,
        )

        # content according to pager and archive selected
        structures = structure.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        ) if domain else None
        request.session["my_structures_history"] = structures.ids[:100] if structures else None

        values.update(
            {
                "structures": structures,
                "page_name": "structure",
                "archive_groups": archive_groups,
                "default_url": "/my/structures",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("partner_profiles_portal.portal_my_structures", values)