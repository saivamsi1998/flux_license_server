from django.contrib import admin

from .models import Offer, OfferAppMap, User, License, LicenseAppMap

admin.site.register(Offer)
admin.site.register(OfferAppMap)
admin.site.register(User)
admin.site.register(License)
admin.site.register(LicenseAppMap)
