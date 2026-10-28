from odoo import models, fields, api, _

class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_id = fields.Many2one('purchase.request', string="PR Reference", ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string="Item", required=True)
    product_qty = fields.Float(string="Quantity", default=1.0, required=True)
    product_uom_id = fields.Many2one(related='product_id.uom_id', string="Unit of Measure")
    category_id = fields.Many2one(related='product_id.categ_id', store=True, string="Category")
    estimated_cost = fields.Float(string="Estimated Cost")
    
    # Line Item State Lifecycle
    state = fields.Selection([
        ('draft', 'Draft'),
        ('office_head', 'Pending Office Head'),
        ('inventory_cert', 'Pending Inventory Specialist'),
        ('it_inspection', 'Pending IT Inspection'),
        ('supervising_vp', 'Pending Supervising VP'),
        ('vpf_approval', 'Pending VPF Approval'),
        ('approved', 'Approved for Canvass'),
        ('in_po', 'In Purchase Order'),
        ('delivered', 'Delivered'),
        ('fulfilled_stock', 'Fulfilled from Stock'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True, index=True)

    # Verification & Approval Tracking
    verified_by_inventory_id = fields.Many2one('res.users', string="Inventory Specialist")
    inventory_remarks = fields.Text(string="Inventory Remarks")
    
    it_service_request_id = fields.Many2one('maintenance.request', string="IT Service Request Ticket")
    it_remarks = fields.Text(string="Tech Remarks")
    
    supervising_vp_remarks = fields.Text(string="Supervising VP Remarks")
    vpf_user_id = fields.Many2one('res.users', string="VPF Approver")

    # PO Consolidation Link
    po_line_id = fields.Many2one('purchase.order.line', string="Linked PO Line", readonly=True)

    # --- Workflow Actions ---

    def action_office_head_approve(self):
        """Office Head approves -> Route to Specialist Inventory Verification."""
        for line in self:
            line.write({'state': 'inventory_cert'})

    def action_inventory_certify_needed(self):
        """Specialist verifies item needs purchase -> Check if IT tech check needed."""
        for line in self:
            line.verified_by_inventory_id = self.env.user
            if line.category_id.requires_it_service_request:
                # Trigger IT Maintenance Request Ticket
                ticket = self.env['maintenance.request'].create({
                    'name': f"PR Inspection: {line.product_id.display_name} ({line.request_id.name})",
                    'description': f"Required for PR line item verification.",
                })
                line.write({'state': 'it_inspection', 'it_service_request_id': ticket.id})
            else:
                line.write({'state': 'supervising_vp'})

    def action_inventory_fulfill_from_stock(self):
        """Item is available in warehouse -> Cancel purchase route."""
        for line in self:
            line.write({
                'verified_by_inventory_id': self.env.user,
                'state': 'fulfilled_stock'
            })

    def action_it_pass_inspection(self):
        """Tech confirms replacement/purchase needed -> Forward to Supervising VP."""
        for line in self:
            line.write({'state': 'supervising_vp'})

    def action_supervising_vp_approve(self):
        """Supervising VP endorses -> Route to VPF for final budget sign-off."""
        for line in self:
            line.write({'state': 'vpf_approval'})

    def action_vpf_final_approve(self):
        """VPF line-item approval -> Eligible for Canvassing Matrix."""
        for line in self:
            line.write({'vpf_user_id': self.env.user, 'state': 'approved'})

    def action_reject(self):
        """Reject line item."""
        for line in self:
            line.write({'state': 'rejected'})