from odoo import models

class InheritedModel(models.Model):
    _inherit = "estate.property"

    def sold_action(self):
        print("This is a test from overridden sold_action")
        return super().sold_action()
       