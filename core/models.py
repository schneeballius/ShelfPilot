from django.db.models import Count,Q
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from collections import Counter

class Product(models.Model):
    storage = models.OneToOneField('Storage', on_delete=models.SET_NULL, related_name='related_product', null=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True)
    weight = models.IntegerField()
    name = models.CharField(max_length=200)
    storing = models.BooleanField()
    stored_on = models.DateTimeField(null=True)

    @staticmethod
    def getTopProducts():
        productsOnceStored = Product.objects.filter(stored_on__isnull=False)
        product_names = [product.name for product in productsOnceStored]
        product_counts = Counter(product_names)
        sortedProducts = sorted(product_counts.keys(), key=lambda x: (-product_counts[x], x))
        
        return sortedProducts

    @staticmethod
    def getTopProductsToday():
        productsStoredToday = Product.objects.filter(stored_on__date=now().date())
        product_names = [product.name for product in productsStoredToday]
        product_counts = Counter(product_names)
        sortedProducts = sorted(product_counts.keys(), key=lambda x: (-product_counts[x], x))

        return sortedProducts

    @staticmethod
    def getCurrentCapacity():
        currentCapacity = Product.objects.filter(storing=True).count()
        return currentCapacity

    @staticmethod
    def getAverageCapacity():
        
        # Vorgehen in Pseudocode: 
        # alle Producte holen, die einen "stored_on" wert haben
        # für jeden Tag: count(products) (stored_on<=today, (if exists) related_order.get(type="Auslagerung").served_on > today)

        # Produkte die lagern oder an irgendeinem Tag mal gelagert waren haben einen stored_on Wert
        products = Product.objects.filter(stored_on__isnull=False)
        if not products.exists():
            return 0

        dates=Product.getDays()
        dateDifference=dates[0]
        earliestDate=dates[1]
        latestDate=dates[2]
        

        # Der "served_on" Wert, der zu Auslagerungsaufträgen von manchen Produkten gehört gibt an
        # wann dieses Produkt ausgelagert wurde. Damit lässt sich für jedes Produkt Liste mit Einlagerungs- und Auslagerungsdatum erstellen
        productList=[]
        for product in products:
            relatedOrders=product.related_order.filter(type="Auslagerung",served_on__isnull=False)
            
            relatedOrder = relatedOrders.first() if relatedOrders.exists() else None

            # Datum oder None
            servedOnDates=relatedOrder.served_on if relatedOrder is not None else None

            productList.append({
                'stored_on':product.stored_on,
                'served_on':servedOnDates,
            })

        # Wenn man für jeden Tag prüft, wieviele Produkte einen "stored_on" Wert haben, welcher vor oder an diesem Tag liegt,
        # und einen (falls er überhaupt existiert) "served_on" Wert haben, welcher nach diesem Tag liegt, kann man feststellen,
        # wie viele Produkte an diesem Tag im Lager gelegen haben müssen
        productsCountSum=0
        iteratorDate=earliestDate
        while iteratorDate<=latestDate:
            print("date",iteratorDate)

            productCount=sum(
                1 for product in productList
                if product['stored_on'].date() <= iteratorDate.date() and
                (product['served_on'] is None or product['served_on'].date() > iteratorDate.date())
            )

            productsCountSum+=productCount
            iteratorDate+=timedelta(days=1)

        # Die Anzahl der Tage (mindestens 1) "dateDifference" kommt aus der Hilfsmethode getDays, um einen Durchschnitt der gesamten Lagerbestände aller Tage zu bilden
        averageCapacity=0 if productsCountSum==0 else productsCountSum/dateDifference
        return averageCapacity
    
    @staticmethod
    def getDays():
        products = Product.objects.filter(stored_on__isnull=False)

        earliestDate=products.aggregate(minDate=models.Min('stored_on'))['minDate']
        latestDate=products.aggregate(maxDate=models.Max('stored_on'))['maxDate']

        dateDifference = None
        if earliestDate and latestDate:
            dateDifference=(latestDate-earliestDate).days
        dateDifference=1 if dateDifference==0 or dateDifference==None else dateDifference

        return [dateDifference,earliestDate,latestDate]




class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='related_order', null=True)
    customer = models.CharField(max_length=200, default="")
    arrived_on = models.DateTimeField(default=timezone.now)
    served_on = models.DateTimeField(null=True)
    type = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    priority = models.IntegerField(null=True)

    def createNumber(self):
        return f"{self.customer[:3].upper()}{self.id}_{self.arrived_on.month}{(str(self.arrived_on.year))[2:]}"

    @staticmethod
    def SortOrders(force=False):

        activeStrategy = Strategy.objects.get(active=True)
        match activeStrategy.name:
            case "FIFO":
                if(force or Order.objects.filter(status="Offen",priority__isnull=True).exists()):
                    print("SORTIEREN")
                    orders=Order.objects.filter(status="Offen").order_by('arrived_on')
                    
                    prioCounter=1
                    for order in orders:
                        order.priority=prioCounter
                        order.save()
                        prioCounter+=1


class Storage(models.Model):
    product = models.OneToOneField(Product, on_delete=models.SET_NULL, related_name='related_storage', null=True)
    number = models.IntegerField(default=0)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    
    # number==-100 und number==100 sind für Wareneingang und Warenausgang reserviert, deshalb werden diese ausgeschlossen
    def getTotalCapacity():
        return Storage.objects.filter(~Q(number=100),~Q(number=-100)).count()

class Category(models.Model):
    name = models.CharField(max_length=200)

class Stacker(models.Model):
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True) # Der Simulation Stacker muss sich über alle Felder bewegen können
    strategy = models.ForeignKey('Strategy', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=200)
    distance = models.IntegerField(default=0)
    emptyDistance = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    emptyTime = models.IntegerField(default=0)
    material_load = models.IntegerField(default=0)

    @staticmethod
    def getTourEfficiency(tourNum,emptyTours):
        tourEfficiency=1 if tourNum==0 or emptyTours==0 else 1-(emptyTours/tourNum)
        return round(tourEfficiency,2)
    
    @staticmethod
    def getDistanceEfficiency(distance,emptyDistance):
        distanceEfficiency=1 if distance==0 or emptyDistance==0 else 1-(emptyDistance/distance)
        return round(distanceEfficiency,2)
    
    @staticmethod
    def getTimeEfficiency(time,emptyTime):
        timeEfficiency=1 if time==0 or emptyTime==0 else 1-(emptyTime/time)
        return round(timeEfficiency,2)

class Strategy(models.Model):
    name = models.CharField(max_length=200)
    active = models.BooleanField()

class Simulation(models.Model):
    strategy = models.ManyToManyField(Strategy, related_name='strategies')

class StrategySimulation(models.Model):
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    tours = models.IntegerField(default=-1)
    empty_tours = models.IntegerField(default=-1)
    distance = models.IntegerField(default=-1)
    empty_distance = models.IntegerField(default=-1)
    time = models.IntegerField(default=-1)
    empty_time = models.IntegerField(default=-1)
    tour_efficiency = models.FloatField(default=-1.0)
    distance_efficiency = models.FloatField(default=-1.0)
    time_efficiency = models.FloatField(default=-1.0)
    maintenance = models.IntegerField(default=0)

class Tour(models.Model):
    stacker = models.ForeignKey(Stacker, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    empty_time = models.IntegerField()
    time = models.IntegerField()
    empty_distance = models.IntegerField()
    distance = models.IntegerField()
    material_load = models.IntegerField(default=0)
    type = models.CharField(max_length=200,null=True)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True,related_name='tours')
    x1 = models.IntegerField(default=0)
    x2 = models.IntegerField(default=0)
    y1 = models.IntegerField(default=0)
    y2 = models.IntegerField(default=0)

    @staticmethod
    def getAverageLeadTime():

        totalLeadTime=0
        totalProductsMoved=0
        productWithMultipleTours=Product.objects.annotate(numTours=Count('tours')).filter(numTours__gt=1)
        
        for product in productWithMultipleTours:
            tours=Tour.objects.filter(product=product)

            for tour in tours:
                totalLeadTime+=tour.time
            
            totalProductsMoved+=1

        averageLeadTime=0 if totalProductsMoved==0 else totalLeadTime/totalProductsMoved
        return averageLeadTime
    
    @staticmethod
    def getAverageTurnoverRatio():
        tPM=Tour.getTotalProductsMoved()
        aC=Product.getAverageCapacity()
        averageTurnoverRatio = 0 if tPM==0 or aC==0 else tPM/aC

        return round(averageTurnoverRatio,2)

    @staticmethod
    def getTotalProductsMoved():
        productsWithMultipleOrders=Product.objects.annotate(numOrders=Count('related_order')).filter(numOrders__gt=1)
        totalProductsMoved=productsWithMultipleOrders.count()

        return totalProductsMoved

class Parameter(models.Model):
    stacker = models.ForeignKey(Stacker, on_delete=models.CASCADE)
    weight_control = models.BooleanField()
    weight_control_value = models.IntegerField(default=0)
    weight_control_from_story = models.IntegerField(default=0)
    vertical_speed = models.IntegerField()
    horizontal_speed = models.IntegerField()
    material_durability = models.IntegerField()