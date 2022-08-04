import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError
from  odoo.tools import float_utils


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property "
    _order = "id desc"
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
    state=fields.Selection(
        string="Status",
        selection=[("new","New"),("Offer_Received","Offer Received"),("Offer_Accepted","Offer Accepted"),("sold","Sold"),('canceled','Canceled')],
        default="new")
    type=fields.Many2one("estate.type",string="Type",ondelete='set null')
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
            if record.state=="canceled":
                 raise UserError("The canceled property cannot be sold. Try to add a new property for selling.")
            else:
                record.state="sold"

    def cancel_action(self):
        for record in self:
            if record.state=="sold":
                raise UserError("The sold property cannot be canceled")
            else:
                record.state="canceled"

    
    _sql_constraints = [
        ('expected_price_check', 'CHECK(expected_price >= 0)',
         'The expected price is strictly  positive'),
        ('selling_price_check', 'CHECK(selling_price >= 0)',
         'The selling price is strictly positive')
    ]

   # python constraibt for selling price
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if float_utils.float_is_zero(record.selling_price,2)!=True:
                if float_utils.float_compare(record.selling_price,.9*record.expected_price,2)==-1:
                    record.selling_price=0
                    record.buyer=""
                    raise ValidationError("The selling price cannot be lower than 90% of the expected price.")
    
    #CURD Action (On-Delete)
    # @api.ondelete
    # def unlink(self, vals):
    #     print("I am here in unlink")
    #     if vals['state'] not in ("new","canceled"):
    #         msg="It is impossible to remove the property" + vals['name'] +" as it is not now in a New or Canceled status."   
    #         print("Message:",msg)
    #         raise UserError(msg)
    #     # Then call super to execute the parent method
    #     return super().unlink(vals)
    
    @api.ondelete(at_uninstall=False)
    def _unlink_if_state_new(self):
        for record in self:
            if record.state not in ("new","canceled"):
                msg="It is impossible to remove the property (" + record.name +') as it is not now in a "New" or "Canceled" status.'   
                print("Message:",msg)
                raise UserError(msg)


    # @api.model
    # def create(self, vals):
    #     # Do some business logic, modify vals...
        
    #     print("I am here 1")

    #     print("All values for estate.property",vals)
        
    #     # Then call super to execute the parent method
    #     return super().create(vals)
 

###########################################

class EstatePropertyType(models.Model):
    _name = "estate.type"
    _description = "Real Estate Property Type as there could be many types"
    _order = "sequence,rank_of_used"
    sequence = fields.Integer('Sequence',default=1, help="Used to order types. Higher is better.")
    name=fields.Char(required=True)
    property_list=fields.One2many("estate.property","type","List of properties")
    rank_of_used=fields.Integer(compute="_compute_seq",Store=True)
    offer_ids=fields.One2many("estate.offer","property_type_id",string="Offers")
    offer_count=fields.Integer(compute="_compute_offer",Store=True)

    @api.depends("offer_ids")
    def _compute_offer(self):
        for record in self:
            print("len of types:",len(record.offer_ids.mapped("price")))
            record.offer_count =len(record.offer_ids.mapped("price"))

    @api.depends("property_list")
    def _compute_seq(self):
        for record in self:
            print("len of types:",len(record.property_list.mapped("name")))
            record.rank_of_used =len(record.property_list.mapped("name"))

###########################################
class EstatePropertyTag(models.Model):
    _name="estate.tag"
    _description = "A property tag is, for example, a property which is ‘cozy’ or ‘renovated’."
    _order = "name"
    name=fields.Char(required=True)
    color=fields.Integer()

    _sql_constraints = [
       ('unique_tag', 'unique(name)', 'The tag name should be unique!')
    ]

###########################################
class EstatePropertyOffer(models.Model):
    _name="estate.offer"
    _description="An offer to a property"
    _order = "price desc"
    price=fields.Float(required=True,string="Offered Price")
    Status=fields.Selection(string="Status",
        selection=[("accepted","Accepted"),("refused","Refused")],
        help="The status of the offer")
    partner_id=fields.Many2one('res.partner', string='Offer maker',copy=False,Required=True)
    property_id=fields.Many2one('estate.property',string="Property",ondelete ='cascade')
    validity=fields.Integer(string="Validity (Days)",default=7)
    create_date=fields.Date(copy=False,default=lambda self: fields.Datetime.now())
    date_deadline=fields.Date(compute="_compute_deadline", inverse="_inverse_deadline")
    property_type_id=fields.Many2one("estate.type",related="property_id.type",store=True )

    _sql_constraints = [
        ('price_check', 'CHECK(price >= 0)',
         'The offered price must be strictly positive')
    ]

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
            if record.property_id.state!="sold" and record.property_id.state!="canceled":
                record.Status = "accepted"
                record.property_id.selling_price=record.price
                record.property_id.buyer=record.partner_id
                record.property_id.state="Offer_Accepted"
            else:
                raise UserError("An offer for a sold or canceled property cannot be accepted.")
        return True

    def action_refuse(self):
        for record in self:
            if record.property_id.state!="sold" and record.property_id.state!="canceled":
                record.Status = "refused"
                if  record.property_id.selling_price!=0:
                    #record.property_id.selling_price=0
                    #record.property_id.buyer=""
                    pass
                # record.property_id.state="Offer_Refused"
            else:
                raise UserError("The property has been either sold or canceled, thus refusing an offer is no longer valid.") 
        return True

    @api.model
    def create(self, vals):        
        query ="SELECT * FROM estate_offer where property_id="+str(vals['property_id'])
        self.env.cr.execute(query)
        result=self.env.cr.fetchall()
        if len(result)==0: # To ensure the offer received status is obtained only once when an offer appears.
            self.env.cr.execute("UPDATE estate_property SET state='Offer_Received' WHERE id="+str(vals['property_id']))
        # Then call super to execute the parent method
        return super(EstatePropertyOffer,self).create(vals)
 
    @api.ondelete(at_uninstall=False)
    def _unlink_if_Status_null(self):
        for record in self:
            query ="SELECT * FROM estate_offer where property_id="+str(record.property_id.id)
            self.env.cr.execute(query)
            result=self.env.cr.fetchall()
            print("Result:",len(result))
            if len(result)==1:
                self.env.cr.execute("UPDATE estate_property SET state='new' WHERE id="+str(record.property_id.id))
                #record.property_id.state='new'


# class InheritedModel(models.Model):
#     _inherit = "res.users"
#     property_ids = fields.One2many('estate.property',"salesperson")
