# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang



class Code(models.Model):
    _name = 'veterinary.code'
    name = fields.Char(string='Nombre')
    code = fields.Char(string='Código')
    category = fields.Char(string='Categoría', domain="{'Diagnóstico', 'Procedimiento', 'Tratamiento farmacológico', 'Otro'}" )
