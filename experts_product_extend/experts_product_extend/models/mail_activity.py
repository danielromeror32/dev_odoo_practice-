# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Daniel Acosta (daniel.acosta@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################
from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError 
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)

class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, summary='', note='', **act_values):
        """ Schedule an activity on each record of the current record set.
        This method allow to provide as parameter act_type_xmlid. This is an
        xml_id of activity type instead of directly giving an activity_type_id.
        It is useful to avoid having various "env.ref" in the code and allow
        to let the mixin handle access rights.

        :param date_deadline: the day the activity must be scheduled on
        the timezone of the user must be considered to set the correct deadline
        """
        if self.env.context.get('mail_activity_automation_skip'):
            return False

        if not date_deadline:
            date_deadline = fields.Date.context_today(self)
        if isinstance(date_deadline, datetime):
            _logger.warning("Scheduled deadline should be a date (got %s)", date_deadline)
        if act_type_xmlid:
            activity_type = self.env.ref(act_type_xmlid, raise_if_not_found=False) or self._default_activity_type()
        else:
            activity_type_id = act_values.get('activity_type_id', False)
            activity_type = activity_type_id and self.env['mail.activity.type'].sudo().browse(activity_type_id)

        model_id = self.env['ir.model']._get(self._name).id
        activities = self.env['mail.activity']
        for record in self:
            create_vals = {
                'activity_type_id': activity_type and activity_type.id,
                'summary': summary or activity_type.summary,
                'automated': True,
                'note': note or activity_type.default_description,
                'date_deadline': date_deadline,
                'res_model_id': model_id,
                'res_id': record.id,
                'user_id': act_values.get('user_id') or activity_type.default_user_id.id or self.env.uid
            }
            create_vals.update(act_values)
            try:
                activities |= self.env['mail.activity'].create(create_vals)
            except:
                activities |= self.env['mail.activity'].sudo().create(create_vals)
        return activities

