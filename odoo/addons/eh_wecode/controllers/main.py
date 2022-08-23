from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from requests import post


class LobbyRequestController(http.Controller):
    @http.route('/ipm_request_webform', type="http", auth="public", website=True)
    def ipm_webform(self, **kw):
        doctor_rec = request.env['ipm.study.request'].sudo().search([])
        print("doctor_rec...", doctor_rec)
        return http.request.render('eh_wecode.ipm_create_request')

    @http.route('/farm_registration_webform', type="http", auth="public", website=True)
    def farm_webform(self, **kw):
        doctor_rec = request.env['lobby.request_last'].sudo().search([])
        print("doctor_rec...", doctor_rec)
        return http.request.render('eh_wecode.create_farm_registration_form')

    @http.route('/exhibitor_registration_webform', type="http", auth="public", website=True)
    def exhibitor_webform(self, **kw):
        doctor_rec = request.env['registration.exhibitor'].sudo().search([])
        print("doctor_rec...", doctor_rec)
        return http.request.render('eh_wecode.create_registration_exhibitor')

    @http.route('/monitoring_tracking_webform', type="http", auth="public", website=True)
    def monitoring_webform(self, **kw):
        doctor_rec = request.env['monitoring.tracking.tool'].sudo().search([])
        print("doctor_rec...", doctor_rec)
        return http.request.render('eh_wecode.create_monitoring_tracking')

    @http.route('/training_booking_webform', type="http", auth="public", website=True)
    def monitoring_webform(self, **kw):
        doctor_rec = request.env['training.department.book'].sudo().search([])
        return http.request.render('eh_wecode.training_booking')

    @http.route('/buyer_interest', type="http", auth="public", website=True)
    def buyer_webform(self, **kw):
        doctor_rec = request.env['buyer.interest'].sudo().search([])
        return http.request.render('eh_wecode.create_buyer_interest')
    # @http.route('/create/weblobbyrequest', type="http", auth="public", website=True)
    # def create_lobbyrequest(self, **kw):
    #     print("Data Received.....", kw)
    #     request.env['ipm.study.request'].sudo().create({
    #         'requested_by':  post['requested_by'],
    #         'camp_email': post['camp_email'],
    #         'partner_id': post['partner_id'],
    #         'requested_support': post['requested_support'], })
    #     return request.render("eh_wecode.lobby_thanks", {})
