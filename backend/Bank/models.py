from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
# Create your models here.


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    account_no = models.CharField(max_length=20,unique=True)

    def __str__(self):
        return f"{self.user.username}  account_no: {self.account_no} Balance : {self.balance}"



class PinCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    pin = models.CharField(max_length=10)


Choices = (
    ('WithDraw','WithDraw'),
    ('Transfer','Transfer'),
    ('Deposit','Deposit'),
)


class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    account = models.ForeignKey(Account,on_delete=models.CASCADE,related_name="user_account")
    accounts = models.ManyToManyField(Account,"transaction_accounts")




class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    from_account = models.ForeignKey(Account,on_delete=models.CASCADE,related_name="Sender_User")
    to_account = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    type = models.CharField(max_length=10,choices=Choices)
    sender_last_balance = models.DecimalField(max_digits=10,decimal_places=2)
    sender_updated_balance = models.DecimalField(max_digits=10,decimal_places=2)
    to_last_balance = models.DecimalField(max_digits=10,decimal_places=2)
    to_updated_balance = models.DecimalField(max_digits=10,decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if not self.pk:
            self.from_account = Account.objects.get(user=self.user)
            to_account = Account.objects.get(account_no=self.to_account)
            self.sender_last_balance =  self.from_account.balance
            self.to_last_balance = to_account.balance
            if self.type == "Deposit":
                # raise ValidationError("Error.....")
                to_account.balance += self.amount
            elif self.type == "Transfer":
                self.from_account.balance -= self.amount
                to_account.balance += self.amount
            elif self.type == "WithDraw":
                to_account.balance -= self.amount
            
            if History.objects.filter(user=self.user).exists():
                hist = History.objects.get(user=self.user)
                if to_account not in hist.accounts.all():
                    hist.accounts.add(to_account)
                    hist.save()
            else:
                hist = History(user=self.user,account=self.from_account)
                hist.save()
                hist.accounts.add(to_account)
                hist.save()
            self.from_account.save()
            to_account.save()
            self.sender_updated_balance = self.from_account.balance
            self.to_updated_balance = to_account.balance
        
        super(Transaction,self).save(*args,**kwargs)

    def __str__(self):
        return f"Amount {self.amount} {self.type} to {self.to_account} from {self.from_account.user.username}"










