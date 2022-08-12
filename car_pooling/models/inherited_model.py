from email.policy import default
from odoo import api,fields, models
from odoo.exceptions import UserError,ValidationError


class InheritedModel(models.Model):
    _inherit = "res.users"
    phone_number=fields.Char()
    is_volunteer=fields.Selection(
        string="Are you volunteer to participate in Car pooling?",
        selection=[("no","No"),("yes","Yes")],
        default="no")
    car_name=fields.Char(strting="Vehicle Name", required=True, default="My car name")
    Car_model=fields.Char(string="Vehicle Model", help="It is to specify the vehicle model like BMW 218i Gran Coupe")
    car_type=fields.Selection(
        string="Vehicle Type",
        selection=[("SUv","SUV"),("Hatchback","Hatchback"),("Crossover","Crossover"),("Convertible","Convertible"),('Sedan','Sedan'),('Sports_Car','Sports Car')
        ,('Coupe','Coupe'),('Minivan','Minivan'),('Station_Wagon','Station Wagon'),('Pickup_Truck','Pickup Truck')],
        default="Sedan")
    car_plate_number=fields.Char(string="Vehicle plate Number", required=True, default="My car plate number")
    car_color = fields.Char(string="Vehicle Color",help="Choose your color")
    Car_image = fields.Binary("Upload Vehicle Image", attachment=True,store=True,
                            help="This field holds the vehicle image ")

    @api.constrains('phone_number')
    def _check_phone_number(self):
        for record in self:
            if record.phone_number!='':
                if not str(record.phone_number).isdigit() or len(record.phone_number) != 10:
                    raise ValidationError(("Cannot enter invalid phone number"))
        return True
