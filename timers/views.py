import datetime

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import JsonResponse, HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    DetailView,
    View,
    CreateView,
    UpdateView,
    TemplateView,
    FormView,
    RedirectView,
    DeleteView,
)
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin
from django.views.generic.edit import ProcessFormView

from timers.forms import ShortCodeForm, TableOffestForm, ConfirmForm, TimeDurationWidget
from timers.models import Session, Timer, TableOffset


class SessionValidation(UserPassesTestMixin, AccessMixin):
    api = True
    raise_exception = True

    def test_func(self):
        valid = self.request.session.get("valid_sessions", [])
        return self.kwargs["slug"] in valid

    def handle_no_permission(self):
        if self.api:
            super().handle_no_permission()
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                "Sorry, you not authorized to access that page",
            )
            return redirect(reverse("timers:view_session", kwargs=self.kwargs))


# Create your views here.
class HomeView(TemplateView):
    template_name = "home.html"


class JoinAdminView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        x = self.request.GET["code"]
        signer = TimestampSigner()
        try:
            session = signer.unsign(x, max_age=datetime.timedelta(minutes=5))
        except SignatureExpired:
            messages.add_message(
                self.request,
                message="Invite expired. Please try again",
                level=messages.ERROR,
            )
            return reverse("timers:home")
        except BadSignature:
            messages.add_message(
                self.request,
                message="Invalid invite. Please try again",
                level=messages.ERROR,
            )
            return reverse("timers:home")

        valid = self.request.session.get("valid_sessions", [])
        if session not in valid:
            valid.append(session)
        self.request.session["valid_sessions"] = valid
        return reverse("timers:control_session", args=[session])


class InviteAdminView(SessionValidation, DetailView):
    model = Session
    template_name = "timers/invite_admin.html"
    slug_field = "short_code"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        signer = TimestampSigner()
        token = signer.sign(self.object.short_code)
        context["access_token"] = token
        return context


class CreateTableView(SessionValidation, CreateView):
    model = TableOffset
    template_name = "timers/create_table.html"
    form_class = TableOffestForm

    def get_session(self):
        return get_object_or_404(Session.objects.filter(short_code=self.kwargs["slug"]))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.session = kwargs["session"] = self.get_session()
        return kwargs

    def form_valid(self, form):
        form.instance.session = self.session
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("timers:control_session", args=[self.session.short_code])


class UpdateTableView(SessionValidation, UpdateView):
    model = TableOffset
    template_name = "timers/update_table.html"
    form_class = TableOffestForm

    def get_session(self):
        return get_object_or_404(Session.objects.filter(short_code=self.kwargs["slug"]))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.session = kwargs["session"] = self.get_session()
        return kwargs

    def get_success_url(self):
        return reverse("timers:control_session", args=[self.session.short_code])


class DeleteTableView(SessionValidation, DeleteView):
    model = TableOffset
    template_name = "timers/create_table.html"

    def post(self, request, *args, **kwargs):
        self.session = self.get_session()
        return super().post(request, *args, **kwargs)

    def get_session(self):
        return get_object_or_404(Session.objects.filter(short_code=self.kwargs["slug"]))

    def get_success_url(self):
        return reverse("timers:control_session", args=[self.session.short_code])


class DeleteAllTablesView(SessionValidation, FormView):
    model = TableOffset
    template_name = "timers/create_table.html"
    form_class = ConfirmForm

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        for i in self.get_session().tableoffset_set.all():
            i.delete()
        return response

    def get_session(self) -> Session:
        return get_object_or_404(Session.objects.filter(short_code=self.kwargs["slug"]))

    def get_success_url(self):
        return reverse("timers:control_session", args=[self.get_session().short_code])


class TimerView(DetailView):
    model = Session
    template_name = "timers/timerview.html"
    slug_field = "short_code"

    def get_context_data(self, **kwargs):
        args = super().get_context_data(**kwargs)
        assert isinstance(self.object, Session)
        args["selected_tables"] = self.request.GET.getlist(
            "selectedTables", [str(s) for s in self.object.available_tables]
        )
        return args


class SelectSessionView(FormView):
    template_name = "timers/select_session.html"
    form_class = ShortCodeForm

    def form_valid(self, form):
        self.object = Session.objects.filter(
            short_code=form.cleaned_data["short_code"]
        ).get()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("timers:view_session", args=[self.object.short_code])


class SelectPersonalSessionView(FormView):
    template_name = "timers/select_session.html"
    form_class = ShortCodeForm

    def form_valid(self, form):
        self.object = Session.objects.filter(short_code=form.cleaned_data["short_code"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("timers:view_table_table", args=[self.object.short_code])


class CreateSessionView(CreateView):
    model = Session
    template_name = "timers/create_session.html"
    fields = ["title"]

    def form_valid(self, form):
        resp = super().form_valid(form)
        Timer.objects.create(
            duration=datetime.timedelta(minutes=30),
            remaining_duration=datetime.timedelta(minutes=30),
            start_time=timezone.now(),
            session=self.object,
        )
        existing_authorizations = self.request.session.get("valid_sessions", [])
        assert isinstance(self.object, Session)
        existing_authorizations.append(self.object.short_code)
        self.request.session["valid_sessions"] = existing_authorizations
        return resp

    def get_success_url(self):
        return reverse("timers:control_session", args=[self.object.short_code])


class UpdateSessionView(SessionValidation, UpdateView):
    model = Session
    template_name = "timers/update_session.html"
    fields = ["title", "round"]
    slug_field = "short_code"

    def get_success_url(self):
        return reverse("timers:control_session", args=[self.object.short_code])


class UpdateSessionTimeView(SessionValidation, UpdateView):
    model = Timer
    template_name = "timers/edit_time.html"
    fields = ["duration"]
    slug_field = "short_code"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg)

        queryset = queryset.filter(session__short_code=slug)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )

        return obj

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields["duration"].widget = TimeDurationWidget()
        return form

    def form_valid(self, form):
        resp = super().form_valid(form)
        self.object.reset()
        return resp

    def get_success_url(self):
        return reverse("timers:control_session", args=[self.object.session.short_code])


class ControlView(SessionValidation, DetailView):
    model = Session
    template_name = "timers/control.html"
    slug_field = "short_code"
    api = False


class SessionStateJson(View):
    def get(self, request: HttpRequest, slug: str):
        session = Session.objects.get(short_code=slug)
        tables = {}
        for table in session.tableoffset_set.all():
            tables[str(table.table)] = {
                "remaining_duration": int(table.remaining_duration.total_seconds())
            }
        return JsonResponse(
            {
                "session": session.short_code,
                "running": session.timer.running,
                "start_time": session.timer.start_time.isoformat(),
                "duration": int(session.timer.duration.total_seconds()),
                "remaining_duration": int(
                    session.timer.remaining_duration.total_seconds()
                ),
                "tables": tables,
            }
        )


class APIPauseView(SessionValidation, View):
    def post(self, request: HttpRequest, slug: str):
        session = Session.objects.get(short_code=slug)
        session.timer.pause()
        return HttpResponse(status=204)


class APIStartView(SessionValidation, View):
    def post(self, request: HttpRequest, slug: str):
        session = Session.objects.get(short_code=slug)
        session.timer.start()
        return HttpResponse(status=204)


class APIResetView(SessionValidation, View):
    def post(self, request: HttpRequest, slug: str):
        session = Session.objects.get(short_code=slug)
        session.timer.reset()
        return HttpResponse(status=204)
