from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseCanvassWizard(models.TransientModel):
    _name = 'purchase.canvass.wizard'
    _description = 'Canvass and PO Consolidation Wizard'

    line_ids = fields.Many2many(
        'purchase.request.line',
        'wizard_pr_line_rel',
        'wizard_id',
        'line_id',
        string="Approved Items to Process",
        domain="[('state', '=', 'approved'), ('po_line_id', '=', False)]"
    )
    supplier_id = fields.Many2one(
        'res.suppliers' if False else 'res.partner', # Using Odoo's standard partner model for vendors
        string="Winning Supplier",
        required=True,
        domain="[('supplier_rank', '>', 0)]"
    )

    def action_generate_purchase_order(self):
        """Consolidate selected approved PR lines into a single Purchase Order for the winning supplier."""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Please select at least one approved item to consolidate into a Purchase Order."))

        # 1. Create Purchase Order Header
        po_vals = {
            'partner_id': self.supplier_id.id,
            'origin': ", ".join(self.line_ids.mapped('request_id.name')),
            'order_line': [],
        }

        po_lines = []
        for pr_line in self.line_ids:
            # Prepare PO line values
            po_line_vals = (0, 0, {
                'product_id': pr_line.product_id.id,
                'name': pr_line.product_id.display_name,
                'product_qty': pr_line.product_qty,
                'product_uom': pr_line.product_uom_id.id,
                'price_unit': pr_line.estimated_cost, # Can be overridden with canvassed price
                'date_planned': fields.Datetime.now(),
            })
            po_lines.append(po_line_vals)

        po_vals['order_line'] = po_lines
        purchase_order = self.env['purchase.order'].create(po_vals)

        # 2. Link PO lines back to PR lines and update state
        for index, pr_line in enumerate(self.line_ids):
            created_po_line = purchase_order.order_line[index]
            pr_line.write({
                'po_line_id': created_po_line.id,
                'state': 'in_po'
            })

        # 3. Return action to open the newly created Purchase Order
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generated Purchase Order',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_mode': 'form',
            'target': 'current',
        }