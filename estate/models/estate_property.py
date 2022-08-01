from curses.ascii import US
import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError

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
        selection=[("new","New"),("Offer_Received","Offer Received"),("Offer_Accepted","Offer Accepted"),("Offer_Refused","Offer Refused"),("sold","Sold"),('canceled','Canceled')],
        default="new")
    type=fields.Many2one("estate.type",string="Type")
    salesperson = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True, default=lambda self: self.env.user)
    
    buyer = fields.Many2one(
        'res.partner', string='Buyer', index=True, tracking=10,copy=False,
        help="Linked partner. You can find a partner by its Name, TIN, Email or Internal Reference.")
    tag=fields.Many2many("estate.tag",string="Tags")
    
    offer_ids=fields.One2many("estate.offer","property_id",string="Offers")

    total_area=fields.Float(compute="_compute_total_area", store=True, string="Total Area (sqm)")

    best_price=fields.Float(compute="_get_best_price",store=True,string="Best Offer Price")

    @api.depends("offer_ids")
    def _get_best_price(self):
        for record in self:
            if len(record.offer_ids.mapped("price"))>0:
                print(record.offer_ids.mapped("price"))
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price=0.0


    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area+ record.living_area


    @api.onchange("garden")
    def _onchange_partner_id(self):
        if self.garden==True:
            self.garden_area=10
            self.garden_orientation="north"
        else:
            self.garden_area=0
            self.garden_orientation=""

    def sold_action(self):
        for record in self:
            if record.Status=="canceled":
                 raise UserError("The canceled property cannot be sold. Try to add a new property for selling.")
            else:
                record.Status="sold"

    def cancel_action(self):
        for record in self:
            if record.Status=="sold":
                raise UserError("The sold property cannot be canceled")
            else:
                record.Status="canceled"

###########################################

class EstatePropertyType(models.Model):
    _name = "estate.type"
    _description = "Real Estate Property Type as there could be many types"
    name=fields.Char(required=True)

###########################################
class EstatePropertyTag(models.Model):
    _name="estate.tag"
    _description = "A property tag is, for example, a property which is ‘cozy’ or ‘renovated’."
    name=fields.Char(required=True)

###########################################
class EstatePropertyOffer(models.Model):
    _name="estate.offer"
    _description="An offer to a property"
    price=fields.Float(required=True,string="Offered Price")
    Status=fields.Selection(string="Status",
        selection=[("accepted","Accepted"),("refused","Refused")],
        help="The status of the offer")
    partner_id=fields.Many2one('res.partner', string='Offer maker',copy=False,Required=True)
    property_id=fields.Many2one('estate.property',string="Property")
    validity=fields.Integer(string="validity (Days)",default=7)
    create_date=fields.Date(copy=False,default=lambda self: fields.Datetime.now())
    date_deadline=fields.Date(compute="_compute_deadline", inverse="_inverse_deadline")
    #date_deadline=fields.Date(compute="_compute_deadline")

    @api.depends("validity","create_date")
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date+ datetime.timedelta(days=record.validity) 

    def _inverse_deadline(self):
        for record in self:
            diff=record.date_deadline- record.create_date
            record.validity = diff.days

    def action_accept(self):
        for record in self:
            if record.property_id.Status!="sold" and record.property_id.Status!="canceled":
                record.Status = "accepted"
                record.property_id.selling_price=record.price
                record.property_id.buyer=record.partner_id
                record.property_id.Status="Offer_Accepted"
            else:
                raise UserError("An offer for a sold or canceled property cannot be accepted.")
        return True

    def action_refuse(self):
        for record in self:
            if record.property_id.Status!="sold" and record.property_id.Status!="canceled":
                record.Status = "refused"
                record.property_id.selling_price=0
                record.property_id.buyer=""
                # record.property_id.Status="Offer_Refused"
            else:
                raise UserError("The property has been either sold or canceled, thus refusing an offer is no longer valid.") 
        return True
    
