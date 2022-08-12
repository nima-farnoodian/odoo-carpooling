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
    departure_date = fields.Datetime(string="Departure Date and Time", required=True)
    capacity=fields.Integer(string="Number of seats",required=True)
    filled_seat=fields.Integer(string="Number of filled seats",readonly=True)
    available_seat=fields.Integer(compute="_compute_available_seat", store=True, string="Available seats")

    status=fields.Selection(
        string="Status",
        selection=[("available","Available"),("full","Full"),("unavailable","Unavailable"),("departed","Departed"),('canceled','Canceled')],
        default="available")
    # @api.depends('departure_date',"departure_time")
    # def _compute_unavailable_state(self):
    #     for record in self:
    #         now =datetime.datetime.now()
    #         if record.departure_date < now:
    #             record.status = "unavailable"
            
            

    
    comments=fields.Text(help="The comments for the trips")
    tag=fields.Many2many("car.pooling.tag",string="Tags")
    is_round_trip=fields.Boolean(string="Round Trip")
    return_date = fields.Datetime(string="Return Date and Time")

    # capacity_return=fields.Integer(string="Capacity for return", required=True)
    passenger_ids=fields.One2many("car.pooling.passenger","trip_id",string="Passengers")


    is_current_user_driver = fields.Boolean(compute="_is_current_user_driver")
    @api.depends('driver')
    # adopted from https://github.com/hlibioulle/OpenWeek-odoo-carpooling/blob/main/carpooling/models/vehicle_trip.py
    def _is_current_user_driver(self):
        for record in self:
            record.is_current_user_driver = (record.driver == self.env.user)

    current_user_is_passenger = fields.Boolean(compute="_compute_current_user_is_passenger")
    @api.depends("passenger_ids")
    # adopted from https://github.com/hlibioulle/OpenWeek-odoo-carpooling/blob/main/carpooling/models/vehicle_trip.py
    def _compute_current_user_is_passenger(self):
        for record in self:
            record.current_user_is_passenger = (self.env.user in record.passenger_ids.passenger)

    current_user_book_status = fields.Char(compute="_compute_current_user_book_status",string="Booking status")
    def _compute_current_user_book_status(self):
        for record in self:
            record.current_user_book_status="Undecided"
            query ="SELECT * FROM car_pooling_passenger where passenger=" + str(self.env.user.id) + " and trip_id=" + str(record.id)
            self.env.cr.execute(query)
            result=self.env.cr.fetchall()
            print("Result for status:",result)
            if len(result)>0:
                if result[0][3]=="accepted":
                    record.current_user_book_status="Accepted"
                if result[0][3]=="refused":
                    record.current_user_book_status="Refused" 
                else:
                     record.current_user_book_status="Undecided"

    @api.depends("capacity","filled_seat")
    def _compute_available_seat(self):
        for record in self:
            record.available_seat = record.capacity- record.filled_seat
    
    car_name = fields.Char(compute="_car_name")
    @api.depends('driver')
    def _car_name(self):
        for record in self:
            record.car_name = record.driver.car_name
    
    Car_model = fields.Char(compute="_car_model")
    @api.depends('driver')
    def _car_model(self):
        for record in self:
            record.Car_model = record.driver.Car_model
    
    car_type = fields.Char(compute="_car_type")
    @api.depends('driver')
    def _car_type(self):
        for record in self:
            record.car_type = record.driver.car_type

    car_plate_number = fields.Char(compute="_car_plate_number")
    @api.depends('driver')
    def _car_plate_number(self):
        for record in self:
            record.car_plate_number = record.driver.car_plate_number

    car_color = fields.Char(compute="_car_color")
    @api.depends('driver')
    def _car_color(self):
        for record in self:
            record.car_color = record.driver.car_color

    Car_image = fields.Binary(attachment=True,store=True,compute="_car_image")
    @api.depends('driver')
    def _car_image(self):
        for record in self:
            record.Car_image = record.driver.Car_image

 
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
    def book_or_unbook(self):
        for record in self:
            if self.env.user in record.passenger_ids.passenger:
                query ="SELECT * FROM car_pooling_passenger where passenger=" + str(self.env.user.id) + " and trip_id=" + str(record.id)
                self.env.cr.execute(query)
                result=self.env.cr.fetchall()
                if result[0][3]=="accepted":
                    msg="You cannot unbook the trip because the book has been accepted by the driver. Contact " + str(record.driver.name) + " at " + str(record.driver.email) + " or by " + str(record.driver.phone_number) + " to ask booking refusal."
                    raise UserError(msg)
                query_exc="delete from car_pooling_passenger where passenger=" + str(self.env.user.id) + " and trip_id=" + str(record.id)
            else:
                query_exc="INSERT INTO car_pooling_passenger (passenger, trip_id) VALUES ("+ str(self.env.user.id) +","+ str(record.id)+");"
            self.env.cr.execute(query_exc)

        return True

    _sql_constraints = [
        ('seat_no_check', 'CHECK(capacity >= 0)',
         'The seat number cannot be negative!'),
        ('available_seat_check', 'CHECK(filled_seat <= capacity)',
         "The capacity of the vehicle must be equal to or greater than the number of filled seats! To reduce the capacity, refuse some passengers' accepted requests.")
    ]

    @api.constrains('res_phone_number')
    def _check_phone_number(self):
        for record in self:
            if record.phone_number!='':
                if not str(record.phone_number).isdigit() or len(record.phone_number) != 10:
                    raise ValidationError(("Cannot enter invalid phone number"))
        return True


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
                    msg="The book has been accepted. To delete the book, the book request must be first refused by the drive. If you are not the drive, please contact him/her to refuse your book request."   
                elif record.trip_id.status=='departed':
                    msg="The trip is in departed status. An accepted book request for a departed trip cannot be removed."   
                print("Message:",msg)
                raise UserError(msg)
        
##############################################################

