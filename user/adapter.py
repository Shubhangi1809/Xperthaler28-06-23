from django.conf import settings
# from allauth.account.adapter import DefaultAccountAdapter
from user.models import UserProfile, UserSocialLink
from django.contrib.auth.models import User
from django.contrib.auth import logout

# from allauth.exceptions import ImmediateHttpResponse

# class MyAccountAdapter(DefaultAccountAdapter):
#     def pre_social_login(self, request, sociallogin):
#         try:
#             user = User.objects.get(email=sociallogin.email)
#             sociallogin.connect(request, user)
#             # Create a response object
#             # raise ImmediateHttpResponse(response)
#         except User.DoesNotExist:
#             pass

    # def get_login_redirect_url(self, request):
    #     UserProfile.objects.get_or_create(user = request.user)
    #     UserSocialLink.objects.get_or_create(user = request.user)
    #     redirect_url = request.session['redirect_url']
    #     user_id = request.user.id
    #     del request.session['redirect_url']
    #     logout(request)
    #     path = "{domain}/social-login-redirect/{user_id}"
    #     return path.format(domain=redirect_url, user_id=user_id)
