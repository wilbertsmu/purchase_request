from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'

    verifier_user_ids = fields.Many2many(
        'res.users',
        'rel_category_verifier_users',
        'category_id',
        'user_id',
        string="Category Inventory Specialists",
        help="Specialists who certify whether requested items are available in stock."
    )
    requires_it_service_request = fields.Boolean(
        string="Requires IT Service Request",
        default=False,
        help="If checked, items in this category require a Computer Tech inspection before proceeding."
    )