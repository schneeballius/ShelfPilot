from django.shortcuts import render, redirect
from django.apps import apps
from .models import *

def simulation(request):

    selectedStrategies=request.POST.getlist('strategies')
    strategies = Strategy.objects.filter(id__in=selectedStrategies)
    simulation=Simulation.objects.create()

    for strategy in strategies:
        data=createSimulationData(strategy)
        tours=data['tours']
        emptyTours=data['emptyTours']
        distance=data['distance']
        emptyDistance=data['emptyDistance']
        time=data['time']
        emptyTime=data['emptyTime']
        tourEfficiency=data['tourEfficiency']
        distanceEfficiency=data['distanceEfficiency']
        timeEfficiency=data['timeEfficiency']
        maintenance=data['maintenance']

        simulation.strategy.add(strategy)

        strategySimulation = StrategySimulation.objects.create(
            simulation=simulation,
            strategy=strategy,
            tours=tours,
            empty_tours=emptyTours,
            distance=distance,
            empty_distance=emptyDistance,
            time=time,
            empty_time=emptyTime,
            tour_efficiency=tourEfficiency,
            distance_efficiency=distanceEfficiency,
            time_efficiency=timeEfficiency,
            maintenance=maintenance
        )
        strategySimulation.save()


    strategySimulations=StrategySimulation.objects.filter(simulation=simulation).all()

    strategies = Strategy.objects.all()
    return render(request, 'strategies.html', {'strategies': strategies,'strategySimulations':strategySimulations})

def createSimulationData(strategy):

    # Storage
    for i in range(4, -1, -1):
        for j in range(10):
            storage1 = Storage.objects.create(number=1000+10*i+j,x=j,y=i)

    # Stacker
    stacker = Stacker.objects.create(
        storage=Storage.objects.get(number=-100),
        strategy=strategy,
        status="Bereit"
    )

    error=[]
    maintenance=0

    match strategy.name:
        case "FIFO":
            openOrders = Order.objects.filter(status="Offen").order_by('priority')
        case "LIFO":
            openOrders = Order.objects.filter(status="Offen").order_by('-priority')
    
    for order in openOrders:
        product=order.product
        match order.type:
            case "Einlagerung":
                if(simStore(product,stacker) == 0):
                    error.append({'name': product.name, 'message': 'Einlagerung'})
                    print("Konnte nicht eingelagert werden!")
            case "Auslagerung":
                if(simDiscard(product,stacker) == 0):
                    error.append({'name': product.name, 'message': 'Auslagerung'})
                    print("Konnte nicht ausgelagert werden!")
        if(stacker.status=="Überlastet"):
            stacker.material_load=0
            stacker.status="Bereit"
            maintenance+=1
    
    # Staplerdaten, wie in history angeordnet
    tours = Tour.objects.filter(stacker=stacker).count()
    emptyTours = Tour.objects.filter(stacker=stacker,type=None).count()
    distance=stacker.distance
    emptyDistance=stacker.emptyDistance
    time=stacker.time
    emptyTime=stacker.emptyTime
    tourEfficiency=stacker.getTourEfficiency(tours,emptyTours)
    distanceEfficiency=stacker.getDistanceEfficiency(distance,emptyDistance)
    timeEfficiency=stacker.getTimeEfficiency(time,emptyTime)
   
    data={'maintenance':maintenance,'tours':tours,'emptyTours':emptyTours,'distance':distance,'emptyDistance':emptyDistance,'time':time,'emptyTime':emptyTime,'tourEfficiency':tourEfficiency,'distanceEfficiency':distanceEfficiency,'timeEfficiency':timeEfficiency}

    for tour in Tour.objects.filter(stacker=stacker):
        print("Distanz: ",tour.distance," Leer: ",tour.empty_distance," Zeit: ",tour.time," Leer: ",tour.empty_time," Material: ",tour.material_load, "Von (",tour.x1,",",tour.y1,") nach (",tour.x2,",",tour.y2,")")
    deleteSimulationData(stacker)
    return data
            
def simStore(product,stacker):
    storages = Storage.objects.filter(product=None,number__gt=999,number__lt=1050).order_by('number')
    if not storages.exists():
        return 0
    
    closestStorage = storages.first()
    minDist = distanceBetween(stacker,storages.first())[0] if storages.exists() else None
    for storage in storages:
        if distanceBetween(stacker,storage)[0] < minDist:
            minDist = distanceBetween(stacker,storage)[0]
            closestStorage = storage
    
    warehouseEntry = Storage.objects.get(number=-100)
    simDrive(stacker,warehouseEntry)
    # hier Fehler abfangen falls überladen
    simDrive(stacker,closestStorage,True,product,tourType="Einlagerung")
    closestStorage.product=product
    closestStorage.save()

    return 1

def simDiscard(product,stacker):
    storages = Storage.objects.filter(product__isnull=False,number__gt=999,number__lt=1050).order_by('number')

    for storage in storages:
        if(storage.product==product):
            simDrive(stacker,storage)
            warehouseExit = Storage.objects.get(number=100)
            # hier Fehler abfangen ?
            simDrive(stacker,warehouseExit,True,product,tourType="Auslagerung")
            storage.product=None
            storage.save()
            return 1
    return 0

def simDrive(stacker,storage,loaded=False,product=None,tourType=None):

    distance = distanceBetween(stacker,storage)[0]
    xDistance = distanceBetween(stacker,storage)[1]
    yDistance = distanceBetween(stacker,storage)[2]
    
    if distance==0:
        return
    
    emptyDistance = 0 if loaded else distance

    parameter = Parameter.objects.get()
    verticalSpeed = parameter.vertical_speed
    horizontalSpeed = parameter.horizontal_speed
    material_durability = parameter.material_durability

    materialLoad = product.weight*(distance-emptyDistance) if product!=None else 0
    if(stacker.material_load+materialLoad>material_durability):
        stacker.status="Überlastet"

    time = xDistance*horizontalSpeed+yDistance*verticalSpeed
    emptyTime = 0 if loaded else time

    Tour.objects.create(
        stacker = stacker,
        date = now(),
        empty_time = emptyTime,
        time = time,
        empty_distance = emptyDistance,
        distance = distance,
        material_load = materialLoad,
        type=tourType,
        product=product,
        x1=stacker.storage.x,
        y1=stacker.storage.y,
        x2=storage.x,
        y2=storage.y   
    )

    stacker.distance += distance
    stacker.emptyDistance += emptyDistance
    stacker.time += time
    stacker.emptyTime += emptyTime
    stacker.storage = storage
    stacker.material_load += materialLoad
    stacker.save()
    return 1

def distanceBetween(stacker,storage):
    x1 = stacker.storage.x
    y1 = stacker.storage.y
    x2 = storage.x
    y2 = storage.y

    xDistance = abs(x1-x2)
    yDistance = abs(y1-y2)

    distance = xDistance+yDistance

    return [distance,xDistance,yDistance]

def deleteSimulationData(stacker):
    simulationStorages = Storage.objects.filter(number__gt=999)
    simulationStorages.delete()

    tours = Tour.objects.filter(stacker=stacker)
    tours.delete()

    stacker.delete()