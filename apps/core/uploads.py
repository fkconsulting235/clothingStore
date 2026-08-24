import os
import uuid


def _safe_name(subdir, filename):
    from django.utils import timezone

    ext = os.path.splitext(filename)[1].lower()
    name = uuid.uuid4().hex
    date_path = timezone.now().strftime('%Y/%m')
    return f'{subdir}/{date_path}/{name}{ext}'


def product_image_upload_to(instance, filename):
    return _safe_name('products', filename)


def payment_proof_upload_to(instance, filename):
    return _safe_name('comprobantes', filename)
