from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from .models import *
from .forms import *
from pylab import *


# ------Start view for Category ------------All done by predefined html pages all inheretied
class CreateCategory(CreateView):
    model = BudgetCategory
    fields = ['category_name']
    success_url = reverse_lazy('categorylist')


class CategoryList(ListView):
    model = BudgetCategory


class CategoryUpdate(UpdateView):
    model = BudgetCategory
    fields = ['category_name']
    success_url = reverse_lazy('categorylist')


class CategoryDelete(DeleteView):
    model = BudgetCategory
    fields = ['category_name']
    success_url = reverse_lazy('categorylist')


# ------End view for Category ------------
# ------Start view for AddExpense --------------
class CreateAddExpense(TemplateView):
    form_class = AddExpenseForm
    model_name = AddExpense
    template_name = "mainapp/addexpense_create.html"

    def get_queryset(self, request):
        user = request.session["username"]
        data = self.model_name.objects.filter(user=user)
        return data

    def get(self, request, *args, **kwargs):
        context = {}
        context["form"] = self.form_class
        context['data'] = self.get_queryset(request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # form.save()
            user = request.session["username"]
            print(user, "heretest")
            budget_category = form.cleaned_data["budget_category"]
            expense = form.cleaned_data["expense"]
            remarks = form.cleaned_data["remarks"]
            entered_date = form.cleaned_data["entered_date"]
            tr = AddExpense.objects.create(user=user, budget_category=budget_category, expense=expense,
                                           remarks=remarks, entered_date=entered_date)
            tr.save()
        return redirect("addexpenselist")


class AddExpenseList(TemplateView):
    model_name = AddExpense
    template_name = "mainapp/addexpense_list.html"

    def get_queryset(self, request):
        return self.model_name.objects.filter(user=request.session['username'])

    def get(self, request, *args, **kwargs):
        context = {}
        context['qs'] = self.get_queryset(request)
        user = request.session["username"]
        context['user'] = user
        return render(request, self.template_name, context)


class AddExpenseDetail(TemplateView):
    model_name = AddExpense
    form_class = AddExpenseForm
    template_name = "mainapp/addexpense_detail.html"

    def get_queryset(self):
        return self.model_name.objects.get(id=self.kwargs.get("pk"))

    def get(self, request, *args, **kwargs):
        # form = self.form_class(instance=self.get_queryset())  # to get the form of instance pk
        context = {}
        # context['form'] = form
        qs = self.get_queryset()
        context['qs'] = qs
        return render(request, self.template_name, context)


class AddExpenseUpdate(TemplateView):
    model_name = AddExpense
    form_class = AddExpenseForm
    template_name = "mainapp/addexpense_create.html"

    def get_queryset(self):
        return self.model_name.objects.get(id=self.kwargs.get("pk"))

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_queryset())  # to get the form of instance pk
        context = {}
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            ob = self.get_queryset()
            ob.budget_category = form.cleaned_data["budget_category"]
            ob.expense = form.cleaned_data["expense"]
            ob.remarks = form.cleaned_data["remarks"]
            ob.entered_date = form.cleaned_data["entered_date"]
            ob.save()
            return redirect("addexpenselist")
        else:
            context = {}
            context['form'] = form
            return render(request, self.template_name, context)


class AddExpenseDelete(TemplateView):
    model_name = AddExpense
    form_class = AddExpenseForm
    template_name = "mainapp/addexpensedelete.html"

    def get_queryset(self):
        return self.model_name.objects.get(id=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_queryset())  # to get the form of instance pk
        context = {}
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.get_queryset().delete()
        print('deleted')
        return redirect("addexpenselist")


# ------End view for AddExpense --------------
def BudgetReport(request):
    if request.method == 'POST':
        user = request.session['username']
        context = {}
        context['user'] = user
        startdate = (request.POST.get("startdate"))
        enddate = (request.POST.get("enddate"))
        print(startdate, enddate)
        # categorywise sum within a date range
        at = AddExpense.objects.filter(user=user).filter(
            entered_date__range=[startdate, enddate]).values('budget_category__category_name'). \
            annotate(categorysum=Sum('expense')).order_by('-categorysum')
        context['t'] = at
        # DateWiseReport
        data = AddExpense.objects.filter(user=user).filter(
            entered_date__range=[startdate, enddate])
        context['data'] = data
        # Total Expense for a Date Range
        qs = AddExpense.objects.filter(user=user).filter(
            entered_date__range=[startdate, enddate]).aggregate(sum=Sum('expense'))
        context['qs'] = qs
        return render(request, 'mainapp/budgetreport.html', context)
    return render(request, 'mainapp/enterdatereview.html')


def Analysis(request, *args, **kwargs):
    if request.method == 'POST':
        user = request.session["username"]
        context = {}
        budget = float(request.POST.get("budget"))
        print(budget)
        context['bud'] = budget
        da = AddExpense.objects.filter(user=user)
        for value in da:
            print(value)
            print(value.expense)
            lst = [item.expense for item in da]
            t = sum(lst)
        print(type(t))
        sumo = float(t)
        print(type(sumo))
        context['data'] = sumo
        diff = budget - sumo
        print(diff)
        context['diff'] = diff
        context['user'] = user
        context['qs'] = da
        return render(request, 'mainapp/budgetreport_analysis.html', context)
    return render(request, 'mainapp/analysis.html')


class BudgetReview(TemplateView):
    model_name = AddExpense
    form_class = ReviewForm
    template_name = 'mainapp/review.html'

    def get(self, request, *args, **kwargs):
        context = {}
        form = self.form_class
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = request.session["username"]
            print(user)
            budget_category = form.cleaned_data["budget_category"]
            startdate = form.cleaned_data["startdate"]
            enddate = form.cleaned_data["enddate"]
            print(budget_category)
            print(startdate, enddate)
            context = {}
            qs = self.get_queryset(request, startdate, enddate, budget_category)
            print(qs)
            context['qs'] = qs
            context['form'] = form
            return render(request, self.template_name, context)

    def get_queryset(self, request, startdate, enddate, budget_category):
        return self.model_name.objects.filter(budget_category__category_name=budget_category).filter(
            user=request.session['username']).filter(entered_date__range=[startdate, enddate]). \
            values('budget_category__category_name').annotate(categorysum=Sum('expense')). \
            order_by('-categorysum')
