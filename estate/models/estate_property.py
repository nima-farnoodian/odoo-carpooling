from dataclasses import field
from datetime import datetime
from email.policy import default
from sqlite3 import Date
from xmlrpc.client import DateTime

from pkg_resources import require
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
        help="The orientation of the place."
    )
    active=fields.Boolean(default=True)
    Status=fields.Selection(
        string="Status",
        selection=[("new","New"),("Offer_Received","Offer Received"),("Offer_Accepted","Offer Accepted,"),("sold","Sold"),('canceled','Canceled')]
        )
