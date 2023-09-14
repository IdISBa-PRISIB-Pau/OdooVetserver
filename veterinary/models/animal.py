# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta 

class Animal(models.Model):
    _name = 'veterinary.animal'

    @api.depends('dob')
    def onchange_age(self):
        if self.dob:
            dt = self.dob
            born = datetime.strptime(dt, "%Y-%m-%d").date()
            today = datetime.today()
            years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            months = (today.month, today.day) - (born.month, born.day)
            self.age = years + " años y " + months + " meses"
        else:
            self.age = "Sin fecha de nacimiento!!"

    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    name = fields.Char('Nombre', required=True)
    microchip_number = fields.Char('Microchip/Número de historia',required=True)
    dob = fields.Date('Fecha de nacimiento', required=True)
    age = fields.Char(compute=onchange_age,string="Edad",store=True)
    appointment_id = fields.Many2many('veterinary.appointment')
    total_appointment = fields.Char('Total',compute='_total_appointment')
    colour =fields.Selection (
        (('b','Blanco'),('c','Claro'), ('o','Oscuro') , ('n','Negro'),('other','Otro'))
        ,required=False, string='Color')
    sex =fields.Selection ((
        ('f','Femenino'),('m','Masculino'), ('d','Desconocido'))
        ,required=True, string='Sexo')
    species =fields.Selection ((
        ('cat','Gato'),('dog','Perro'),('other','Otros'))
        ,required=True,string="Especie")
    bread =fields.Selection ((
        ('m','Mascota'),('cr','Criador'),
        ('p','Protectora'),('other','Otro'))
        ,required=True,string="Procedencia")
    breed = fields.Many2one('veterinary.breed',string='Raza', required=False)    
    partner_id = fields.Many2one('res.partner',string='Dueño', required=True)
    evaluation = fields.One2many('veterinary.evaluation','animal',readonly=True)
    bloodtest = fields.One2many('veterinary.bloodtest','animal',readonly=True)
    citology = fields.One2many('veterinary.citology','animal',readonly=True)
    echo = fields.One2many('veterinary.echo','animal',readonly=True)
    xr = fields.One2many('veterinary.xr','animal',readonly=True)

    _sql_constraints = [
    ('microchio_uniq', 'unique(microchip_number)', 'Microchip already exists!')
    ]

    @api.multi
    def _total_appointment(self):
        self.total_appointment = len(self.appointment_id)

    def appointment_view(self):
        action = self.env.ref('veterinary.action_appointment_form')
        result = action.read()[0]
        result['domain'] = [('animals', '=', self.id)]
        return result

    def calculate_age(self):        
        today = date.today()
        self.age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner'
    animal_picking_id = fields.One2many('veterinary.animal','partner_id', string="Animal Id")

    def open_animal(self):
        action = self.env.ref('veterinary.action_animal_form')
        result = action.read()[0]
        result['domain'] = [('partner_id', '=', self.id)]
        return result

class Breed(models.Model):
    _name = 'veterinary.breed'
    name = fields.Char('Nombre', required=True)
