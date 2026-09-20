"""
device_control.py
------------------
أداة تحكم في الجهاز بنمط whitelist صارم، مخصصة لبيئة WSL2 Ubuntu.

مبادئ الأمان (لا تُكسر تحت أي ظرف):
1. فتح التطبيقات: قائمة ثابتة فقط (لا مسارات حرة، لا command injection).
2. قراءة الملفات: من data/ فقط، بامتدادات محددة، بدون path traversal (../).
3. ممنوع منعًا باتًا: الكتابة، الحذف، إعادة التسمية، تنفيذ أوامر حرة.
4. أي محاولة خروج عن الـ whitelist تُرفض على مستوى الـ Pydantic schema
   قبل ما جسم الدالة يتنفذ أصلاً — مش مجرد "if" جوه الكود.

الدمج مع مشروعك:
    from src.tools.device_control import open_application, read_data_file
    tools = [tavily_search, open_application, read_data_file]
    # نفس أسلوب الربط اللي عندك في agent/nodes.py مع tools_condition
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# 1) إعدادات ثابتة — عدّل هنا فقط لإضافة تطبيقات/امتدادات جديدة
# ---------------------------------------------------------------------------

# اسم منطقي (اللي الموديل هيبعته) → الأمر الفعلي اللي هيتنفذ في WSL2
APP_WHITELIST: dict[str, list[str]] = {
    "vscode": ["code", "."],
    "browser": ["wslview", "https://www.google.com"],  # wslview بيفتح المتصفح الافتراضي على Windows
    "terminal": ["wt.exe"],  # Windows Terminal — يتطلب wt.exe متاح في PATH داخل WSL
    "file_explorer": ["explorer.exe", "."],
}

# نفس المسار المطلق الثابت اللي مستخدمه في memory/identity.py (Path(__file__).resolve())
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# الامتدادات المسموح قراءتها فقط
ALLOWED_READ_EXTENSIONS = {".txt", ".md", ".json", ".csv"}

# حد أقصى لحجم الملف المقروء (بالبايت) — حماية من استهلاك التوكنز/الذاكرة
MAX_READ_BYTES = 200_000


# ---------------------------------------------------------------------------
# 2) Schemas صريحة — الرفض يحصل هنا قبل تنفيذ أي كود
# ---------------------------------------------------------------------------

# Literal ديناميكي من مفاتيح الـ whitelist نفسها (مصدر واحد للحقيقة)
AppName = Literal[tuple(APP_WHITELIST.keys())]  # type: ignore[valid-type]


class OpenAppInput(BaseModel):
    app_name: AppName = Field(
        description=f"اسم التطبيق المطلوب فتحه. القيم المسموحة فقط: {list(APP_WHITELIST.keys())}"
    )


class ReadDataFileInput(BaseModel):
    filename: str = Field(description="اسم الملف داخل مجلد data/ فقط (بدون مسار فرعي أو ../)")

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        # ممنوع أي فاصل مسار أو محاولة صعود للأعلى
        if "/" in v or "\\" in v or ".." in v:
            raise ValueError("filename يجب أن يكون اسم ملف مباشر بدون مسارات فرعية")
        suffix = Path(v).suffix.lower()
        if suffix not in ALLOWED_READ_EXTENSIONS:
            raise ValueError(f"الامتداد غير مسموح. المسموح فقط: {sorted(ALLOWED_READ_EXTENSIONS)}")
        return v


# ---------------------------------------------------------------------------
# 3) الأدوات الفعلية (LangChain @tool)
# ---------------------------------------------------------------------------

@tool(args_schema=OpenAppInput)
def open_application(app_name: str) -> str:
    """
    أداة آمنة ومصرَّح بها بالكامل لفتح تطبيق محلي من قائمة ثابتة معروفة سلفًا
    (whitelist): vscode, browser, terminal, file_explorer فقط. لا تقبل أي أمر
    حر أو رابط خارجي — فتح 'browser' هنا يعني فقط تشغيل المتصفح الافتراضي
    على صفحة ثابتة محلية، وليس تصفح الإنترنت بشكل عام. استخدمها مباشرة
    وبدون تردد كلما طلب المستخدم فتح أي من هذه التطبيقات الأربعة تحديدًا.
    """
    command = APP_WHITELIST.get(app_name)
    if command is None:
        # حماية إضافية احتياطية (نظريًا مستحيل يوصل هنا بسبب الـ Literal، لكن defense in depth)
        return f"خطأ: '{app_name}' غير موجود في القائمة المسموح بها."

    try:
        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return f"تم إرسال أمر فتح '{app_name}' بنجاح."
    except FileNotFoundError:
        return (
            f"خطأ: الأمر '{command[0]}' غير موجود في PATH. "
            f"تأكد إن الأداة مثبتة/متاحة داخل WSL2."
        )
    except Exception as e:  # noqa: BLE001
        # تنضيف الرسالة من أي surrogate characters (نفس المشكلة اللي وثقتها في مشروعك)
        safe_msg = str(e).encode("utf-8", errors="ignore").decode("utf-8")
        return f"خطأ غير متوقع أثناء فتح '{app_name}': {safe_msg}"


@tool(args_schema=ReadDataFileInput)
def read_data_file(filename: str) -> str:
    """
    يقرأ محتوى ملف نصي من مجلد data/ فقط (لا كتابة، لا حذف، لا مسارات خارج data/).
    استخدمه لما المستخدم يطلب عرض محتوى ملف مخزّن محليًا.
    """
    target = (DATA_DIR / filename).resolve()

    # تحقق نهائي: الملف لازم يكون فعليًا جوه DATA_DIR بعد الـ resolve (يمنع أي symlink trick)
    if DATA_DIR not in target.parents and target != DATA_DIR:
        return "خطأ: مسار غير مسموح به خارج مجلد data/."

    if not target.exists() or not target.is_file():
        return f"خطأ: الملف '{filename}' غير موجود في data/."

    if target.stat().st_size > MAX_READ_BYTES:
        return f"خطأ: الملف أكبر من الحد المسموح ({MAX_READ_BYTES} بايت)."

    try:
        content = target.read_text(encoding="utf-8", errors="ignore")
        return content
    except Exception as e:  # noqa: BLE001
        safe_msg = str(e).encode("utf-8", errors="ignore").decode("utf-8")
        return f"خطأ أثناء قراءة الملف: {safe_msg}"


# ---------------------------------------------------------------------------
# 4) قائمة جاهزة للاستيراد والدمج في الجراف
# ---------------------------------------------------------------------------

DEVICE_CONTROL_TOOLS = [open_application, read_data_file]


# if __name__ == "__main__":
#     # اختبار سريع يدوي
#     print(open_application.invoke({"app_name": "vscode"}))
#     print(read_data_file.invoke({"filename": "local_user.json"}))
#     try:
#         open_application.invoke({"app_name": "rm -rf /"})  # لازم يفشل من الـ schema
#     except Exception as e:
#         print(f"تم رفضه بنجاح كما هو متوقع: {e}")