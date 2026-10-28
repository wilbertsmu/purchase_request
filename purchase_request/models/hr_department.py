from odoo import models, fields

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    supervising_vp_id = fields.Many2one(
        'res.users',
        string="Supervising Vice President",
        help="VP responsible for endorsing Purchase Requests from this department."
    )