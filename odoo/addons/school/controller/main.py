from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from requests import post


class LobbyRequestController(http.Controller):

    @http.route('/certificate_request_webform', type="http", auth="public", website=True)
    def lobby_webform(self, **kw):
        doctor_rec = request.env['certificate.request'].sudo().search([])
        print("doctor_rec...", doctor_rec)
        return http.request.render('school.create_certificate_request')
