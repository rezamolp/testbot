#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات اتوفوروارد تلگرام
Telegram Auto-Forward Bot

این ربات پست‌های کانال مبدا را به صورت خودکار به کانال مقصد فوروارد می‌کند
"""

import asyncio
import logging
import os
from typing import Optional, Union
from telethon import TelegramClient, events
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv

# بارگذاری تنظیمات از فایل .env
load_dotenv()

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_forward.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramAutoForward:
    """کلاس اصلی ربات اتوفوروارد تلگرام"""
    
    def __init__(self):
        """مقداردهی اولیه ربات"""
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.phone = os.getenv('PHONE_NUMBER')
        self.source_channel = os.getenv('SOURCE_CHANNEL')
        self.destination_channel = os.getenv('DESTINATION_CHANNEL')
        self.forward_delay = int(os.getenv('FORWARD_DELAY', 5))
        
        # بررسی تنظیمات ضروری
        if not all([self.api_id, self.api_hash, self.phone, 
                   self.source_channel, self.destination_channel]):
            raise ValueError("لطفاً تمام تنظیمات ضروری را در فایل .env قرار دهید")
        
        # ایجاد کلاینت تلگرام
        self.client = TelegramClient('auto_forward_session', self.api_id, self.api_hash)
        
        logger.info("ربات اتوفوروارد مقداردهی شد")
        logger.info(f"کانال مبدا: {self.source_channel}")
        logger.info(f"کانال مقصد: {self.destination_channel}")

    async def start(self):
        """شروع ربات"""
        try:
            # اتصال به تلگرام
            await self.client.start(phone=self.phone)
            logger.info("اتصال به تلگرام برقرار شد")
            
            # بررسی دسترسی به کانال‌ها
            await self._check_channels()
            
            # ثبت event handler برای پیام‌های جدید
            @self.client.on(events.NewMessage(chats=self.source_channel))
            async def new_message_handler(event):
                await self._handle_new_message(event)
            
            logger.info("ربات شروع به کار کرد - منتظر پیام‌های جدید...")
            logger.info("برای خروج Ctrl+C را فشار دهید")
            
            # نگه‌داشتن ربات در حالت اجرا
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.info("ربات توسط کاربر متوقف شد")
        except Exception as e:
            logger.error(f"خطا در اجرای ربات: {e}")
        finally:
            await self.client.disconnect()

    async def _check_channels(self):
        """بررسی دسترسی به کانال‌های مبدا و مقصد"""
        try:
            # بررسی کانال مبدا
            source_entity = await self.client.get_entity(self.source_channel)
            logger.info(f"دسترسی به کانال مبدا تایید شد: {source_entity.title}")
            
            # بررسی کانال مقصد
            dest_entity = await self.client.get_entity(self.destination_channel)
            logger.info(f"دسترسی به کانال مقصد تایید شد: {dest_entity.title}")
            
        except Exception as e:
            logger.error(f"خطا در دسترسی به کانال‌ها: {e}")
            raise

    async def _handle_new_message(self, event):
        """پردازش پیام جدید و فوروارد آن"""
        try:
            message = event.message
            
            logger.info(f"پیام جدید دریافت شد از {self.source_channel}")
            logger.info(f"نوع پیام: {self._get_message_type(message)}")
            
            # تاخیر قبل از فوروارد (برای جلوگیری از spam detection)
            if self.forward_delay > 0:
                await asyncio.sleep(self.forward_delay)
            
            # فوروارد پیام
            await self._forward_message(message)
            
        except Exception as e:
            logger.error(f"خطا در پردازش پیام: {e}")

    async def _forward_message(self, message: Message):
        """فوروارد پیام به کانال مقصد"""
        try:
            # فوروارد پیام
            forwarded = await self.client.forward_messages(
                entity=self.destination_channel,
                messages=message
            )
            
            logger.info(f"پیام با موفقیت فوروارد شد به {self.destination_channel}")
            
            # اطلاعات اضافی برای لاگ
            if message.text:
                text_preview = message.text[:50] + "..." if len(message.text) > 50 else message.text
                logger.info(f"متن پیام: {text_preview}")
            
        except Exception as e:
            logger.error(f"خطا در فوروارد پیام: {e}")

    def _get_message_type(self, message: Message) -> str:
        """تشخیص نوع پیام"""
        if message.photo:
            return "عکس"
        elif message.video:
            return "ویدیو"
        elif message.document:
            return "فایل"
        elif message.audio:
            return "صوت"
        elif message.voice:
            return "پیام صوتی"
        elif message.sticker:
            return "استیکر"
        elif message.text:
            return "متن"
        else:
            return "نامشخص"

    async def get_channel_info(self, channel_username: str):
        """دریافت اطلاعات کانال"""
        try:
            entity = await self.client.get_entity(channel_username)
            return {
                'id': entity.id,
                'title': entity.title,
                'username': getattr(entity, 'username', None),
                'participants_count': getattr(entity, 'participants_count', 'نامشخص')
            }
        except Exception as e:
            logger.error(f"خطا در دریافت اطلاعات کانال {channel_username}: {e}")
            return None

    async def test_forward(self):
        """تست فوروارد با آخرین پیام کانال مبدا"""
        try:
            logger.info("شروع تست فوروارد...")
            
            # دریافت آخرین پیام از کانال مبدا
            async for message in self.client.iter_messages(self.source_channel, limit=1):
                logger.info(f"تست فوروارد آخرین پیام: {self._get_message_type(message)}")
                await self._forward_message(message)
                break
            
            logger.info("تست فوروارد کامل شد")
            
        except Exception as e:
            logger.error(f"خطا در تست فوروارد: {e}")


async def main():
    """تابع اصلی"""
    try:
        # ایجاد نمونه ربات
        bot = TelegramAutoForward()
        
        # شروع ربات
        await bot.start()
        
    except Exception as e:
        logger.error(f"خطای کلی: {e}")

if __name__ == "__main__":
    # اجرای ربات
    print("🤖 ربات اتوفوروارد تلگرام")
    print("=" * 40)
    asyncio.run(main())