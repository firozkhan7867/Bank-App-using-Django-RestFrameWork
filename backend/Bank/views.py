from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import AccountSerializer,PinCodeSerializer,TransactionSerializer,HistorySerializer
from .models import Account,PinCode,Transaction,History
from .permissions import UpdateOwnAccount
# Create your views here.




class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,UpdateOwnAccount)
    queryset = Account.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class PinCodeViewSet(viewsets.ModelViewSet):
    serializer_class = PinCodeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,UpdateOwnAccount,)
    queryset = PinCode.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        account = Account.objects.get(user=self.request.user)
        print(account)
        serializer.save(user=self.request.user,account=account)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,UpdateOwnAccount,)
    queryset = Transaction.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Will raise ValidationError if serializer is invalid
        pinCode = serializer.validated_data["pinCode"]
        if PinCode.objects.filter(user=self.request.user).exists():
            pin = PinCode.objects.get(user=self.request.user)
            if pinCode != pin.pin:
                return Response({"Error":"Invalid PinCode Entered ..   Illegal Transaction ......!!!!!!!!"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error":"Please Generate a PinCode before making any Transaction....   Illegal Transaction ......!!!!!!!!"},status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data["type"] == "Deposit":
            from_account = Account.objects.get(user=self.request.user)
            to_account = Account.objects.get(account_no=serializer.validated_data["to_account"])
            if to_account != from_account:
                return Response({"Error":"User Account and To Account details does not match"},status=status.HTTP_400_BAD_REQUEST)
        elif serializer.validated_data["type"] == "WithDraw":
            from_account = Account.objects.get(user=self.request.user)
            to_account = Account.objects.get(account_no=serializer.validated_data["to_account"])
            if to_account.account_no != from_account.account_no:
                return Response({"Error":"User Account and To Account details does not match"},status=status.HTTP_400_BAD_REQUEST)
            amount = serializer.validated_data["amount"]
            if from_account.balance -amount < 0 or to_account.balance - amount <0:
                return Response({"Error":"Insufficient Fund. Cannot WithDraw Money"},status=status.HTTP_400_BAD_REQUEST)
        elif serializer.validated_data["type"] == "Transfer":
            from_account = Account.objects.get(user=self.request.user)
            amount = serializer.validated_data["amount"]
            if from_account.balance - amount < 0:
                return Response({"Error":"Insufficient Fund. Transaction of Money Not Possible"},status=status.HTTP_400_BAD_REQUEST)
        serializer.validated_data.pop("pinCode")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,UpdateOwnAccount,)
    serializer_class = HistorySerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        account = Account.objects.get(user=self.request.user)
        serializer.save(user=self.request.user,account=account)

