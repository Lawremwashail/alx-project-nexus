# social/graphql/middleware.py
from graphql_jwt.middleware import JSONWebTokenMiddleware

class AuthMiddleware(JSONWebTokenMiddleware):
    """
    Extends JSONWebTokenMiddleware to attach a boolean `is_authenticated`
    and convenience `user_is_staff` to info.context for easy checks.
    """
    def resolve(self, next_, root, info, **args):
        user = getattr(info.context, "user", None)
        info.context.is_authenticated = bool(user and not user.is_anonymous)
        # convenience property (role example)
        info.context.user_is_staff = bool(user and getattr(user, "is_staff", False))
        return next_(root, info, **args)

