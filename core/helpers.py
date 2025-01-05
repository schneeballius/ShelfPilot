from django.db import transaction,connection
from django.utils.timezone import now
from random import randint
from django.http import JsonResponse

from django.shortcuts import render, redirect
from django.apps import apps
from .models import *
from .storageLogic import *
from .strategySimulation import *

def deleteDummy():
    for model in apps.get_models():
        model.objects.all().delete()
        reset_auto_increment(model)

def reset_auto_increment(model):
    table_name = model._meta.db_table
    with connection.cursor() as cursor:
        # Für SQLite: Setze den Auto-Increment-Wert zurück
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")


def createDummy():
    try:
        if Category.objects.all().exists():
            deleteDummy()
        # Category
        category = Category.objects.create(name="Elektronik")
        category1 = Category.objects.create(name="Computertechnik")

        # Orders
        order = Order.objects.create(
            customer="Kolle",
            product=None,
            arrived_on=now(),
            served_on=None,
            type="Einlagerung",
            status="Offen"
        )
        order1 = Order.objects.create(
            customer="Intel",
            product=None,
            arrived_on=now(),
            served_on=None,
            type="Einlagerung",
            status="Offen"
        )
        order2 = Order.objects.create(
            customer="Nahkauf",
            product=None,
            arrived_on=now(),
            served_on=None,
            type="Auslagerung",
            status="Offen"
        )
        order3 = Order.objects.create(
            customer="Intel",
            product=None,
            arrived_on=now(),
            served_on=None,
            type="Auslagerung",
            status="Offen"
        )
        

        # Products
        product = Product.objects.create(
        #order=order,
        storage=None,  # Kann später zugewiesen werden
        category=category,
        weight=2,
        name="Rauchmelder",
        storing=False,
        stored_on=None
        )
        product1 = Product.objects.create(
        #order=order1,
        storage=None,  # Kann später zugewiesen werden
        category=category1,
        weight=1,
        name="Prozessor",
        storing=False,
        stored_on=None
        )
        product2 = Product.objects.create(
        #order=order2,
        storage=None,  # Kann später zugewiesen werden
        category=category,
        weight=5,
        name="Fernseher",
        storing=False,
        stored_on=None
        )
        
        order.product=product
        order.save()
        order1.product=product1
        order1.save()
        order2.product=product2
        order2.save()
        order3.product=product1
        order3.save()

        

        # Storage
        storage = Storage.objects.create(number=-100,x=-1,y=0)  # Lagerplatz mit ID "1" (oder "0", wenn mit 0 begonnen wird)
        for i in range(4, -1, -1):
            for j in range(10):
                storage1 = Storage.objects.create(number=10*i+j,x=j,y=i)

        storage2 = Storage.objects.create(number=100,x=10,y=0)

        # Strategy
        strategy = Strategy.objects.create(
            name="FIFO", 
            active=True
        )
        strategy1 = Strategy.objects.create(
            name="LIFO",
            active=False
        )

        # Stacker
        stacker = Stacker.objects.create(
            storage=storage,
            strategy=strategy,  # Strategy wird später verknüpft
            status="Bereit"
        )


        # Simulation

        # Tour

        # Parameter
        Parameter.objects.create(
            stacker=stacker,
            weight_control=True,
            weight_control_value=80,
            weight_control_from_story=3,
            vertical_speed=5,
            horizontal_speed=10,
            material_durability=100
        )

        print("Dummydaten erfolgreich erstellt!")
    except Exception as e:
        print(f"Fehler bei der Erstellung der Dummy-Daten: {e}")

def deleteDummyView(request):
    deleteDummy()
    return JsonResponse({
        'success': True,
        'message': 'Dummy wurde erfolgreich gelöscht',
        'redirect_url': '/einstellungen'  # falls du den Nutzer weiterleiten möchtest
    })

def createDummyView(request):
    createDummy()
    return JsonResponse({
        'success': True,
        'message': 'Dummy wurde erfolgreich erstellt',
        'redirect_url': '/einstellungen'  # falls du den Nutzer weiterleiten möchtest
    })

def removeProduct(request, product_id):

    product = Product.objects.get(id=product_id)

    order = Order.objects.create(
        customer="/  ",
        product=product,
        arrived_on=now(),
        type="Auslagerung",
        status="Offen"
    )

    orderId=order.id
    return serveOrder(request,orderId)

def addInOrder(request):
    customer=request.POST.get('order_customer')
    name=request.POST.get('product_name')
    weight=request.POST.get('product_weight')
    categoryId=request.POST.get('category')

    category=Category.objects.get(id=categoryId)

    order = Order.objects.create(
        customer=customer,
        product=None,
        arrived_on=now(),
        type="Einlagerung",
        status="Offen"
    )

    product = Product.objects.create(
    storage=None,  # Kann später zugewiesen werden
    category=category,
    weight=weight,
    name=name,
    storing=False,
    stored_on=None
    )
    
    order.product=product
    order.save()

    from .views import overview
    return overview(request)

def addOutOrder(request):
    customer=request.POST.get('out_order_customer')
    productId=request.POST.get('product')
    
    product = Product.objects.get(id=productId)

    order = Order.objects.create(
        customer=customer,
        product=product,
        arrived_on=now(),
        type="Auslagerung",
        status="Offen"
    )
    
    from .views import overview
    return overview(request)

def serveOrder(request, order_id):

    order=Order.objects.get(id=order_id)
    
    match order.status:
        case "Offen":
            match order.type:
                case "Einlagerung":
                    product=order.product
                    if(store(product.id) == 1):
                        order.status="Geschlossen"
                        order.served_on=now()
                        order.save()

                case "Auslagerung":
                    product=order.product
                    if(discard(product.id) == 1):
                        order.status="Geschlossen"
                        order.served_on=now()
                        order.save()

    Order.SortOrders(force=True)
    from .views import overview
    return overview(request)

def deleteOrder(request, order_id):

    order=Order.objects.get(id=order_id)
    order.delete()

    from .views import overview
    return overview(request)