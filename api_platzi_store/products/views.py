import requests
from django.shortcuts import render, redirect
from .forms import ProductForm

base_url = "https://api.escuelajs.co/api/v1/"

def product_list(request):
    try:
        response = requests.get(f"{base_url}products/", timeout=20)
        response.raise_for_status()
        productos = response.json()
    except requests.RequestException:
        productos = []

    categorias = sorted({
        p['category']['name']
        for p in productos
    })

    selected = request.GET.get('category', 'All')
    if selected != 'All':
        productos = [
            p for p in productos
            if p['category']['name'] == selected
        ]

    context = {
        'productos': productos,
        'categorias': ['All'] + categorias,
        'selected': selected,
    }
    return render(request, 'products/product_list.html', context)


def product_create(request):
    try:
        resp_cat = requests.get(f'{base_url}categories/', timeout=10)
        resp_cat.raise_for_status()
        cats_json = resp_cat.json()
        categories = [(c['id'], c['name']) for c in cats_json]
    except requests.RequestException:
        categories = []

    if request.method == 'POST':
        form = ProductForm(request.POST, categories=categories)
        if form.is_valid():
            payload = {
                "title":       form.cleaned_data['title'],
                "price":       float(form.cleaned_data['price']),
                "description": form.cleaned_data['description'],
                "categoryId":  int(form.cleaned_data['category']),
                "images":      [form.cleaned_data['image']],
            }
            try:
                resp_post = requests.post(
                    f'{base_url}products/',
                    json=payload,
                    timeout=10
                )
                resp_post.raise_for_status()
                return redirect('products:product_list')
            except requests.RequestException:
                form.add_error(None, 'Error al crear el producto en la API')
    else:
        form = ProductForm(categories=categories)

    return render(request, 'products/product_create.html', {
        'form': form
    })


def product_update(request, product_id):
    try:
        resp = requests.get(f'{base_url}products/{product_id}', timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        return redirect('products:product_list')

    try:
        resp_cat = requests.get(f'{base_url}categories/', timeout=5)
        resp_cat.raise_for_status()
        cats_json = resp_cat.json()
        categories = [(c['id'], c['name']) for c in cats_json]
    except requests.RequestException:
        categories = []

    if request.method == 'POST':
        form = ProductForm(request.POST, categories=categories)
        if form.is_valid():
            payload = {
                "title":       form.cleaned_data['title'],
                "price":       float(form.cleaned_data['price']),
                "description": form.cleaned_data['description'],
                "categoryId":  int(form.cleaned_data['category']),
                "images":      [form.cleaned_data['image']],
            }
            try:
                resp_put = requests.put(
                    f'{base_url}products/{product_id}',
                    json=payload,
                    timeout=5
                )
                resp_put.raise_for_status()
                return redirect('products:product_list')
            except requests.RequestException:
                form.add_error(None, 'Error al actualizar el producto.')
    else:
        initial = {
            'title':       data.get('title'),
            'price':       data.get('price'),
            'description': data.get('description'),
            'category':    data.get('category', {}).get('id'),
            'image':       data.get('images', [''])[0],
        }
        form = ProductForm(initial=initial, categories=categories)

    return render(request, 'products/product_update.html', {
        'form': form,
        'product_id': product_id
    })

def home(request):
    return render(request, 'products/home.html')
def product_delete(request, product_id):
    if request.method == 'POST':
        try:
            resp = requests.delete(
                f'{base_url}products/{product_id}',
                timeout=5
            )
            resp.raise_for_status()
        except requests.RequestException:
            pass

    return redirect('products:product_list')

def product_list(request):
    try:
        response = requests.get(f"{base_url}products/", timeout=20)
        response.raise_for_status()
        productos = response.json()
    except requests.RequestException:
        productos = []

    categorias = sorted({
        p['category']['name']
        for p in productos
    })

    selected = request.GET.get('category', 'All')
    if selected != 'All':
        productos = [
            p for p in productos
            if p['category']['name'] == selected
        ]

    query = request.GET.get('q', '').strip().lower()
    if query:
        productos = [
            p for p in productos
            if query in str(p['id']).lower()
            or query in p['title'].lower()
            or query in p['category']['name'].lower()
        ]

    context = {
        'productos': productos,
        'categorias': ['All'] + categorias,
        'selected': selected,
    }
    return render(request, 'products/product_list.html', context)
