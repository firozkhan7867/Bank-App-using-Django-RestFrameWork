from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import AccountSerializer,PinCodeSerializer,TransactionSerializer,HistorySerializer,NotificationSerializer,ListTransactionBetweenUserSerializer
from .models import Account,PinCode,Transaction,History,Notification
from .permissions import UpdateOwnAccount
from drf_spectacular.utils import extend_schema,OpenApiParameter
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
 


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

@extend_schema(
    request=None,
    responses=TransactionSerializer(many=True),
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY),
    ]
)
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,UpdateOwnAccount,)
    queryset = Transaction.objects.all()
    pagination_class = MyPagination

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
            to_account = Account.objects.get(account_no=serializer.validated_data["to_account"])
            amount = serializer.validated_data["amount"]
            if from_account.balance - amount < 0:
                return Response({"Error":"Insufficient Fund. Transaction of Money Not Possible"},status=status.HTTP_400_BAD_REQUEST)
            if from_account.account_no == to_account.account_no:
                return Response({"Error":"Invalid Transation.....!!!!!"},status=status.HTTP_400_BAD_REQUEST)
            
        serializer.validated_data.pop("pinCode")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



@extend_schema(
    request=None,
    responses=HistorySerializer(many=True),
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY),
    ]
)
class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,UpdateOwnAccount,)
    serializer_class = HistorySerializer
    pagination_class = MyPagination
    pagination_class = MyPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        account = Account.objects.get(user=self.request.user)
        serializer.save(user=self.request.user,account=account)

@extend_schema(
    request=None,
    responses=NotificationSerializer(many=True),
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY),
    ]
)
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,UpdateOwnAccount,)
    serializer_class = NotificationSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# @extend_schema(
#     request=None,
#     responses=TransactionSerializer(many=True),
#     parameters=[
#         OpenApiParameter('page', int, OpenApiParameter.QUERY),
#         OpenApiParameter('page_size', int, OpenApiParameter.QUERY),
#     ]
# )
class ListTransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionSerializer
    # pagination_class = MyPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='account_no',
                location=OpenApiParameter.QUERY,
                description='Account ID',
            ),OpenApiParameter(
                name='page',
                location=OpenApiParameter.QUERY,
                description='Page no',
            ),OpenApiParameter(
                name='page_size',
                location=OpenApiParameter.QUERY,
                description='Page Size',
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
            account_no -- A first parameter
        """ 
        account_no = request.query_params.get('account_no',None)
        if not account_no:
            return Response({'Error': 'Account  field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        from_account = Account.objects.get(user=self.request.user)
        try:
            to_account = Account.objects.get(account_no=account_no)
        except:
            return Response({'Error': 'Account not found in server.... check ur account number'}, status=status.HTTP_400_BAD_REQUEST)
        to_user = to_account.user
        
        page = request.query_params.get('page',1)
        page_size = request.query_params.get('page_size',10)
        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page = 1
            page_size = 10
        
        offset = (page - 1) * page_size
        limit = offset + page_size
        transactions = Transaction.objects.filter(Q(from_account=from_account) & Q(to_account=account_no) | Q(from_account=to_account) & Q(to_account=from_account.account_no),Q(user=self.request.user) | Q(user=to_user)).order_by("-id")[offset:limit]
        

        serializer = ListTransactionBetweenUserSerializer({'account_no': account_no, 'transactions': transactions}, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)



