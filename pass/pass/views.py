from django.shortcuts import render, render_to_response, redirect
from django.views.generic.base import View
from .forms import AccountForm, LoginForm

class LoginView(View):
	def get(self, request):
		return render(request, 'login.html', {
			'form': LoginForm()
		})
	def post(self, request):

		username = request.POST.get('username')
		password = request.POST.get('password')

		if  username == "<username>" and password == '<password>':
			request.session['username'] = username
			request.session['password'] = password

			return redirect('/account')


class AccountView(View):
	def get(self, request):

		valid_login = False
		if 'username' in request.session and 'password' in request.session:
			username = request.session.get('username')
			password = request.session.get('password')
			if username == "<username>" and password == '<password>':
				valid_login = True

		if valid_login:
			return render(request, 'account_entry.html', {
				'form': AccountForm()
			})
		else:
			return render(request, 'login.html', {
				'form': LoginForm()
			})

	def post(self, request):
		form = AccountForm(request.POST)
		if form.is_valid():

			form.save()

			return render_to_response('success.html')
		else:
			return render_to_response('failure.html')