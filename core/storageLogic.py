from django.utils.timezone import now

from .models import *

def store(product_id):
    storages = Storage.objects.filter(product=None, number__gt=-1, number__lt=50).order_by('number')
    storage = storages.first()
    
    product = Product.objects.get(id=product_id)
        
    if(storage.product==None):
        warehouseEntry = Storage.objects.get(number=-100)
        drive(warehouseEntry,-1,0)

        if(drive(storage,storage.x,storage.y,True,product,tourType="Einlagerung")==0):
            return 0

        storage.product=product
        product.storage=storage
        product.storing=True
        product.stored_on=now()
        product.save()
        storage.save()
        return 1

    return 0

def discard(product_id):
    storages = Storage.objects.filter(product__isnull=False, number__gt=-1, number__lt=50)
    product = Product.objects.get(id=product_id)

    for storage in storages:
        if(storage.product==product):
            drive(storage,storage.x,storage.y)    
            warehouseExit = Storage.objects.get(number=100)
            if(drive(warehouseExit,10,0,True,product,tourType="Auslagerung")==0):
                return 0

            storage.product=None
            product.storage=None
            product.storing=False
            product.save()
            storage.save()
            return 1
    return 0

def drive(storage,x2,y2,loaded=False,product=None,tourType=None):
    
    stacker = Stacker.objects.get()
    x1 = stacker.storage.x
    y1 = stacker.storage.y

    if(x1==x2 and y1==y2):
        return

    xDistance = abs(x1-x2)
    yDistance = abs(y1-y2)
    distance = xDistance+yDistance
    emptyDistance = 0 if loaded else distance

    parameter = Parameter.objects.get()
    verticalSpeed = parameter.vertical_speed
    horizontalSpeed = parameter.horizontal_speed
    weight_control = parameter.weight_control
    weight_control_value = parameter.weight_control_value
    weight_control_from_story = parameter.weight_control_from_story
    material_durability = parameter.material_durability

    materialLoad = product.weight*(distance-emptyDistance) if product!=None else 0
    if(stacker.material_load+materialLoad>material_durability):
        stacker.status="Überlastet"
        stacker.save()
        return 0
    elif(stacker.material_load+materialLoad >= material_durability*0.95):
        stacker.status="Hinweis_Wartung"
    else:
        stacker.status="Bereit"

    time = xDistance*horizontalSpeed+yDistance*verticalSpeed
    emptyTime = 0 if loaded else time
    
    tour = Tour.objects.create(
        stacker = stacker,
        date = now(),
        empty_time = emptyTime,
        time = time,
        empty_distance = emptyDistance,
        distance = distance,
        material_load = materialLoad,
        type=tourType,
        product=product,
        x1=x1,
        x2=x2,
        y1=y1,
        y2=y2    
    )

    stacker.distance += distance
    stacker.emptyDistance += emptyDistance
    stacker.time += time
    stacker.emptyTime += emptyTime
    stacker.storage = storage
    stacker.material_load += materialLoad
    stacker.save()
    return 1