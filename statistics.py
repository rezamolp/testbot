#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سیستم آمارگیری حرفه‌ای ربات اتوفوروارد تلگرام
Professional Statistics System for Telegram Auto-Forward Bot
"""

import sqlite3
import json
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class MessageStats:
    """کلاس آمار پیام"""
    id: int
    message_type: str
    source_channel: str
    destination_channel: str
    timestamp: datetime
    forward_delay: float
    success: bool
    error_message: Optional[str] = None
    message_size: Optional[int] = None
    has_media: bool = False
    media_type: Optional[str] = None

@dataclass
class ChannelStats:
    """آمار کانال"""
    channel_id: str
    channel_name: str
    total_messages: int
    successful_forwards: int
    failed_forwards: int
    last_activity: datetime
    message_types: Dict[str, int]

class StatisticsDB:
    """پایگاه داده آمارگیری"""
    
    def __init__(self, db_path: str = "forward_stats.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """مقداردهی پایگاه داده"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS message_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    message_type TEXT NOT NULL,
                    source_channel TEXT NOT NULL,
                    destination_channel TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    forward_delay REAL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    message_size INTEGER,
                    has_media BOOLEAN DEFAULT FALSE,
                    media_type TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    total_messages INTEGER DEFAULT 0,
                    successful_forwards INTEGER DEFAULT 0,
                    failed_forwards INTEGER DEFAULT 0,
                    average_delay REAL DEFAULT 0,
                    message_types TEXT DEFAULT '{}'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS channel_stats (
                    channel_id TEXT PRIMARY KEY,
                    channel_name TEXT,
                    total_messages INTEGER DEFAULT 0,
                    successful_forwards INTEGER DEFAULT 0,
                    failed_forwards INTEGER DEFAULT 0,
                    last_activity TEXT,
                    message_types TEXT DEFAULT '{}'
                )
            """)
            
            # ایندکس‌ها برای بهبود عملکرد
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON message_stats(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source_channel ON message_stats(source_channel)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_success ON message_stats(success)")
    
    def add_message_stat(self, stat: MessageStats):
        """افزودن آمار پیام جدید"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO message_stats 
                (message_id, message_type, source_channel, destination_channel, 
                 timestamp, forward_delay, success, error_message, message_size, 
                 has_media, media_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stat.id, stat.message_type, stat.source_channel, 
                stat.destination_channel, stat.timestamp.isoformat(),
                stat.forward_delay, stat.success, stat.error_message,
                stat.message_size, stat.has_media, stat.media_type
            ))
            
            # به‌روزرسانی آمار روزانه
            self._update_daily_stats(stat)
            
            # به‌روزرسانی آمار کانال
            self._update_channel_stats(stat)
    
    def _update_daily_stats(self, stat: MessageStats):
        """به‌روزرسانی آمار روزانه"""
        date_str = stat.timestamp.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # دریافت آمار موجود
            cursor = conn.execute(
                "SELECT total_messages, successful_forwards, failed_forwards, message_types FROM daily_stats WHERE date = ?",
                (date_str,)
            )
            result = cursor.fetchone()
            
            if result:
                total, success, failed, types_json = result
                message_types = json.loads(types_json) if types_json else {}
            else:
                total, success, failed = 0, 0, 0
                message_types = {}
            
            # به‌روزرسانی
            total += 1
            if stat.success:
                success += 1
            else:
                failed += 1
            
            message_types[stat.message_type] = message_types.get(stat.message_type, 0) + 1
            
            # محاسبه میانگین تاخیر
            avg_delay = self._calculate_average_delay(date_str)
            
            conn.execute("""
                INSERT OR REPLACE INTO daily_stats 
                (date, total_messages, successful_forwards, failed_forwards, average_delay, message_types)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, total, success, failed, avg_delay, json.dumps(message_types)))
    
    def _update_channel_stats(self, stat: MessageStats):
        """به‌روزرسانی آمار کانال"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT total_messages, successful_forwards, failed_forwards, message_types FROM channel_stats WHERE channel_id = ?",
                (stat.source_channel,)
            )
            result = cursor.fetchone()
            
            if result:
                total, success, failed, types_json = result
                message_types = json.loads(types_json) if types_json else {}
            else:
                total, success, failed = 0, 0, 0
                message_types = {}
            
            total += 1
            if stat.success:
                success += 1
            else:
                failed += 1
            
            message_types[stat.message_type] = message_types.get(stat.message_type, 0) + 1
            
            conn.execute("""
                INSERT OR REPLACE INTO channel_stats 
                (channel_id, total_messages, successful_forwards, failed_forwards, last_activity, message_types)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                stat.source_channel, total, success, failed, 
                stat.timestamp.isoformat(), json.dumps(message_types)
            ))
    
    def _calculate_average_delay(self, date_str: str) -> float:
        """محاسبه میانگین تاخیر برای یک روز"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT AVG(forward_delay) FROM message_stats WHERE date(timestamp) = ? AND success = 1",
                (date_str,)
            )
            result = cursor.fetchone()
            return result[0] if result[0] else 0.0
    
    def get_daily_stats(self, days: int = 30) -> List[Dict]:
        """دریافت آمار روزانه"""
        start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM daily_stats 
                WHERE date >= ? 
                ORDER BY date DESC
            """, (start_date,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_channel_stats(self) -> List[Dict]:
        """دریافت آمار کانال‌ها"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM channel_stats ORDER BY total_messages DESC")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_message_type_stats(self, days: int = 30) -> Dict[str, int]:
        """آمار انواع پیام"""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT message_type, COUNT(*) 
                FROM message_stats 
                WHERE timestamp >= ? 
                GROUP BY message_type
            """, (start_date.isoformat(),))
            
            return dict(cursor.fetchall())
    
    def get_error_stats(self, days: int = 30) -> List[Dict]:
        """آمار خطاها"""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT error_message, COUNT(*) as count, MAX(timestamp) as last_occurrence
                FROM message_stats 
                WHERE timestamp >= ? AND success = 0 AND error_message IS NOT NULL
                GROUP BY error_message
                ORDER BY count DESC
            """, (start_date.isoformat(),))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

class StatisticsAnalyzer:
    """تحلیلگر آمار"""
    
    def __init__(self, db: StatisticsDB):
        self.db = db
    
    def get_performance_metrics(self, days: int = 30) -> Dict:
        """محاسبه معیارهای عملکرد"""
        daily_stats = self.db.get_daily_stats(days)
        
        if not daily_stats:
            return {}
        
        total_messages = sum(stat['total_messages'] for stat in daily_stats)
        successful_forwards = sum(stat['successful_forwards'] for stat in daily_stats)
        failed_forwards = sum(stat['failed_forwards'] for stat in daily_stats)
        
        success_rate = (successful_forwards / total_messages * 100) if total_messages > 0 else 0
        
        # میانگین پیام در روز
        avg_messages_per_day = total_messages / len(daily_stats) if daily_stats else 0
        
        # محاسبه روند
        if len(daily_stats) >= 2:
            recent_avg = sum(stat['total_messages'] for stat in daily_stats[:7]) / 7
            old_avg = sum(stat['total_messages'] for stat in daily_stats[-7:]) / 7
            trend = ((recent_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0
        else:
            trend = 0
        
        return {
            'total_messages': total_messages,
            'successful_forwards': successful_forwards,
            'failed_forwards': failed_forwards,
            'success_rate': round(success_rate, 2),
            'avg_messages_per_day': round(avg_messages_per_day, 2),
            'trend_percentage': round(trend, 2),
            'period_days': days
        }
    
    def get_peak_hours(self, days: int = 30) -> Dict:
        """تحلیل ساعات پیک"""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                FROM message_stats 
                WHERE timestamp >= ?
                GROUP BY hour
                ORDER BY count DESC
            """, (start_date.isoformat(),))
            
            hour_stats = dict(cursor.fetchall())
            
            # تبدیل کلیدها به int و پر کردن ساعات خالی
            full_hours = {}
            for hour in range(24):
                hour_str = f"{hour:02d}"
                full_hours[hour] = int(hour_stats.get(hour_str, 0))
            
            peak_hour = max(full_hours, key=full_hours.get) if full_hours else 0
            
            return {
                'hourly_distribution': full_hours,
                'peak_hour': peak_hour,
                'peak_hour_count': full_hours[peak_hour]
            }
    
    def get_weekly_pattern(self, days: int = 30) -> Dict:
        """تحلیل الگوی هفتگی"""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT strftime('%w', timestamp) as weekday, COUNT(*) as count
                FROM message_stats 
                WHERE timestamp >= ?
                GROUP BY weekday
            """, (start_date.isoformat(),))
            
            weekday_stats = dict(cursor.fetchall())
            
            # نام روزهای هفته
            weekday_names = {
                '0': 'یکشنبه', '1': 'دوشنبه', '2': 'سه‌شنبه', 
                '3': 'چهارشنبه', '4': 'پنج‌شنبه', '5': 'جمعه', '6': 'شنبه'
            }
            
            weekly_pattern = {}
            for day_num, day_name in weekday_names.items():
                weekly_pattern[day_name] = int(weekday_stats.get(day_num, 0))
            
            busiest_day = max(weekly_pattern, key=weekly_pattern.get) if weekly_pattern else 'نامشخص'
            
            return {
                'weekly_distribution': weekly_pattern,
                'busiest_day': busiest_day,
                'busiest_day_count': weekly_pattern.get(busiest_day, 0)
            }

class StatisticsReporter:
    """گزارش‌ساز آمار"""
    
    def __init__(self, db: StatisticsDB, analyzer: StatisticsAnalyzer):
        self.db = db
        self.analyzer = analyzer
    
    def generate_daily_report(self) -> str:
        """تولید گزارش روزانه"""
        today = datetime.now().date().isoformat()
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM daily_stats WHERE date = ?", (today,)
            )
            today_stats = cursor.fetchone()
        
        if not today_stats:
            return "📊 گزارش روزانه\n\n❌ هیچ فعالیتی امروز ثبت نشده است."
        
        total, success, failed = today_stats[1], today_stats[2], today_stats[3]
        success_rate = (success / total * 100) if total > 0 else 0
        
        report = f"""📊 گزارش روزانه - {today}
═══════════════════════════════════

📈 آمار کلی:
• کل پیام‌ها: {total:,}
• فوروارد موفق: {success:,}
• فوروارد ناموفق: {failed:,}
• نرخ موفقیت: {success_rate:.1f}%

"""
        
        # آمار انواع پیام
        message_types = json.loads(today_stats[5]) if today_stats[5] else {}
        if message_types:
            report += "📱 انواع پیام:\n"
            for msg_type, count in sorted(message_types.items(), key=lambda x: x[1], reverse=True):
                report += f"• {msg_type}: {count:,}\n"
        
        return report
    
    def generate_weekly_report(self) -> str:
        """تولید گزارش هفتگی"""
        metrics = self.analyzer.get_performance_metrics(7)
        weekly_pattern = self.analyzer.get_weekly_pattern(7)
        peak_hours = self.analyzer.get_peak_hours(7)
        
        report = f"""📊 گزارش هفتگی
═══════════════════════════════════

📈 عملکرد کلی:
• کل پیام‌ها: {metrics.get('total_messages', 0):,}
• نرخ موفقیت: {metrics.get('success_rate', 0)}%
• میانگین روزانه: {metrics.get('avg_messages_per_day', 0):.1f}

🕐 ساعت پیک: {peak_hours.get('peak_hour', 'نامشخص')}:00
📅 روز پرترافیک: {weekly_pattern.get('busiest_day', 'نامشخص')}

📱 الگوی هفتگی:
"""
        
        for day, count in weekly_pattern.get('weekly_distribution', {}).items():
            report += f"• {day}: {count:,}\n"
        
        return report
    
    def generate_monthly_report(self) -> str:
        """تولید گزارش ماهانه"""
        metrics = self.analyzer.get_performance_metrics(30)
        error_stats = self.db.get_error_stats(30)
        message_types = self.db.get_message_type_stats(30)
        
        report = f"""📊 گزارش ماهانه
═══════════════════════════════════

📈 عملکرد کلی:
• کل پیام‌ها: {metrics.get('total_messages', 0):,}
• پیام‌های موفق: {metrics.get('successful_forwards', 0):,}
• پیام‌های ناموفق: {metrics.get('failed_forwards', 0):,}
• نرخ موفقیت: {metrics.get('success_rate', 0)}%
• میانگین روزانه: {metrics.get('avg_messages_per_day', 0):.1f}
• روند: {metrics.get('trend_percentage', 0):+.1f}%

📱 انواع پیام:
"""
        
        for msg_type, count in sorted(message_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / metrics.get('total_messages', 1) * 100)
            report += f"• {msg_type}: {count:,} ({percentage:.1f}%)\n"
        
        if error_stats:
            report += "\n❌ خطاهای رایج:\n"
            for error in error_stats[:5]:  # تنها 5 خطای اول
                report += f"• {error['error_message']}: {error['count']} بار\n"
        
        return report