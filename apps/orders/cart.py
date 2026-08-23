from apps.catalog.models import ProductVariant

SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.data = self.session.setdefault(SESSION_KEY, {})

    def add(self, variant_id, quantity):
        key = str(variant_id)
        self.data[key] = self.data.get(key, 0) + quantity
        self._save()

    def update(self, variant_id, quantity):
        key = str(variant_id)
        if quantity <= 0:
            self.data.pop(key, None)
        else:
            self.data[key] = quantity
        self._save()

    def remove(self, variant_id):
        self.data.pop(str(variant_id), None)
        self._save()

    def clear(self):
        self.data = {}
        self._save()

    def _save(self):
        self.session[SESSION_KEY] = self.data
        self.session.modified = True

    def lines(self):
        variant_ids = [int(vid) for vid in self.data]
        variants = ProductVariant.objects.select_related('product').filter(pk__in=variant_ids)
        variants_by_id = {v.pk: v for v in variants}

        result = []
        for vid, quantity in self.data.items():
            variant = variants_by_id.get(int(vid))
            if not variant:
                continue
            result.append({
                'variant': variant,
                'quantity': quantity,
                'subtotal': variant.price * quantity,
            })
        return result

    def total(self):
        return sum(line['subtotal'] for line in self.lines())

    def __len__(self):
        return sum(self.data.values())
