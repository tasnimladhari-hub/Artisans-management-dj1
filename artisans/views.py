from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
import json
from .models import Artisan, Material, Sale
from .forms import ArtisanForm, MaterialForm, SaleForm, RegisterForm

def home(request):
    if request.user.is_authenticated:
        # Basic statistics
        artisans = Artisan.objects.filter(is_active=True)
        total_artisans = artisans.count()
        total_materials = Material.objects.count()
        
        # Total sales calculation
        all_sales = Sale.objects.all()
        total_sales_amount = sum(s.total_price for s in all_sales)
        
        # Top artisans with calculations
        top_artisans = []
        for artisan in artisans[:5]:
            sales = artisan.sales.all()
            materials = artisan.materials.all()
            total_sales = sum(s.total_price for s in sales)
            total_material_cost = sum(m.quantity * m.cost_per_unit for m in materials)
            profit = total_sales - total_material_cost
            top_artisans.append({
                'full_name': artisan.full_name,
                'specialty': artisan.specialty,
                'total_sales': total_sales,
                'profit': profit,
            })
        
        # Chart - last 6 months
        chart_labels = []
        chart_data = []
        today = datetime.now().date()
        for i in range(6, 0, -1):
            month = today - timedelta(days=30*i)
            month_name = month.strftime('%b')
            chart_labels.append(month_name)
            month_sales = sum(s.total_price for s in Sale.objects.filter(
                sale_date__year=month.year,
                sale_date__month=month.month
            ))
            chart_data.append(float(month_sales))
        
        context = {
            'total_artisans': total_artisans,
            'total_materials': total_materials,
            'total_sales': all_sales.count(),
            'total_sales_amount': total_sales_amount,
            'total_materials_value': sum(m.quantity * m.cost_per_unit for m in Material.objects.all()),
            'avg_profit_per_artisan': total_sales_amount / max(total_artisans, 1),
            'top_artisans': top_artisans,
            'recent_artisans': artisans.order_by('-join_date')[:6],
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
        }
    else:
        context = {}
    return render(request, 'artisans/home.html', context)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'artisans/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Hello {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'artisans/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def artisan_list(request):
    artisans_list = Artisan.objects.filter(is_active=True)
    search_query = request.GET.get('search', '')
    if search_query:
        artisans_list = artisans_list.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(specialty__icontains=search_query)
        )
    paginator = Paginator(artisans_list, 6)
    page_number = request.GET.get('page')
    artisans = paginator.get_page(page_number)
    return render(request, 'artisans/artisan_list.html', {
        'artisans': artisans,
        'search_query': search_query,
    })

@login_required
def artisan_detail(request, pk):
    artisan = get_object_or_404(Artisan, pk=pk)
    materials = artisan.materials.all()
    sales = artisan.sales.all()
    total_sales = sum(s.total_price for s in sales)
    total_materials = sum(m.quantity * m.cost_per_unit for m in materials)
    return render(request, 'artisans/artisan_detail.html', {
        'artisan': artisan,
        'materials': materials,
        'sales': sales,
        'total_sales': total_sales,
        'total_materials': total_materials,
        'profit': total_sales - total_materials,
    })

@login_required
def artisan_create(request):
    if request.method == 'POST':
        form = ArtisanForm(request.POST, request.FILES)
        if form.is_valid():
            artisan = form.save(commit=False)
            artisan.user = request.user
            artisan.save()
            messages.success(request, f'{artisan.full_name} has been added!')
            return redirect('artisan_detail', pk=artisan.pk)
    else:
        form = ArtisanForm()
    return render(request, 'artisans/artisan_form.html', {'form': form, 'title': 'Add Artisan'})

@login_required
def artisan_edit(request, pk):
    artisan = get_object_or_404(Artisan, pk=pk)
    if request.method == 'POST':
        form = ArtisanForm(request.POST, request.FILES, instance=artisan)
        if form.is_valid():
            form.save()
            messages.success(request, f'{artisan.full_name} has been updated!')
            return redirect('artisan_detail', pk=artisan.pk)
    else:
        form = ArtisanForm(instance=artisan)
    return render(request, 'artisans/artisan_form.html', {'form': form, 'title': 'Edit Artisan'})

@login_required
def artisan_delete(request, pk):
    artisan = get_object_or_404(Artisan, pk=pk)
    if request.method == 'POST':
        name = artisan.full_name
        artisan.delete()
        messages.success(request, f'{name} has been deleted.')
        return redirect('artisan_list')
    return render(request, 'artisans/artisan_confirm_delete.html', {'artisan': artisan})

@login_required
def material_create(request, artisan_pk):
    artisan = get_object_or_404(Artisan, pk=artisan_pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.artisan = artisan
            material.save()
            messages.success(request, 'Material added!')
            return redirect('artisan_detail', pk=artisan.pk)
    else:
        form = MaterialForm()
    return render(request, 'artisans/material_form.html', {'form': form, 'artisan': artisan})

@login_required
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    artisan = material.artisan
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted!')
        return redirect('artisan_detail', pk=artisan.pk)
    return render(request, 'artisans/material_confirm_delete.html', {'material': material, 'artisan': artisan})

@login_required
def sale_create(request, artisan_pk):
    artisan = get_object_or_404(Artisan, pk=artisan_pk)
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.artisan = artisan
            sale.save()
            messages.success(request, 'Sale recorded!')
            return redirect('artisan_detail', pk=artisan.pk)
    else:
        form = SaleForm()
    return render(request, 'artisans/sale_form.html', {'form': form, 'artisan': artisan})

@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    artisan = sale.artisan
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Sale deleted!')
        return redirect('artisan_detail', pk=artisan.pk)
    return render(request, 'artisans/sale_confirm_delete.html', {'sale': sale, 'artisan': artisan})