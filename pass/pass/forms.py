from django.forms import ModelForm, CharField, PasswordInput, Form
from django.core.exceptions import ValidationError
from .models import Accounts
from .strxor import strxor

class AccountForm(ModelForm):

	password = CharField(max_length = 100,
			widget = PasswordInput
			)

	def clean_name(self):
		name = self.cleaned_data['name']

		names = [account.name for account in Accounts.objects.all()]

		if name in names:
			raise ValidationError('Name is already in database')
		else:
			return name

	def clean_password(self):
		return self.cleaned_data['password'] # You will want to add some kind of encryption here.

	class Meta:
		model = Accounts
		fields = ['name', 'username', 'password', 'url', 'metadata']

class LoginForm(Form):
	username = CharField()
	password = CharField(widget = PasswordInput)