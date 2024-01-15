from flask import Blueprint,Flask, render_template, request, redirect, url_for, flash, session, Blueprint
import json, os, datetime
adminHomeBP = Blueprint("admin", __name__)

@adminHomeBP.route('/admin/dashboard')
def home():
    return render_template('admin/home.html')
@adminHomeBP.route('/user_management')
def user_management():
    return render_template('admin/user_management.html')
@adminHomeBP.route('/admin/report')
def report():
    with open('reports/reportsInfo.json', 'r') as file:
        data = json.load(file)
    return render_template('admin/report.html', data=data, date = datetime.datetime.now().strftime("%d %B %I:%M %p"))
@adminHomeBP.route('/system_health')
def system_health():
    return render_template('admin/system_health.html')
@adminHomeBP.route('/reply')
def reply():
    return render_template('admin/reply.html')