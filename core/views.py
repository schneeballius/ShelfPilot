from django.shortcuts import render, redirect
from datetime import date
from .helpers import *
from .strategySimulation import *
from .models import *

# Dashboard
def dashboard(request):
    Order.SortOrders()
    openOrders = Order.objects.filter(status="Offen").order_by("priority")

    openOrdersIn = Order.objects.filter(status="Offen",type="Einlagerung")
    openOrdersOut = Order.objects.filter(status="Offen",type="Auslagerung")
    closedOrdersInToday = Order.objects.filter(status="Geschlossen",type="Einlagerung",served_on__date=date.today())
    closedOrdersOutToday = Order.objects.filter(status="Geschlossen",type="Auslagerung",served_on__date=date.today())
    
    sortedProducts = Product.getTopProductsToday()

    context={'openOrders':openOrders,'openOrdersIn':openOrdersIn,'openOrdersOut':openOrdersOut,'closedOrdersInToday':closedOrdersInToday,'closedOrdersOutToday':closedOrdersOutToday,'sortedProducts':sortedProducts}
    return render(request, 'dashboard.html',context)

# Lagerübersicht
def overview(request):
    Order.SortOrders()  
    openOrders = Order.objects.filter(status="Offen").order_by("priority")
    storages = Storage.objects.all()
    greenHouse = Storage.objects.get(number=-100)
    redHouse = Storage.objects.get(number=100)
    orders = Order.objects.filter(status="Offen")
    closedOrders = Order.objects.filter(status="Geschlossen",type="Auslagerung")
    categories = Category.objects.all()
    stacker = Stacker.objects.get()
    storingProducts = Product.objects.filter(storage__isnull=False)
    currentCapacity = Product.getCurrentCapacity()
    totalCapacity = Storage.getTotalCapacity()
    capacityRatio = currentCapacity/totalCapacity*100
    
    context={'openOrders':openOrders,'storages':storages,'greenHouse':greenHouse,'redHouse':redHouse,'categories':categories,'orders':orders,'closedOrders':closedOrders,'stacker':stacker,'storingProducts':storingProducts,'currentCapacity':currentCapacity,'totalCapacity':totalCapacity,'capacityRatio':capacityRatio}
    return render(request, 'overview.html',context)



def orders(request):
     orders = Order.objects.filter(status="Offen")
     closedOrders = Order.objects.filter(status="Geschlossen")
     return render(request, 'orders.html', {'orders': orders, 'closedOrders': closedOrders})

def orders_json(request):
    # "Offen" und "Geschlossen" QuerySets abrufen
    orders = Order.objects.filter(status="Offen").select_related('product')
    closed_orders = Order.objects.filter(status="Geschlossen").select_related('product')
    
    # Daten für offene Aufträge formatieren
    open_orders_data = [
        {
            'id': order.id,
            'create_number': order.createNumber(),
            'customer': order.customer,
            'product_name': order.product.name if order.product else None,
            'type': order.type,
            'arrived_on': order.arrived_on.strftime('%Y-%m-%d %H:%M:%S'),
            'status': order.status,
        }
        for order in orders
    ]

    # Daten für geschlossene Aufträge formatieren
    closed_orders_data = [
        {
            'id': order.id,
            'create_number': order.createNumber(),
            'customer': order.customer,
            'product_name': order.product.name if order.product else None,
            'type': order.type,
            'arrived_on': order.arrived_on.strftime('%Y-%m-%d %H:%M:%S'),
            'status': order.status,
        }
        for order in closed_orders
    ]

    # Beide Datensätze in ein Dictionary packen
    data = {
        'orders': open_orders_data,
        'closed_orders': closed_orders_data
    }

    return JsonResponse(data)


# offene Aufträge, einlagernd #######################################################

def openIncomingView(request):
    orders = Order.objects.filter(type="Einlagerung", status="Offen")
    closedOrders = Order.objects.filter(status="Geschlossen")
    return render(request, 'orders.html', {'orders': orders, 'closedOrders': closedOrders})

def Incoming_json(request):
    # "Offen" und "Geschlossen" QuerySets abrufen
    orders = Order.objects.filter(status="Offen", type="Einlagerung").select_related('product')
    closed_orders = Order.objects.filter(status="Geschlossen", type="Einlagerung").select_related('product')
    
    # Daten für offene Aufträge formatieren
    open_orders_data = [
        {
            'id': order.id,
            'create_number': order.createNumber(),
            'customer': order.customer,
            'product_name': order.product.name if order.product else None,
            'type': order.type,
            'arrived_on': order.arrived_on.strftime('%Y-%m-%d %H:%M:%S'),
            'status': order.status,
        }
        for order in orders
    ]

    # Daten für geschlossene Aufträge formatieren
    closed_orders_data = [
        {
            'id': order.id,
            'create_number': order.createNumber(),
            'customer': order.customer,
            'product_name': order.product.name if order.product else None,
            'type': order.type,
            'arrived_on': order.arrived_on.strftime('%Y-%m-%d %H:%M:%S'),
            'status': order.status,
        }
        for order in closed_orders
    ]

    # Beide Datensätze in ein Dictionary packen
    data = {
        'orders': open_orders_data,
        'closed_orders': closed_orders_data
    }

    return JsonResponse(data)


## Offene Aufträge, Auslagernd ####################################################################

def openOutgoingView(request):
    orders = Order.objects.filter(type="Auslagerung", status="Offen")
    closedOrders = Order.objects.filter(status="Geschlossen")
    return render(request, 'orders.html', {'orders': orders, 'closedOrders': closedOrders})

def outgoing_json(request):
    # "Offen" und "Geschlossen" QuerySets abrufen
    orders = Order.objects.filter(status="Offen", type="Auslagerung").select_related('product')
    closed_orders = Order.objects.filter(status="Geschlossen", type="Auslagerung").select_related('product')
    
    # Daten für offene Aufträge formatieren
    open_orders_data = [
        {
            'id': order.id,
            'create_number': order.createNumber(),
            'customer': order.customer,
            'product_name': order.product.name if order.product else None,
            'type': order.type,
            'arrived_on': order.arrived_on.strftime('%Y-%m-%d %H:%M:%S'),
            'status': order.status,
        }
        for order in orders
    ]

    # Daten für geschlossene Aufträge formatieren
    closed_orders_data = [
        {
            'id': order.id,
            'create_number': order.createNumber(),
            'customer': order.customer,
            'product_name': order.product.name if order.product else None,
            'type': order.type,
            'arrived_on': order.arrived_on.strftime('%Y-%m-%d %H:%M:%S'),
            'status': order.status,
        }
        for order in closed_orders
    ]

    # Beide Datensätze in ein Dictionary packen
    data = {
        'orders': open_orders_data,
        'closed_orders': closed_orders_data
    }

    return JsonResponse(data)


# Geschlossene Aufträge, Alle ####################################################################

def closedOrders(request):
     closedOrders = Order.objects.filter(status="Geschlossen")
     orders = Order.objects.filter(status="Offen")
     return render(request, 'orders.html', {'orders': orders, 'closedOrders': closedOrders})

def closedIncomingView(request):
    closedOrders = Order.objects.filter(type="Einlagerung", status="Geschlossen")
    orders = Order.objects.filter(status="Offen")
    return render(request, 'orders.html', {'orders': orders, 'closedOrders': closedOrders})

def closedOutgoingView(request):
    closedOrders = Order.objects.filter(type="Auslagerung", status="Geschlossen")
    orders = Order.objects.filter(status="Offen")
    return render(request, 'orders.html', {'orders': orders, 'closedOrders': closedOrders})


# Strategien
def strategies(request):
     strategies = Strategy.objects.all()
     return render(request, 'strategies.html', {'strategies': strategies})

def strategySimulation(request):
    return simulation(request)

# Historische Daten
def history(request):
    tours = Tour.objects.all()
    stacker = Stacker.objects.get()
    parameter = Parameter.objects.get()
    topProducts = Product.getTopProducts()

    aC=Product.getAverageCapacity()
    aRC=(Storage.objects.all().count()- 2 - aC)
    aLT=Tour.getAverageLeadTime()
    aTR=Tour.getAverageTurnoverRatio()
    days=Product.getDays()[0]
    tOI=Order.objects.filter(status="Geschlossen",type="Einlagerung").count()
    tOO=Order.objects.filter(status="Geschlossen",type="Auslagerung").count()
    aOIPD=tOI/days
    aOOPD=tOO/days

    tN=Tour.objects.filter(stacker=stacker).count()
    eT=Tour.objects.filter(stacker=stacker,type=None).count()
    d=stacker.distance
    eD=stacker.emptyDistance
    t=stacker.time
    eTi=stacker.emptyTime
    efT=stacker.getTourEfficiency(tN,eT)
    efD=stacker.getDistanceEfficiency(d,eD)
    efTi=stacker.getTimeEfficiency(t,eTi)

    context={'tours':tours,'stacker':stacker,'parameter':parameter,'topProducts':topProducts}

    averageContext={'averageCapacity':aC,'averageRestCapacity':aRC,'averageLeadTime':aLT,'averageTurnoverRatio':aTR}
    orderContext={'totalOrdersIn':tOI,'totalOrdersOut':tOO,'averageOrdersInPerDay':aOIPD,'averageOrdersOutPerDay':aOOPD}

    stackerContext={'toursNum':tN,'emptyTours':eT,'distance':d,'emptyDistance':eD,'time':t,'emptyTime':eTi,'efficiencyTour':efT,'efficiencyDistance':efD,'efficiencyTime':efTi}

    context.update(orderContext)
    context.update(averageContext)
    context.update(stackerContext)
    return render(request, 'history.html',context)

# Einstellungen
def settings(request):
     parameter = Parameter.objects.first()
     editable = False
     return render(request, 'settings.html', {'parameter': parameter,'editable':editable})

def editSettings(request):
     parameter = Parameter.objects.first()
     editable = True
     return render(request, 'settings.html', {'parameter': parameter,'editable':editable})

def saveSettings(request):
     vertical_speed = request.POST.get("vertical_speed")
     horizontal_speed = request.POST.get("horizontal_speed")
     material_durability = request.POST.get("material_durability")
     weight_control = request.POST.get("weight_control")
     weight_control_value = request.POST.get("weight_control_value")
     weight_control_from_story = request.POST.get("weight_control_from_story")

     parameter = Parameter.objects.first()  # Lade das Objekt, das du aktualisieren möchtest

     parameter.vertical_speed = vertical_speed
     parameter.horizontal_speed = horizontal_speed
     parameter.material_durability = material_durability
     parameter.weight_control = weight_control
     parameter.weight_control_value = weight_control_value
     parameter.weight_control_from_story = weight_control_from_story

     parameter.save()
     return settings(request)


def login(request):
     return render(request, 'login.html')