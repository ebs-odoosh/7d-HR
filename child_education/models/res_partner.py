from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        @Author:Bhavesh Jadav TechUltra Soluation
        @Date: 25/01/2021
        @Func:This method inherit for the add dynamic domain in the child
        @Return:result of supper call of the specific children id
        """
        if self._context.get('is_child_education_child_id_request_dynamic_domain') or self._context.get(
                'is_child_education_eligibility_dynamic_domain'):
            employee_id = self._context.get('employee_id') and self.env['hr.employee'].browse(
                self._context.get('employee_id'))
            if employee_id:
                contact_relation_types = self.env['contact.relation.type'].search(
                    [('name', 'in',
                      ['Son', 'Child', 'Daughter', 'SON', 'CHILD', 'DAUGHTER', 'son', 'child', 'daughter'])])
                if self._context.get('is_child_education_child_id_request_dynamic_domain'):
                    query = """Select array_agg(id) as children from  res_partner where state = 'approved' and related_employee= {} and 
                    contact_relation_type_id in {}  """.format(
                        employee_id.id, tuple(contact_relation_types.ids))
                    self.env.cr.execute(query)
                    query_result = self.env.cr.dictfetchall()
                    res = query_result and query_result[0].get('children', [])
                    return res
                elif self._context.get('is_child_education_eligibility_dynamic_domain'):
                    specific_children = self.env['res.partner']
                    if self._context.get('education_eligibility_id'):
                        query = """Select array_agg(child_id) as children from  specific_child_education_eligibility where 
                        education_eligibility_id= {} """.format(
                            self._context.get('education_eligibility_id'))
                        self.env.cr.execute(query)
                        query_result = self.env.cr.dictfetchall()
                        specific_children = query_result and query_result[0].get('children', [])
                    if specific_children:
                        query = """Select array_agg(id) as children from  res_partner where state = 'approved' and related_employee= {} and 
                                        contact_relation_type_id in {} and id not in {} """.format(employee_id.id,
                                                                                                   tuple(
                                                                                                       contact_relation_types.ids),
                                                                                                   tuple(
                                                                                                       [
                                                                                                           specific_children[
                                                                                                               0],
                                                                                                           -1] if len(
                                                                                                           specific_children) == 1 else specific_children))
                    else:
                        query = """Select array_agg(id) as children from  res_partner where state = 'approved' and related_employee= {} and 
                                                                contact_relation_type_id in {}""".format(
                            employee_id.id, tuple(contact_relation_types.ids))

                    self.env.cr.execute(query)
                    query_result = self.env.cr.dictfetchall()
                    res = query_result and query_result[0].get('children', [])
                    return res
            else:
                res = []
                return res

        res = super(ResPartner, self)._search(args, offset, limit, order, count, access_rights_uid)
        return res
