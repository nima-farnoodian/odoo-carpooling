import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError
from  odoo.tools import float_utils


class CarPooling(models.Model):
    _name = "car.pooling"
    _description = "Trips"
    _order = "id desc"
    driver=fields.Many2one('res.users',required=True,readonly=True, string='Driver (Car owner)', index=True, tracking=True, default=lambda self: self.env.user)
    source_city=fields.Char(required=True)
    source_address=fields.Char(required=True)
    destination_city=fields.Char(required=True)
    destination_address=fields.Char(required=True)
    departure_date=fields.Date(copy=False,default=lambda self: fields.Datetime.now())
    departure_time = fields.Float('Departure Time',required=True)
    capacity=fields.Integer(string="Number of seats",required=True)
    filled_seat=fields.Integer(string="Number of filled seats",readonly=True)
    available_seat=fields.Integer(compute="_compute_available_seat", store=True, string="available seats")

    status=fields.Selection(
        string="Status",
        selection=[("available","Available"),("full","Full"),("unavailable","Unavailable"),("departed","Departed"),('canceled','Canceled')],
        default="available")
    comments=fields.Char(help="The comments for the trips")
    tag=fields.Many2many("car.pooling.tag",string="Tags")
    is_round_trip=fields.Boolean(string="Round Trip")
    return_date=fields.Date(copy=False,default=lambda self: fields.Datetime.now())
    return_time = fields.Float('Return Time',copy=False)
    # capacity_return=fields.Integer(string="Capacity for return", required=True)
    passenger_ids=fields.One2many("car.pooling.passenger","trip_id",string="Passengers")


    @api.depends("capacity","filled_seat")
    def _compute_available_seat(self):
        for record in self:
            record.available_seat = record.capacity- record.filled_seat

 
    def cancel_action(self):
        # This function is responsible for canceling a trip if the trip is not in "departed" status.
        for record in self:
            if record.status=="departed":
                raise UserError("The departed trip cannot be canceled")
            else:
                record.status="canceled"

    def depart_action(self):
        # This function is responsible for changing the trip status to "departed" status.
        for record in self:
            if record.status=="canceled":
                raise UserError("The canceled trip cannot be in 'departed' status")
            else:
                record.status="departed"

    _sql_constraints = [
        ('seat_no_check', 'CHECK(capacity >= 0)',
         'The seat number cannot be negative!'),
        ('available_seat_check', 'CHECK(filled_seat <= capacity)',
         "The capacity of the vehicle must be equal to or greater than the number of filled seats! To reduce the capacity, refuse some passengers' accepted requests.")
    ]

    #On write and On-delete and create api should be added to avoid inconsistency (e.g., what if we update the capacity while it is in full status?)
    @api.model
    def create(self, vals):        
        if vals['capacity']==0:
            raise UserError("The Number of seats (Vehicle Capacity) should be greater than zero!")
        # Then call super to execute the parent method
        return super(CarPooling,self).create(vals)
    @api.ondelete(at_uninstall=False)
    def _unlink_if_passenger_refused(self):
        if any(record.passenger_ids.status=="accepted" for record in self):
                msg="There are some passengers in 'accepted' status for this trip. To delete the trip, please make sure you have refused all passenger book requests."   
                print("Message:",msg)
                raise UserError(msg)

    def write (self,vals):
        # on_write for updating capacity. (e.g., what if we update the capacity while it is in full status?)
        if "filled_seat" in vals and "capacity" in vals:
            if vals['capacity']- vals['filled_seat']==0 and self.status not in ('unavailable','departed','canceled'):
                vals["status"]='full'
            elif vals['capacity']- vals['filled_seat']>0  and self.status not in ('unavailable','departed','canceled'):
                vals["status"]='available'
        elif  "filled_seat" not in vals and "capacity" in vals:
            if vals['capacity']- self.filled_seat==0 and self.status not in ('unavailable','departed','canceled'):
                vals["status"]='full'
            elif vals['capacity']- self.filled_seat>0  and self.status not in ('unavailable','departed','canceled'):
                vals["status"]='available'
        elif "filled_seat" in vals and "capacity" not in vals:
            if self.capacity- vals['filled_seat']==0 and self.status not in ('unavailable','departed','canceled'):
                vals["status"]='full'
            elif self.capacity- vals['filled_seat']>0  and self.status not in ('unavailable','departed','canceled'):
                vals["status"]='available'
        super(CarPooling,self).write(vals)
    
    #TODO Book action with its button should be added such that it inserts the user to the passenger list
#############################################################
class CarPoolingTag(models.Model):
    _name="car.pooling.tag"
    _description = "A trip tag is, for example, a trip which is ‘long’ or ‘short’."
    _order = "name"
    name=fields.Char(required=True)
    color=fields.Integer()

    _sql_constraints = [
       ('unique_tag', 'unique(name)', 'The tag name should be unique!')
    ]

#############################################################

class CarPoolingPassenger(models.Model):
    _name = "car.pooling.passenger"
    _description = "Passenger"
    _order = "id desc"
    passenger= fields.Many2one('res.users',required=True,readonly=True, string='Passenger', index=True, tracking=True, default=lambda self: self.env.user)
    trip_id=fields.Many2one('car.pooling',string="Trip",ondelete ='cascade')
    status=fields.Selection(string="Status",
        selection=[("accepted","Accepted"),("refused","Refused")],
        help="The status of the trip offer")


    #TODO complete the following functions 
    def action_accept(self):
        #TODO add automatic odoo message (Accpeted) sent to the passanger
        for record in self:
            if record.trip_id.status!="departed" and record.trip_id.status!="canceled":
                if record.trip_id.filled_seat<record.trip_id.capacity:
                    record.trip_id.filled_seat=record.trip_id.filled_seat+1
                    record.status="accepted"
                    if  record.trip_id.filled_seat==record.trip_id.capacity:
                        record.trip_id.status="full"
                else:
                    raise UserError("The vehicle does not have capacity for more passengers.")
            else:
                raise UserError("No passenger can be added to a departed or canceled trip.")
        return True

    def action_refuse(self):
        #TODO add automatic odoo message (Refuse) sent to the passanger
        for record in self:
            if record.trip_id.status!="departed" and record.trip_id.status!="canceled":
                record.status = "refused"
                record.trip_id.filled_seat=record.trip_id.filled_seat-1
                record.trip_id.status="available"
            else:
                raise UserError("No passenger can be removed from a departed or canceled trip.")
        return True
    
    @api.ondelete(at_uninstall=False)
    def _unlink_if_passenger_refused(self):
        for record in self:
            if record.status=="accepted":
                if record.trip_id.status!='departed':
                    msg="The book has been accepted. To delete the book, first refuse the book requests."   
                elif record.trip_id.status=='departed':
                    msg="The trip is in departed status. An accepted book request for a departed trip cannot be removed."   
                print("Message:",msg)
                raise UserError(msg)
        
##############################################################

