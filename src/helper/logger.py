"""
logger.py
---------
إعداد مركزي واحد للـ logging لكل المشروع.
الهدف: أي ملف يستورد نفس الـ logger، فتتحكم في المستوى (level) من مكان واحد
بدل ما تلاقي print() متناثرة في كل مكان.

الاستخدام في أي ملف تاني:
    from helper.logger import logger
    logger.info("رسالة عادية")
    logger.warning("تحذير")
    logger.error("خطأ")
"""

import logging
import sys


def setup_logger(name: str = "ai_agent", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)

    # يمنع تكرار الـ handlers لو الملف اتعمله import أكتر من مرة
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # (اختياري) لو عايز تسجل في ملف كمان بجانب الشاشة، فك التعليق:
    # file_handler = logging.FileHandler("agent.log", encoding="utf-8")
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    return logger


# instance جاهزة تتستورد مباشرة في أي مكان في المشروع
logger = setup_logger(level=logging.DEBUG)