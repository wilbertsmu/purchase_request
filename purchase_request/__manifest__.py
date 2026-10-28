{
    'name': 'Custom Purchase Request & Multi-Level Approval',
    'version': '18.0.1.0.0', # Adjust version based on your Odoo version (e.g., 16.0, 17.0, 18.0)
    'category': 'Inventory/Purchase',
    'summary': 'Automated PR workflow with category verifications, IT checks, and PO consolidation.',
    'author': 'Your Organization',
    'depends': [
        'base',
        'purchase',
        'stock',
        'hr',
        'maintenance', # Used for IT Service Requests
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/hr_department_views.xml',
        'views/product_category_views.xml',
        'views/purchase_request_views.xml',
        'views/canvass_wizard_views.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}