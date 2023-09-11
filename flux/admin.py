from django.contrib import admin

from .models import User, Offer, OfferAppMap, OfferUserMap, License, LicenseAppMap

admin.site.register(User)
admin.site.register(Offer)
admin.site.register(OfferAppMap)
admin.site.register(OfferUserMap)
admin.site.register(License)
admin.site.register(LicenseAppMap)
