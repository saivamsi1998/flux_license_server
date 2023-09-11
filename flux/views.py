from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone
from .models import User, Offer, OfferAppMap, OfferUserMap, License, LicenseAppMap

import json

HEARTBEAT_TIME = 60 #min
BUFFER_TIME = 5 #min

def json_response(err_msg="", require_profile_status = True):
	json_obj = {}
	if err_msg=="" or err_msg=="success":
		if require_profile_status:
			json_obj['profile_status'] = "PROFILE_AVAIALBLE"
		json_obj['status'] = "success"
		err_msg = ""
	else:
		if require_profile_status:
			json_obj['profile_status'] = "PROFILE_DENIED"
		json_obj['status'] = "fail"
		json_obj['err_msg'] = err_msg
	return HttpResponse(json.dumps(json_obj))

@csrf_exempt 
def index(request):
	return json_response("Hello, world. You're at the flux index.")

@csrf_exempt
def reg(request):
	user_id = request.POST["userId"]
	app_id = request.POST["nglAppId"]
	device_id = request.POST["deviceId"]

	# verify if the user, app is part of the license
	qs1 = OfferUserMap.objects.filter(user__user_id = user_id).values("offer_id")
	qs2 = OfferAppMap.objects.filter(app_id = app_id).values("offer_id")
	qs = qs1.intersection(qs2)
	if(qs.count()==0):
		return json_response("Offer isn't available for given (user_id, app_id)= (%s,%s)"%(user_id, app_id))
	offer = Offer.objects.get(pk = qs[0]['offer_id'])
	print("Using offer: %s for given (user_id, app_id)= (%s,%s)"%(str(offer),user_id, app_id))
	offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
	user = offerusermap_entry.user
	license_id = offer.license_id

	# license update
	query_set = License.objects.filter(offer = offer, user = user, device_id = device_id)
	query_set_count = query_set.count()

	if (query_set_count >= 2):
		return json_response("Multiple license for same (user, device) tuple found. Something went wrong")
	if (query_set_count  == 0):
		# check and allocate license and add license entry
		# mutex might be required when updating active_license_count
		if (offer.active_license_count >= offer.max_license_count):
			return json_response("Pool license limit reached")
		else:
			offer.active_license_count += 1
			offer.save()
			license = License.objects.create(offer = offer, user = user, device_id = device_id)
			print("Created Pool License entry for (license_id, user_id, device_id) = (%s,%s,%s)"%(license_id, user_id, device_id))
	elif (query_set_count  == 1):
		license = query_set[0]
	# add/update license app map entry
	try:
		licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
		licenseappmap_entry.last_active_time = timezone.now()
		licenseappmap_entry.save()
	except (KeyError, LicenseAppMap.DoesNotExist):
		license.licenseappmap_set.create(app_id = app_id, last_active_time = timezone.now())
	print("Created/Updated LicenseAppMap entry due to expired heartbeat for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
	# TODO: Schedule next heartbeat check and remove entry
	return json_response("success")

@csrf_exempt
def heartbeat(request):
	user_id = request.POST["userId"]
	app_id = request.POST["nglAppId"]
	device_id = request.POST["deviceId"]

	# verify if the user, app is part of the license
	qs1 = OfferUserMap.objects.filter(user__user_id = user_id).values("offer_id")
	qs2 = OfferAppMap.objects.filter(app_id = app_id).values("offer_id")
	qs = qs1.intersection(qs2)
	if(qs.count()==0):
		return json_response("Offer isn't available for given (user_id, app_id)= (%s,%s)"%(user_id, app_id))
	offer = Offer.objects.get(pk = qs[0]['offer_id'])
	print("Using offer: %s for given (user_id, app_id)= (%s,%s)"%(str(offer),user_id, app_id))
	offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
	user = offerusermap_entry.user
	license_id = offer.license_id

	# license update
	query_set = License.objects.filter(offer = offer, user = user, device_id = device_id)
	query_set_count = query_set.count()

	if (query_set_count >= 2):
		return json_response("Multiple license for same (user, device) tuple found. Something went wrong")
	if (query_set_count  == 0):
		# check and allocate license and add license entry
		# mutex might be required when updating active_license_count
		if (offer.active_license_count >= offer.max_license_count):
			return json_response("Pool license limit reached")
		else:
			offer.active_license_count += 1
			offer.save()
			license = License.objects.create(offer = offer, user = user, device_id = device_id)
			print("Created Pool License entry for (license_id, user_id, device_id) = (%s,%s,%s)"%(license_id, user_id, device_id))
	elif (query_set_count  == 1):
		license = query_set[0]
	# add/update license app map entry
	try:
		licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
		licenseappmap_entry.last_active_time = timezone.now()
		licenseappmap_entry.save()
	except (KeyError, LicenseAppMap.DoesNotExist):
		license.licenseappmap_set.create(app_id = app_id, last_active_time = timezone.now())
	print("Created/Updated LicenseAppMap entry due to expired heartbeat for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
	# TODO: Schedule next heartbeat check and remove entry
	return json_response("success")

@csrf_exempt
def dereg(request):
	user_id = request.POST["userId"]
	app_id = request.POST["nglAppId"]
	device_id = request.POST["deviceId"]

	# verify if the user, app is part of the license
	qs1 = OfferUserMap.objects.filter(user__user_id = user_id).values("offer_id")
	qs2 = OfferAppMap.objects.filter(app_id = app_id).values("offer_id")
	qs = qs1.intersection(qs2)
	if(qs.count()==0):
		return json_response("Offer isn't available for given (user_id, app_id)= (%s,%s)"%(user_id, app_id), False)
	offer = Offer.objects.get(pk = qs[0]['offer_id'])
	print("Using offer: %s for given (user_id, app_id)= (%s,%s)"%(str(offer),user_id, app_id))
	offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
	user = offerusermap_entry.user
	license_id = offer.license_id

	# license update
	query_set = License.objects.filter(offer = offer, user = user, device_id = device_id)
	query_set_count = query_set.count()

	if (query_set_count >= 2):
		return json_response("Multiple license for same (user, device) tuple found. Something went wrong", False)
	if (query_set_count  == 0):
		# do nothing
		return json_response("Dereg call made for non existant license entry", False)
	elif (query_set_count  == 1):
		license = query_set[0]
		# Remove license app map entry
		try:
			licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
			licenseappmap_entry.delete()
			print("Removed LicenseAppMap entry due to dereg for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
		except (KeyError, LicenseAppMap.DoesNotExist):
			return json_response("Dereg call made for non existant licenceappmap entry", False)
		if (license.licenseappmap_set.count()==0):
			license = query_set[0]
			license.delete()
			if (offer.active_license_count == 0):
				return json_response("Trying to reduce active_license_count when current active_license_count=0. Something went wrong", False)
			offer.active_license_count -= 1
			offer.save()
			print("Released Pool License entry for (license_id, user_id, device_id) =  (%s,%s,%s)"%(license_id, user_id, device_id))
	return json_response("success", False)

def dereg_by_server_if_req(request, user_id, device_id, app_id):
	# verify if the user, app is part of the license
	qs1 = OfferUserMap.objects.filter(user__user_id = user_id).values("offer_id")
	qs2 = OfferAppMap.objects.filter(app_id = app_id).values("offer_id")
	qs = qs1.intersection(qs2)
	if(qs.count()==0):
		return json_response("Offer isn't available for given (user_id, app_id)= (%s,%s)"%(user_id, app_id), False)
	offer = Offer.objects.get(pk = qs[0]['offer_id'])
	print("Using offer: %s for given (user_id, app_id)= (%s,%s)"%(str(offer),user_id, app_id))
	offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
	user = offerusermap_entry.user
	license_id = offer.license_id

	# license update
	query_set = License.objects.filter(offer = offer, user = user, device_id = device_id)
	query_set_count = query_set.count()

	if (query_set_count >= 2):
		return json_response("Multiple license for same (user, device) tuple found. Something went wrong", False)
	if (query_set_count  == 0):
		# do nothing
		return json_response("Dereg call made for non existant license entry", False)
	elif (query_set_count  == 1):
		license = query_set[0]
		# Remove license app map entry
		try:
			licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
			if (licenseappmap_entry.last_active_time +  timezone.timedelta(minutes = HEARTBEAT) < timezone.now()):
				licenseappmap_entry.delete()
				print("Removed LicenseAppMap entry due to expired heartbeat for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
		except (KeyError, LicenseAppMap.DoesNotExist):
			return json_response("Dereg call made for non existant licenceappmap entry", False)
		if (license.licenseappmap_set.count()==0):
			license = query_set[0]
			license.delete()
			if (offer.active_license_count == 0):
				return json_response("Trying to reduce active_license_count when current active_license_count=0. Something went wrong", False)
			offer.active_license_count -= 1
			offer.save()
			print("Released Pool License entry for (license_id, user_id, device_id) =  (%s,%s,%s)"%(license_id, user_id, device_id))
	return json_response("Success", False)