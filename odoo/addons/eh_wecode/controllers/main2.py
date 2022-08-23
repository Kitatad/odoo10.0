from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from requests import post


class WasteManagment(http.Controller):
    @http.route('/waste_management_request_webform', type="http", auth="public", website=True)
    def Waste_managment_webform(self, **kw):
        doctor_rec = request.env['waste.management.request'].sudo().search([])
        return http.request.render('eh_wecode.create_wast_request')