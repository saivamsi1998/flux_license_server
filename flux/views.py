from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone

HEARTBEAT_TIME = 60 #min
BUFFER_TIME = 5 #min

@csrf_exempt 
def index(request):
	return HttpResponse("Hello, world. You're at the flux index.")


def reg(request):
	license_id = request.POST["license_id"]
	user_id = request.POST["user_id"]
	app_id = request.POST["app_id"]
	device_id = request.POST["device_id"]

	# verify if the user, app is part of the license
	try:
		offer = Offer.objects.get(license_id = license_id)
		offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
		user = offerusermap_entry.user
		offer.offerappmap_set.get(app_id = app_id)

		# license update
		query_set_count = License.objects.filter(offer = offer, user = user, device_id = device_id).count()
		if (query_set_count  == 0):
			# check and allocate license and add license entry
			# mutex might be required when updating active_license_count
			if (offer.active_license_count >= offer.max_license_count):
				return HttpResponse("Pool license limit reached")
			else:
				offer.active_license_count += 1
				offer.save()
				license = License.objects.create(offer = offer, user = user, device_id = device_id)
				print("Created Pool License entry for (license_id, user_id, device_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id))
		# add/update license app map entry
		if (query_set_count == 0 or query_set_count == 1):
			try:
				licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
				licenseappmap_entry.last_active_time = timezone.now()
				licenseappmap_entry.save()
			except (KeyError, LicenseAppMap.DoesNotExist):
				license.licenseappmap_set.create(app_id = app_id, last_active_time = timezone.now())
			print("Created/Updated LicenseAppMap entry due to expired heartbeat for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
			# TODO: Schedule next heartbeat check and remove entry
		if (query_set_count >= 2):
			return HttpResponse("Multiple license for same (user, device) tuple found. Something went wrong")

	except (KeyError, Offer.DoesNotExist):
		return HttpResponse("Offer isn't available for given license id")
	except (KeyError, OfferUserMap.DoesNotExist):
		return HttpResponse("Offer isn't available for given user id")
	except (KeyError, OfferAppMap.DoesNotExist):
		return HttpResponse("Offer isn't available for given app id")

def heartbeat(request):
	license_id = request.POST["license_id"]
	user_id = request.POST["user_id"]
	app_id = request.POST["app_id"]
	device_id = request.POST["device_id"]

	# verify if the user, app is part of the license
	try:
		offer = Offer.objects.get(license_id = license_id)
		offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
		user = offerusermap_entry.user
		offer.offerappmap_set.get(app_id = app_id)

		# license update
		query_set_count = License.objects.filter(offer = offer, user = user, device_id = device_id).count()
		if (query_set_count  == 0):
			# check and allocate license and add license entry
			# mutex might be required when updating active_license_count
			if (offer.active_license_count >= offer.max_license_count):
				return HttpResponse("Pool license limit reached")
			else:
				offer.active_license_count += 1
				offer.save()
				license = License.objects.create(offer = offer, user = user, device_id = device_id)
				print("Created Pool License entry for (license_id, user_id, device_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id))
		# add/update license app map entry
		if (query_set_count == 0 or query_set_count == 1):
			try:
				licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
				licenseappmap_entry.last_active_time = timezone.now()
				licenseappmap_entry.save()
			except (KeyError, LicenseAppMap.DoesNotExist):
				license.licenseappmap_set.create(app_id = app_id, last_active_time = timezone.now())
			print("Created/Updated LicenseAppMap entry due to expired heartbeat for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
			# TODO: Schedule next heartbeat check and remove entry
		if (query_set_count >= 2):
			return HttpResponse("Multiple license for same (user, device) tuple found. Something went wrong")

	except (KeyError, Offer.DoesNotExist):
		return HttpResponse("Offer isn't available for given license id")
	except (KeyError, OfferUserMap.DoesNotExist):
		return HttpResponse("Offer isn't available for given user id")
	except (KeyError, OfferAppMap.DoesNotExist):
		return HttpResponse("Offer isn't available for given app id")


def dereg(request):
	license_id = request.POST["license_id"]
	user_id = request.POST["user_id"]
	app_id = request.POST["app_id"]
	device_id = request.POST["device_id"]

	# verify if the user, app is part of the license
	try:
		offer = Offer.objects.get(license_id = license_id)
		offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
		user = offerusermap_entry.user
		offer.offerappmap_set.get(app_id = app_id)

		# license update
		query_set = License.objects.filter(offer = offer, user = user, device_id = device_id)
		query_set_count = query_set.count()
		if (query_set_count  == 0):
			# do nothing
			return HttpResponse("Dereg call made for non existant license entry")
		# Remove license app map entry
		if (query_set_count == 1):
			try:
				licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
				licenseappmap_entry.delete()
			except (KeyError, LicenseAppMap.DoesNotExist):
				return HttpResponse("Dereg call made for non existant licenceappmap entry")
			if (license.licenseappmap_set.count()==0):
				try:
					License.objects.get(offer = offer, user = user, device_id = device_id).delete();
				except (KeyError, License.DoesNotExist):
					return HttpResponse("Offer isn't available for given license id")
				offer.active_license_count -= 1
				offer.save()
				print("Released Pool License entry for (license_id, user_id, device_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id))
		if (query_set_count >= 2):
			return HttpResponse("Multiple license for same (user, device) tuple found. Something went wrong")

	except (KeyError, Offer.DoesNotExist):
		return HttpResponse("Offer isn't available for given license id")
	except (KeyError, OfferUserMap.DoesNotExist):
		return HttpResponse("Offer isn't available for given user id")
	except (KeyError, OfferAppMap.DoesNotExist):
		return HttpResponse("Offer isn't available for given app id")

def dereg_by_server_if_req(request, license_id, user_id, device_id, app_id):
	# verify if the user, app is part of the license
	try:
		offer = Offer.objects.get(license_id = license_id)
		offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
		user = offerusermap_entry.user
		offer.offerappmap_set.get(app_id = app_id)

		# license update
		query_set = License.objects.filter(offer = offer, user = user, device_id = device_id)
		query_set_count = query_set.count()
		if (query_set_count  == 0):
			# do nothing
			return HttpResponse("Dereg call made for non existant license entry")
		# Remove license app map entry
		if (query_set_count == 1):
			try:
				licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
				if (licenseappmap_entry.last_active_time +  timezone.timedelta(minutes = HEARTBEAT+BUFFER) < timezone.now()):
					licenseappmap_entry.delete()
					print("Removed LicenseAppMap entry due to expired heartbeat for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
			except (KeyError, LicenseAppMap.DoesNotExist):
				return HttpResponse("Dereg call made for non existant licenceappmap entry")
			if (license.licenseappmap_set.count()==0):
				try:
					License.objects.get(offer = offer, user = user, device_id = device_id).delete();
				except (KeyError, License.DoesNotExist):
					return HttpResponse("Offer isn't available for given license id")
				offer.active_license_count -= 1
				offer.save()
				print("Released Pool License entry by server for (license_id, user_id, device_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id))
		if (query_set_count >= 2):
			return HttpResponse("Multiple license for same (user, device) tuple found. Something went wrong")

	except (KeyError, Offer.DoesNotExist):
		return HttpResponse("Offer isn't available for given license id")
	except (KeyError, OfferUserMap.DoesNotExist):
		return HttpResponse("Offer isn't available for given user id")
	except (KeyError, OfferAppMap.DoesNotExist):
		return HttpResponse("Offer isn't available for given app id")
