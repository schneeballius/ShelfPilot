from django.urls import path
from . import views
from . import helpers

urlpatterns = [

    path("", views.dashboard, name="dashboard"),
    path("historie", views.history, name="history"),
    path("login", views.login, name="login"),

    # Strategien
    path("strategien", views.strategies, name="strategies"),
    path("strategien/simulation", views.strategySimulation, name="strategySimulation"),

    # Aufträge
    path("aufträge", views.orders, name="orders"),
    path("aufträge-json", views.orders_json, name="orders_json"),
    
    path("openIncoming", views.openIncomingView, name='openIncoming'),
    path("incoming_json", views.Incoming_json, name="incoming_json"),
    
    path("openOutgoing", views.openOutgoingView, name='openOutgoing'),
    path("outgoing_json", views.outgoing_json, name="outgoing_json"),

    path("closedOrders", views.closedOrders, name="closedOrders"),
    path("closedIncoming", views.closedIncomingView, name="closedIncoming"),
    path("closedOutgoing", views.closedOutgoingView, name="closedOutgoing"),

    # Einstellungen
    path("einstellungen", views.settings, name="settings"),
    path('editSettings', views.editSettings, name='editSettings'),
    path('saveSettings', views.saveSettings, name='saveSettings'),

    path('deleteDummy', helpers.deleteDummyView, name='deleteDummy'),
    path('createDummy', helpers.createDummyView, name='createDummy'),


    # Lagerübersicht
    path("übersicht", views.overview, name="overview"),

    path('greenHouse', views.overview, name='greenHouse'),
    path('serveOrder/<int:order_id>', helpers.serveOrder, name='serveOrder'),
    path('deleteOrder/<int:order_id>', helpers.deleteOrder, name='deleteOrder'),

    path('redHouse', views.overview, name='redHouse'),

    path('addInOrder', helpers.addInOrder, name='addInOrder'),
    path('addOutOrder', helpers.addOutOrder, name='addOutOrder'),

    path('removeProduct/<int:product_id>/', helpers.removeProduct, name='removeProduct'),
]