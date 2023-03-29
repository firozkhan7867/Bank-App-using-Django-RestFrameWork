from rest_framework import serializers
from .models import Account,PinCode,Transaction,History,Notification
from accounts.serializers import CustomUserSerializer


class AccountSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    class Meta:
        model = Account
        fields = ("id","balance","account_no","user")
        extra_kwargs = {
            'user':{
                'read_only':True
            }
        }
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user != instance.user:
            data.pop('balance')
        return data

class AccountOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id","user","account_no")


class PinCodeSerializer(serializers.ModelSerializer):
    account = AccountOtherSerializer(read_only=True)
    class Meta:
        model = PinCode
        fields = ("id","account","pin")
        extra_kwargs = {
            'pin':{
                "write_only":True
            },
            'account':{
                "read_only":True
            }
        }

class TransactionSerializer(serializers.ModelSerializer):
    pinCode = serializers.CharField(write_only=True)
    class Meta:
        model = Transaction
        fields = ("id","user","from_account","to_account","amount","type","sender_last_balance","sender_updated_balance","to_last_balance","to_updated_balance","pinCode")
        extra_kwargs = { 
            "from_account":{
                "read_only":True
            },
            "sender_last_balance":{
                "read_only":True
            },
            "sender_updated_balance":{
                "read_only":True
            },
            "to_last_balance":{
                "read_only":True
            },
            "to_updated_balance":{
                "read_only":True
            },
            "user":{
                "read_only":True
            }
        }
    def get_pinCode(self, obj):
        pass


class HistorySerializer(serializers.ModelSerializer):
    accounts = AccountOtherSerializer(many=True, read_only=True)
    account = AccountOtherSerializer(read_only=True)
    # accounts = serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    class Meta:
        model = History
        fields = ("id","accounts","account","user")
        extra_kwargs = {
            "account":{
                "read_only":True
            },
            "user":{
                "read_only":True
            }
        }
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['user'] = instance.user.username
    #     data['accounts'] = AccountSerializer(instance.accounts.all(), many=True).data
    #     return data


class NotificationSerializer(serializers.ModelSerializer):
    account = AccountOtherSerializer(read_only=True)
    class Meta:
        model = Notification
        fields =  ("id","account","amount","message")
        # extra_kwargs = {
        #     "account":{
        #         "read_only":True
        #     },
        # }

class ListTransactionBetweenUserSerializer(serializers.ModelSerializer):
    account_no = serializers.CharField()
    transactions = TransactionSerializer(many=True,read_only=True)
    class Meta:
        model = Transaction
        fields = ("account_no","transactions")




