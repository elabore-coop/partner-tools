# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
from random import randint
from odoo.exceptions import ValidationError


class ResPartnerSkill(models.Model):
    _name = 'res.partner.skill'

    _description = 'Partner skill'
    _order = 'name'
    _parent_store = True

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Skill Name', required=True, translate=True)
    color = fields.Integer(string='Color', default=_get_default_color)
    parent_id = fields.Many2one('res.partner.skill', string='Parent Skill', index=True, ondelete='cascade')
    child_ids = fields.One2many('res.partner.skill', 'parent_id', string='Child Skills')
    active = fields.Boolean(default=True, help="The active field allows you to hide the skill without removing it.")
    parent_path = fields.Char(index=True, unaccent=False)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive skills.'))

    def name_get(self):
        """ Return the skills' display name, including their direct
            parent by default.
        """
        res = []
        for skill in self:
            names = []
            current = skill
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((skill.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)