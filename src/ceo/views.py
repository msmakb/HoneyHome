from django.shortcuts import render
from main import constant
from accounting_manager.models import Sales
from warehouse_admin.models import GoodsMovement


def Dashboard(request):
    sales = Sales.objects.filter(is_approved=True).order_by('-id')[:5]
    goodsMovement = GoodsMovement.objects.all().order_by('-id')[:3]
    context = {'GoodsMovement': goodsMovement, 'Sales': sales}
    return render(request, constant.TEMPLATES.CEO_DASHBOARD_TEMPLATE, context)
