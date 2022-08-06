from odoo import fields, models

class InheritedModel(models.Model):
    _inherit = "res.users"
    is_volunteer=fields.Boolean(string="Are you volunteer to participate in Car pooling?",require=True)
    car_name=fields.Char(strting="Vehicle Name", required=True)
    Car_model=fields.Char(string="Vehicle Model", help="It is to specify the vehicle model like BMW 218i Gran Coupe")
    car_type=fields.Selection(
        string="Vehicle Type",
        selection=[("SUv","SUV"),("Hatchback","Hatchback"),("Crossover","Crossover"),("Convertible","Convertible"),('Sedan','Sedan'),('Sports_Car','Sports Car')
        ,('Coupe','Coupe'),('Minivan','Minivan'),('Station_Wagon','Station Wagon'),('Pickup_Truck','Pickup Truck')],
        default="Sedan")
    car_plate_number=fields.Char(string="Vehicle registration plate Number", required=True)
    car_color=fields.Integer(required=True, string="Vehicle Color")
    Car_image = fields.Binary("Upload Vehicle Image", attachment=True,store=True,
                            help="This field holds the vehicle image ")

    #fields.Image