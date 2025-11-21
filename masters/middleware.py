# masters/middleware.py
import threading
from django.utils.deprecation import MiddlewareMixin
from django.apps import apps

_user = threading.local()


def get_current_user(request=None):
    """Return the current logged-in user from thread-local storage or session."""
    if request is not None:
        # Check UserCustom login session
        user_id = request.session.get("user_id")
        if user_id:
            UserCustom = apps.get_model("masters", "UserCustom")
            try:
                return UserCustom.objects.get(id=user_id)
            except UserCustom.DoesNotExist:
                return None

        # Check Employee login session
        employee_id = request.session.get("employee_id")
        if employee_id:
            Employee = apps.get_model("employee_management", "Employee")
            try:
                return Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return None

    # Thread-local fallback
    return getattr(_user, "value", None)


class CurrentUserMiddleware(MiddlewareMixin):
    """Middleware to store the current logged-in user in thread-local."""

    def process_request(self, request):
        _user.value = get_current_user(request)

    def process_response(self, request, response):
        _user.value = None
        return response



class RecentActivityMiddleware(MiddlewareMixin):
    """
    Optional: logs 'viewed' detail pages into RecentActivity.
    Uses apps.get_model to avoid circular imports.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        # skip admin/static/media/ajax
        if (
            request.path.startswith("/admin/")
            or request.path.startswith("/static/")
            or request.path.startswith("/media/")
            or request.headers.get("x-requested-with") == "XMLHttpRequest"
        ):
            return None

        user = get_current_user(request)
        if not user:
            return None

        try:
            resolver_match = resolve(request.path)
            view_name = resolver_match.url_name or ""
            app_name = resolver_match.app_name or ""
        except Exception:
            return None

        if view_name.endswith("_detail"):
            pk = view_kwargs.get("pk")
            if not pk:
                return None

            try:
                model_name = view_name.replace("_detail", "").capitalize()
                model_class = apps.get_model(app_name, model_name)
                obj = model_class.objects.filter(pk=pk).first()
            except LookupError:
                return None

            if obj:
                RecentActivity = apps.get_model("masters", "RecentActivity")
                RecentActivity.objects.create(
                    user_content_type=ContentType.objects.get_for_model(user),
                    user_object_id=user.pk,
                    action="viewed",
                    model_name=model_class.__name__,
                    object_id=obj.pk,
                    object_repr=str(obj)[:200],
                )
        return None
