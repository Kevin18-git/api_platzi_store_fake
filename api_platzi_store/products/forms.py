from django import forms

class ProductForm(forms.Form):
    title       = forms.CharField(max_length=255, label='Título')
    price       = forms.DecimalField(max_digits=10, decimal_places=2, label='Precio')
    description = forms.CharField(widget=forms.Textarea, label='Descripción')
    category    = forms.ChoiceField(label='Categoría')
    image       = forms.URLField(label='URL de la imagen')

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)

        if categories:
            self.fields['category'].choices = categories

        # 🔥 Aquí añado la clase form-control a todos los campos automáticamente
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'
