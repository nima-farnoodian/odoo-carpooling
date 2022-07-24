from odoo import models, fields, api


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property "
    name=fields.Char(required=True)
    description=fields.Text()
    postcode=fields.Char()
    date_availability=fields.Date(copy=False,default=lambda self: fields.Datetime.now())
    expected_price=fields.Float(required=True)
    selling_price=fields.Float(readonly=True,copy=False)
    bedrooms=fields.Integer(default=2)
    living_area=fields.Integer()
    facades=fields.Integer()
    garage=fields.Boolean()
    garden=fields.Boolean()
    garden_area=fields.Integer()
    garden_orientation=fields.Selection(
        string="Orientation",
        selection=[("north","North"),("south","South"),("east","East"),("west","West")],
        help="The orientation of the place.")
    
    active=fields.Boolean(default=True)
    Status=fields.Selection(
        string="Status",
        selection=[("new","New"),("Offer_Received","Offer Received"),("Offer_Accepted","Offer Accepted,"),("sold","Sold"),('canceled','Canceled')]
        )
    type=fields.Many2one("estate.type",string="Type")
    salesperson = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True, default=lambda self: self.env.user)
    
    buyer = fields.Many2one(
        'res.partner', string='Buyer', index=True, tracking=10,copy=False,
        help="Linked partner. You can find a partner by its Name, TIN, Email or Internal Reference.")
    tag=fields.Many2many("estate.tag",string="Tags")
    offers=fields.One2many("estate.offer","property_id",string="offers")


class EstatePropertyType(models.Model):
    _name = "estate.type"
    _description = "Real Estate Property Type as there could be many types"
    name=fields.Char(required=True)

class EstatePropertyTag(models.Model):
    _name="estate.tag"
    _description = "A property tag is, for example, a property which is ‘cozy’ or ‘renovated’."
    name=fields.Char(required=True)


class EstatePropertyOffer(models.Model):
    _name="estate.offer"
    _description="An offer to a property"
    Status=fields.Selection(string="Status",
        selection=[("accepted","Accepted"),("refused","Refused")],
        help="The status of the offer")
    partner_id=fields.Many2one('res.partner', string='Offer maker',copy=False,Required=True)
    property_id=fields.Many2one('estate.property',string="Property")
