from django.urls import path,include
from rest_framework.routers import DefaultRouter
from Bank import views

router = DefaultRouter()
router.register("account",views.AccountViewSet,basename="account")
router.register("pinCode",views.PinCodeViewSet)
router.register("transaction",views.TransactionViewSet)
router.register("History",views.HistoryViewSet)
router.register("notification",views.NotificationViewSet)
router.register("listTransaction",views.ListTransactionViewSet)

urlpatterns = [
    path('',include(router.urls)),
]



# a@gmail 640f7380371435c7114ba9e04a567509df2e6aac
# firoz@gmail ca1d5dd666ddadaded2c8c6d81285ed7eaea95d3
# f@gmail.com  dc0610021d85c385dd2e492a78ec530b39206cb7