# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang


class Evaluation(models.Model):
    _name = 'veterinary.evaluation'
    _inherit = ['mail.thread']

    @api.multi
    def default_stage(self):
        return self.env['veterinary.evaluation.stages'].search([('name', '=', 'Nueva')])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['veterinary.evaluation.stages'].search([])
        return stage_ids

    name = fields.Char('Código', compute='_compute_name')
    animal = fields.Many2one('veterinary.animal', string='Animal', readonly=True)
    appointment_id = fields.Many2one('veterinary.appointment', string='Cita')

    date = fields.Datetime(related='appointment_id.dateOfAppointment')
    description = fields.Char(string='Motivo de consulta', store=True, related='appointment_id.description')

    current_illness = fields.Text('Anamnesis')
    stage_id = fields.Many2one('veterinary.evaluation.stages', string='Estado', required=False, default=default_stage,
                               group_expand='_read_group_stage_ids')
    stage_name = fields.Char(related='stage_id.name')
    user_id = fields.Many2one('res.users', string='Doctor', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Dueño', required=True, readonly=True)
    conditions = fields.Many2many('veterinary.code', 'cod_eval_rel', 'name', 'code',
                                  domain="[('category', '=', 'Condition')]", string='Diagnósticos')
    procedures = fields.Many2many('veterinary.code', 'proc_eval_rel', 'name', 'code',
                                  domain="[('category', '=', 'Procedure')]", string='Procedimientos')
    prescriptions = fields.Many2many('product.product', 'prod_eval_rel', 'name', 'product_id', string='Prescripciones')

    # Musculoskeletal System Page
    conformation = fields.Char('Morfología')
    feet_shoeing = fields.Char('Patas')
    lf = fields.Char('Trasera izquierda')
    rf = fields.Char('Trasera derecha')
    lh = fields.Char('Delantera izquierda')
    rh = fields.Char('Delantera derecha')
    neck_back_pelvis = fields.Char('Cuello, columna, pelvis')
    flexion_tests = fields.Char('Test de flexión')
    ridden = fields.Char('Montura')
    diagnostic_imaging = fields.Char('Diagnóstico por imagen')
    walk = fields.Char('Paso')
    trot = fields.Char('Carrera')

    # Respiratory System
    res_general = fields.Char('General')
    lung_auscultation = fields.Char('Auscultación pulmonar')
    upper_airway = fields.Char('Vía aérea')

    # Cardiovascular System
    cardi_general = fields.Char('General')
    auscultation = fields.Char('Auscultación cardiovascular')
    ecg = fields.Char('ECG')

    # Gastrointestinal System
    gest_general = fields.Char('General')
    worming_history = fields.Char('Historia de desparasitación')
    teeth = fields.Char('Dentición')

    # Nervous System
    nevr_general = fields.Char('General')
    mentation = fields.Char('Consciencia')
    gait = fields.Char('Marcha')
    eyes = fields.Char('Vista')

    # Reproductive and Urinary System
    fig = fields.Char('Castración')
    testicles = fields.Char('Testículos')
    vulva = fields.Char('Vulva')

    # Skin
    scars = fields.Char('Cicatrices - Traumáticas / Quirúrgicas')
    melanomas = fields.Char('Tumores')
    Dermatitis = fields.Char('Dermatitis')
    Allergy = fields.Char('Alergias')
    skin_other = fields.Char('Otros')

    other = fields.Text('Otros')
    overall_assessment = fields.Text('Orientación diagnóstica')
    recommendations = fields.Text('Recomendaciones')

    def _compute_name(self):
        self.name = self.appointment_id.name
        return True

    @api.one
    def action_create_invoice(self):
        self.appointment_id.action_create_invoice

    @api.one
    def action_done(self):
        self.appointment_id.action_done

    @api.multi
    def action_evaluation_sent(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('veterinary', 'email_template_evaluation')[1]
        except ValueError:
            template_id = False
        ctx = {
            'default_model': 'veterinary.evaluation',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "veterinary.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }


class EvaluationStages(models.Model):
    _name = 'veterinary.evaluation.stages'
    name = fields.Char('Stage')
