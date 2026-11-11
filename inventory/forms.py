from django import forms
from .models import Product, Category, Supplier, StockTransaction, Sale

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = ["name","sku","category","supplier","unit","purchase_price","selling_price","quantity","reorder_level","description","active"]

class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ["name","description"]

class SupplierForm(StyledModelForm):
    class Meta:
        model = Supplier
        fields = ["name","contact_person","email","phone","address"]

class StockTransactionForm(StyledModelForm):
    class Meta:
        model = StockTransaction
        fields = ["product","transaction_type","quantity","reference","notes"]

class SaleForm(StyledModelForm):
    class Meta:
        model = Sale
        fields = ["product","quantity","unit_price","reference"]
