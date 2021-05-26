# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models
import base64
from odoo.modules.module import get_module_resource

org_chart_classes = {
    0: "level-0",
    1: "level-1",
    2: "level-2",
    3: "level-3",
    4: "level-4",
}


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_employee_domain(self, parent_id):
        # company = self.env.company
        # Take Company from Current User
        company = self.env.user.company_id

        domain = ["|", ("company_id", "=", False), ("company_id", "=", company.id)]
        if not parent_id:
            domain.extend([("parent_id", "=", False), ("child_ids", "!=", False)])
        else:
            domain.append(("parent_id", "=", parent_id))
        return domain

    def get_class_name(self):
        self = self.sudo()
        result = ''
        # nationality = self.country_id.id
        group = self.contract_id.contract_group.id
        subgroup = self.contract_id.contract_subgroup.id
        employment_type = self.contract_employment_type.id
        resignations = self.contract_id.related_resign_request.filtered(
            lambda x: x.state in ('open', 'active', 'extended'))
        if len(resignations) > 0:
            color_combo = self.env['employee.color.combo'].search(
                [('leaver', '=', True)], limit=1)
        else:
            color_combo = self.env['employee.color.combo'].search(
                [('subgroup_id', '=', subgroup), ('group_id', '=', group),
                 ('employment_type_id', '=', employment_type)], limit=1)

            # color_combo = self.env['employee.color.combo'].search(
            #     [('nationality_id', 'in', [nationality, False]), ('subgroup_id', 'in', [subgroup, False]),
            #      ('group_id', 'in', [group, False]),
            #      ('employment_type_id', 'in', [employment_type, False])], limit=1)

        if color_combo:
            color_class_id = color_combo.name.get_external_id()
            result = color_class_id.get(color_combo.name.id).split('.')[1]
        return result

    def _get_employee_data(self, level=0):
        self = self.sudo()
        # added invisible character in order to divide the string client side

        node_content = self.prepare_node_content()
        class_name = self.get_class_name()

        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        default_image = base64.b64encode(open(image_path, 'rb').read())

        return {
            "id": self.id,
            "name": self.name,
            "title": node_content,
            # "className": org_chart_classes[level],
            "className": class_name,
            'collapsed': True,
            "image": self.env["ir.attachment"]
                .sudo()
                .search(
                [
                    ("res_model", "=", "hr.employee"),
                    ("res_id", "=", self.id),
                    ("res_field", "=", "image_512"),
                ],
                limit=1,
            )
                .datas if self.env["ir.attachment"].sudo().search([
                ("res_model", "=", "hr.employee"),
                ("res_id", "=", self.id),
                ("res_field", "=", "image_512"),
            ], limit=1, ).datas else default_image
            ,
        }

    def prepare_node_content(self):
        """
        :Author:Bhavesh Jadav  TechUltra Solutions
        :Date:25/09/2020
        :Func:This method use for the prepare node content
        :Return:content:str: single  node content
        """
        self = self.sudo()
        job_title = str(self.contract_id.job_title.name) if self.contract_id.job_title.name else '‎'
        job_position = str(self.contract_id.job_id.name) if self.contract_id.job_id.name else '‎'
        department_name = str(self.department_id.name) if self.department_id.name else '‎'
        parent_department_code = str(
            self.department_id.parent_id.code) if self.department_id and self.department_id.parent_id and self.department_id.parent_id.code else '‎'
        department_code = str(self.department_id.code) if self.department_id.code else '‎'
        system_id = str(self.system_id) if self.system_id else '‎'
        department_full_name = str(self.department_id.display_name) if self.department_id.display_name else '‎'
        parent_department_full_name = str(
            self.department_id.parent_id.display_name) if self.department_id and self.department_id.parent_id else '‎'
        content = '''<style> .hide {display: none;} .myDIV:hover + .hide {display:block;color: black;}</style>
        <div><b>''' + department_name + '''</b></div>
        <div class="myDIV">''' + department_code + '''</div>
        <div class="hide">''' + department_full_name + '''</div>
        <div class="myDIV">''' + parent_department_code + '''</div>
        <div class="hide">''' + parent_department_full_name + '''</div>
        <hr></hr>
        <div>''' + system_id + '''</div>
        <div>''' + job_title + '''</div>
        <div>''' + job_position + '''</div>
        '''
        return content

    @api.model
    def get_organization_data(self):
        # First get employee with no manager
        domain = self._get_employee_domain(False)
        top_employee = self.search(domain, limit=1)
        data = top_employee._get_employee_data()
        data.update({'collapsed': False})
        # If any child we fetch data recursively for childs of top employee
        top_employee_child_ids = self.search(self._get_employee_domain(top_employee.id))
        if top_employee_child_ids:
            print("-------------------",top_employee_child_ids)
            top_employee_child_ids = self.employee_sorting(employees=top_employee_child_ids)
            data.update(
                {"children": self._get_children_data(top_employee_child_ids, 1)}
            )
        return data

    def employee_sorting(self, employees):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 25/09/2020
        :Func:This method use to sort employees based on the department name alphabet
        :return: sorted_employees
        """

        department_names = [emp.department_id.name for emp in employees]
        # department_names = employees.department_id.mapped('name')
        department_names.sort()
        sorted_employees = self.env['hr.employee']
        for department_name in department_names:
            sorted_employees += employees.filtered(
                lambda employee: employee.department_id and employee.department_id.name == department_name)
        return sorted_employees

    def search_department_result(self, value1=False, value2=False, value3=False, value4=False, value5=False,
                                 value6=False, value7=False, value8=False):
        """
        Author:Bhavesh Jadav Techultra soluation
        Date: 18/08/2020
        Func: This method use for the prepare domain from the search criteria
        and search employee and call other method for the hierarchy
        :param value1: use for the employee
        :param value2: use for the group
        :param value3: use for the department
        :param value4: use for the section
        :param value5: use for the subsection
        :param value6: use for the job title
        :param value7: use for the job position
        :param value8: use for the starta id
        :return: prepared data dictionary for tree
        """
        domain = []
        if value1:
            domain.append(('id', '=', int(value1)))
        if value6:
            domain.append(('contract_id.job_title', '=', int(value6)))
        if value7:
            domain.append(('job_id', '=', int(value7)))
        if value8:
            domain.append(('system_id', '=', value8))
            # domain.append(('company_employee_id', '=', value8))
        if value2 and value2 != '' and value3 == '' and value4 == '' and value5 == '':
            domain.append(('contract_id.group', '=', int(value2)))
        if value3 and value3 != '' and value4 == '' and value5 == '':
            domain.append(('contract_id.department', '=', int(value3)))
        if value4 and value4 != '' and value5 == '':
            domain.append(('contract_id.section', '=', int(value4)))
        if value5 and value5 != '':
            domain.append(('contract_id.subsection', '=', int(value5)))
        if len(domain) > 0:
            employees = self.env['hr.employee'].search(domain)
            if employees:
                employees_data = self.env['hr.employee'].browse(
                    list(set(list(set(self.get_parent_and_child(employees))) + list(set(self.get_child(employees))))))
                # employees_data = self.env['hr.employee'].browse(list(set(self.get_parent_and_child(employees)))) + \
                #                  self.env['hr.employee'].browse(list(set(self.get_child(employees))))
                # employees_data = employees_data + employees.child_ids
                # child_data = self.env['hr.employee'].browse(list(set(self.get_child(employees))))
                # employees_data = employees_data + child_data
                data = self.prepare_hierarchy(employees_data)
                return data

    def prepare_hierarchy(self, employees_data):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date: 20/08/2020
        :param employees_data: result of the search employees id
        :return: prepared data dictionary for tree
        """
        top_employee = employees_data.filtered(lambda emp: not emp.parent_id)
        # if we search from group then we are found 4 employee without manager
        # then we are set fix manager with (Ismail Ali Mohammad Sulaiman Abdulla)
        if len(top_employee) > 1:
            top_employee = top_employee.filtered(lambda emp: emp.id == 9398)
            if not top_employee:
                return False
        data = top_employee._get_employee_data()
        data.update({'collapsed': False})
        top_employee_child_ids = employees_data.filtered(lambda emp: emp.parent_id == top_employee)
        if top_employee_child_ids:
            data.update(
                {"children": self._get_children_data(top_employee_child_ids, 1, employees_data)}
            )
        return data

    @api.model
    def _get_children_data(self, child_ids, level, employees_data=False):
        """
        Changes by :Bhavesh Jadav TechUltra solutions
        Date: 20/08/2020
        Func: if user search then prepared data dictionary base on search
        :param employees_data: result of the search employees id
        :return: prepared data dictionary for tree
        """
        children = []
        for employee in child_ids:
            data = employee._get_employee_data(level)
            if employees_data:
                data.update({'collapsed': False})
                employee_child_ids = employees_data.filtered(lambda emp: emp.parent_id == employee)
            else:
                employee_child_ids = self.search(self._get_employee_domain(employee.id))
            if employee_child_ids:
                employee_child_ids = self.employee_sorting(employees=employee_child_ids)
                data.update(
                    {
                        "children": self._get_children_data(employee_child_ids, (level + 1) % 5, employees_data)
                    }
                )
            children.append(data)
        return children

    def get_parent_and_child(self, employee):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date: 20/08/2020
        :param employee: use for the child id of the employee
        :return: data list of the all parent nid
        """
        if len(employee.mapped('parent_id').ids):
            parents = employee.mapped('parent_id')
            data = self.get_parent_and_child(parents)
            return data + [e.id for e in employee]
        else:
            return [employee.id]

    def get_child(self, child_ids):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date: 25/08/2020
        :param child_ids:use for the child id of the employee
        :return: data list of the all child id
        """
        data = []
        for employee in child_ids:
            if employee.child_ids:
                data = self.get_child(employee.child_ids) + [e.id for e in employee.child_ids]
        return data


class Department(models.Model):
    _inherit = "hr.department"

    def get_department_data(self):
        data_dict = {}
        hr_department_obj = self.env['hr.department']
        job_positions = self.env['hr.job'].search_read(domain=[], fields=['id', 'name'])
        job_titles = self.env['job.title'].search_read(domain=[], fields=['id', 'name'])
        employees = self.env['hr.employee'].search_read(domain=[], fields=['id', 'name'])
        groups = hr_department_obj.search_read(domain=[('type', '=', 'BU')], fields=['id', 'name'])
        departments = hr_department_obj.search_read(domain=[('type', '=', 'BD')], fields=['id', 'name'])
        sections = hr_department_obj.search_read(domain=[('type', '=', 'BS')], fields=['id', 'name'])
        subsection = hr_department_obj.search_read(domain=[('type', '=', 'SS')], fields=['id', 'name'])
        data_dict.update(
            {'groups': groups, 'departments': departments, 'sections': sections, 'subsections': subsection,
             'employees': employees, 'job_titles': job_titles, 'job_positions': job_positions})
        return data_dict

    def get_department_from_searchbar(self, dict):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:26/08/2020
        :param dict: use for the search bar name and value from the js
        :return: dict for the department section or sub section
        """
        data_dict = {}
        datas = []
        hr_department_obj = self.env['hr.department']
        if dict.get('searchbar_name') == 'group' and not dict.get('searchbar_value') == '':
            datas = hr_department_obj.search_read(
                domain=[('type', '=', 'BD'), ('parent_id', '=', int(dict.get('searchbar_value')))],
                fields=['id', 'name'])
        elif dict.get('searchbar_value') == '':
            datas = hr_department_obj.search_read(
                domain=[('type', '=', 'BD')],
                fields=['id', 'name'])
        if dict.get('searchbar_name') == 'departments' and not dict.get('searchbar_value') == '':
            datas = hr_department_obj.search_read(
                domain=[('type', '=', 'BS'), ('parent_id', '=', int(dict.get('searchbar_value')))],
                fields=['id', 'name'])
        elif dict.get('searchbar_value') == '':
            datas = hr_department_obj.search_read(
                domain=[('type', '=', 'BS')],
                fields=['id', 'name'])
        if dict.get('searchbar_name') == 'sections' and not dict.get('searchbar_value') == '':
            datas = hr_department_obj.search_read(
                domain=[('type', '=', 'SS'), ('parent_id', '=', int(dict.get('searchbar_value')))],
                fields=['id', 'name'])
        elif dict.get('searchbar_value') == '':
            datas = hr_department_obj.search_read(
                domain=[('type', '=', 'SS')],
                fields=['id', 'name'])
        for data in datas:
            data_dict.update({data.get('id'): data.get('name')})
        return data_dict
