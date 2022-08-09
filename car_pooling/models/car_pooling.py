import datetime

from pkg_resources import require
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
    departure_time=fields.Date(copy=False,default=lambda self: fields.Datetime.now())
    capacity=fields.Integer(required=True)
    status=fields.Selection(
        string="Status",
        selection=[("available","Available"),("full","Full"),("unavailable","Unavailable"),('canceled','Canceled')],
        default="available")
    
    tag=fields.Many2many("estate.tag",string="Tags")
    is_round_trip=fields.Boolean()
    return_time=fields.Date(copy=False,default=lambda self: fields.Datetime.now())
    capacity_return=fields.Integer(string="Capacity for return", required=True)
    passanger_ids=fields.One2many("car.pooling.passanger","trip_id",string="Passangers")
    

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

class CarPooling(models.Model):
    _name = "car.pooling.passanger"
    _description = "Passanger"
    _order = "id desc"
    passanger= fields.Many2one('res.users',required=True,readonly=True, string='Passanger', index=True, tracking=True, default=lambda self: self.env.user)
    trip_id=fields.Many2one('car.pooling',string="Trip",ondelete ='cascade')
    status=fields.Selection(string="Status",
        selection=[("accepted","Accepted"),("refused","Refused")],
        help="The status of the trip offer")
##############################################################

