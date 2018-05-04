from django.core.exceptions import PermissionDenied


class GroupRequiredMixin(object):
    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied
        else:
            user_groups = []
            for group in request.user.groups.values_list('name', flat=True):
                user_groups.append(group)
            if len(set(user_groups).intersection(self.group_required)) <= 0:
                raise PermissionDenied
        return super(GroupRequiredMixin, self).dispatch(request, *args, **kwargs)


class AdminUser(object):
    user_required = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied
        else:
            user_admin = []
            user_admin.append(request.user.username)
            if len(set(user_admin).intersection(self.user_required)) <= 0:
                raise PermissionDenied
        return super(AdminUser, self).dispatch(request, *args, **kwargs)
