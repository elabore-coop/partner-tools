# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Adds last name and first name; name becomes a stored function field."""
    _inherit = 'res.partner'

    def _compute_is_favorite(self):
        for partner in self:
            partner.is_favorite = self.env.user in partner.favorite_user_ids

    def _inverse_is_favorite(self):
        favorite_partners = not_fav_partners = self.env['res.partner']
        for partner in self:
            if self.env.user in partner.favorite_user_ids:
                favorite_partners |= partner
            else:
                not_fav_partners |= partner

        # partner User has no write access for partner.
        not_fav_partners.write({'favorite_user_ids': [(4, self.env.uid)]})
        favorite_partners.write({'favorite_user_ids': [(3, self.env.uid)]})

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    favorite_user_ids = fields.Many2many(
        'res.users', 'partner_favorite_user_rel', 'partner_id', 'user_id',
        default=_get_default_favorite_user_ids,
        string='Members')
    is_favorite = fields.Boolean(
        compute='_compute_is_favorite',
        inverse='_inverse_is_favorite',
        string='Show Favorite Partner',
        help="Display this partner with favorite filter")
