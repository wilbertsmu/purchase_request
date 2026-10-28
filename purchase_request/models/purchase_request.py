from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request Header'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="PR Number", 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('New')
    )
    requested_by_id = fields.Many2one(
        'res.users', 
        string="Requested By", 
        default=lambda self: self.env.user, 
        required=True, 
        tracking=True
    )
    department_id = fields.Many2one(
        'hr.department', 
        string="Office / Department", 
        required=True, 
        default=lambda self: self.env.user.department_id
    )
    supervising_vp_id = fields.Many2one(
        related='department_id.supervising_vp_id', 
        store=True, 
        string="Supervising VP"
    )
    date_created = fields.Date(string="Date Requested", default=fields.Date.context_today, required=True)
    description = fields.Text(string="Purpose / Justification")
    
    line_ids = fields.One2many(
        'purchase.request.line', 
        'request_id', 
        string="Requested Items"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.seq') or _('New')
        return super(PurchaseRequest, self).create(vals_list)

    def action_submit_to_office_head(self):
        """Forward all draft lines to Office Head review state."""
        for line in self.line_ids.filtered(lambda l: l.state == 'draft'):
            line.state = 'office_head'