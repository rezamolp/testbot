#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
داشبورد وب برای نمایش آمارگیری ربات
Web Dashboard for Bot Statistics
"""

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime, timedelta
from statistics import StatisticsDB, StatisticsAnalyzer, StatisticsReporter
import os

app = Flask(__name__)
app.secret_key = 'telegram_forward_bot_secret_key'

# مقداردهی سیستم آمار
stats_db = StatisticsDB()
stats_analyzer = StatisticsAnalyzer(stats_db)
stats_reporter = StatisticsReporter(stats_db, stats_analyzer)

@app.route('/')
def dashboard():
    """صفحه اصلی داشبورد"""
    return render_template('dashboard.html')

@app.route('/api/overview')
def api_overview():
    """API برای دریافت آمار کلی"""
    try:
        metrics_30 = stats_analyzer.get_performance_metrics(30)
        metrics_7 = stats_analyzer.get_performance_metrics(7)
        metrics_1 = stats_analyzer.get_performance_metrics(1)
        
        return jsonify({
            'success': True,
            'data': {
                'monthly': metrics_30,
                'weekly': metrics_7,
                'daily': metrics_1
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/daily-stats')
def api_daily_stats():
    """API برای دریافت آمار روزانه"""
    try:
        days = request.args.get('days', 30, type=int)
        daily_stats = stats_db.get_daily_stats(days)
        
        # تبدیل به فرمت مناسب برای چارت
        dates = []
        total_messages = []
        success_rates = []
        
        for stat in reversed(daily_stats):  # معکوس کردن برای نمایش صحیح
            dates.append(stat['date'])
            total_messages.append(stat['total_messages'])
            
            if stat['total_messages'] > 0:
                success_rate = (stat['successful_forwards'] / stat['total_messages']) * 100
            else:
                success_rate = 0
            success_rates.append(round(success_rate, 1))
        
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'total_messages': total_messages,
                'success_rates': success_rates
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/message-types')
def api_message_types():
    """API برای دریافت آمار انواع پیام"""
    try:
        days = request.args.get('days', 30, type=int)
        message_types = stats_db.get_message_type_stats(days)
        
        return jsonify({
            'success': True,
            'data': {
                'labels': list(message_types.keys()),
                'values': list(message_types.values())
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/peak-hours')
def api_peak_hours():
    """API برای دریافت آمار ساعات پیک"""
    try:
        days = request.args.get('days', 30, type=int)
        peak_data = stats_analyzer.get_peak_hours(days)
        
        hours = list(range(24))
        counts = [peak_data['hourly_distribution'].get(hour, 0) for hour in hours]
        
        return jsonify({
            'success': True,
            'data': {
                'hours': hours,
                'counts': counts,
                'peak_hour': peak_data['peak_hour']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/weekly-pattern')
def api_weekly_pattern():
    """API برای دریافت الگوی هفتگی"""
    try:
        days = request.args.get('days', 30, type=int)
        weekly_data = stats_analyzer.get_weekly_pattern(days)
        
        return jsonify({
            'success': True,
            'data': {
                'distribution': weekly_data['weekly_distribution'],
                'busiest_day': weekly_data['busiest_day']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/channel-stats')
def api_channel_stats():
    """API برای دریافت آمار کانال‌ها"""
    try:
        channel_stats = stats_db.get_channel_stats()
        
        return jsonify({
            'success': True,
            'data': channel_stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/error-stats')
def api_error_stats():
    """API برای دریافت آمار خطاها"""
    try:
        days = request.args.get('days', 30, type=int)
        error_stats = stats_db.get_error_stats(days)
        
        return jsonify({
            'success': True,
            'data': error_stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reports/<report_type>')
def api_reports(report_type):
    """API برای دریافت گزارشات"""
    try:
        if report_type == 'daily':
            report = stats_reporter.generate_daily_report()
        elif report_type == 'weekly':
            report = stats_reporter.generate_weekly_report()
        elif report_type == 'monthly':
            report = stats_reporter.generate_monthly_report()
        else:
            return jsonify({'success': False, 'error': 'نوع گزارش نامعتبر'})
        
        return jsonify({
            'success': True,
            'data': {
                'report': report,
                'type': report_type,
                'generated_at': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export/<format>')
def api_export(format):
    """API برای export کردن داده‌ها"""
    try:
        days = request.args.get('days', 30, type=int)
        
        if format == 'json':
            data = {
                'overview': stats_analyzer.get_performance_metrics(days),
                'daily_stats': stats_db.get_daily_stats(days),
                'message_types': stats_db.get_message_type_stats(days),
                'error_stats': stats_db.get_error_stats(days),
                'export_date': datetime.now().isoformat(),
                'period_days': days
            }
            
            response = jsonify(data)
            response.headers['Content-Disposition'] = f'attachment; filename=telegram_bot_stats_{datetime.now().strftime("%Y%m%d")}.json'
            return response
            
        elif format == 'csv':
            # TODO: پیاده‌سازی export CSV
            return jsonify({'success': False, 'error': 'فرمت CSV هنوز پیاده‌سازی نشده'})
        
        else:
            return jsonify({'success': False, 'error': 'فرمت نامعتبر'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # ایجاد پوشه templates اگر وجود ندارد
    os.makedirs('templates', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)