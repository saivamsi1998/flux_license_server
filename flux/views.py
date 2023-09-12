from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from django.utils import timezone
from .models import User, Offer, OfferAppMap, OfferUserMap, License, LicenseAppMap

import json
from . import scheduler

HEARTBEAT_TIME = 25 #secs
BUFFER_TIME = 5 #secs

def json_response(err_msg="", profile_status = ""):
	json_obj = {}
	if err_msg=="" or err_msg=="success":
		if profile_status != "":
			json_obj['profile_status'] = profile_status
		json_obj['status'] = "success"
	else:
		if profile_status != "":
			json_obj['profile_status'] = profile_status
		json_obj['status'] = "fail"
		json_obj['err_msg'] = err_msg
	return HttpResponse(json.dumps(json_obj))

@csrf_exempt 
def index(request):
	return HttpResponse("Hello, world. You're at the flux index.")

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
		return json_response("Offer isn't available for given (user_id, app_id)= (%s,%s)"%(user_id, app_id), "PROFILE_NOT_IN_POOL")
	offer = Offer.objects.get(pk = qs[0]['offer_id'])
	print("Using offer: %s for given (user_id, app_id)= (%s,%s)"%(str(offer),user_id, app_id))
	offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
	user = offerusermap_entry.user
	license_id = offer.license_id

	# license update
	query_set = License.objects.filter(offer = offer, user = user, device_id = device_id)
	query_set_count = query_set.count()

	if (query_set_count >= 2):
		return json_response("Multiple license for same (user, device) tuple found. Something went wrong", "PROFILE_DENIED")
	if (query_set_count  == 0):
		# check and allocate license and add license entry
		# mutex might be required when updating active_license_count
		if (offer.active_license_count >= offer.max_license_count):
			return json_response("Pool license limit reached", "PROFILE_POOL_LIMIT_REACHED")
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
	print("Created/Updated LicenseAppMap entry due to reg for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
	# TODO: Schedule next heartbeat check and remove entry
	scheduler.schedule_task(delay=HEARTBEAT_TIME+BUFFER_TIME,func=dereg_by_server_if_req,keyword_args={
				'user_id': user_id,
				'device_id': device_id,
				'app_id': app_id})
	return json_response("success", "PROFILE_AVAILABLE")

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
		return json_response("Offer isn't available for given (user_id, app_id)= (%s,%s)"%(user_id, app_id), "PROFILE_NOT_IN_POOL")
	offer = Offer.objects.get(pk = qs[0]['offer_id'])
	print("Using offer: %s for given (user_id, app_id)= (%s,%s)"%(str(offer),user_id, app_id))
	offerusermap_entry = offer.offerusermap_set.get(user__user_id = user_id)
	user = offerusermap_entry.user
	license_id = offer.license_id

	# license update
	query_set = License.objects.filter(offer = offer, user = user, device_id = device_id)
	query_set_count = query_set.count()

	if (query_set_count >= 2):
		return json_response("Multiple license for same (user, device) tuple found. Something went wrong", "PROFILE_DENIED")
	if (query_set_count  == 0):
		# check and allocate license and add license entry
		# mutex might be required when updating active_license_count
		if (offer.active_license_count >= offer.max_license_count):
			return json_response("Pool license limit reached", "PROFILE_POOL_LIMIT_REACHED")
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
	print("Created/Updated LicenseAppMap entry due to heartbeat for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
	scheduler.schedule_task(delay=HEARTBEAT+BUFFER_TIME+BUFFER_TIME,func=dereg_by_server_if_req,keyword_args={
				'user_id': user_id,
				'device_id': device_id,
				'app_id': app_id})
	return json_response("success", "PROFILE_AVAILABLE")

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
		# do nothing
		return json_response("Dereg call made for non existant license entry")
	elif (query_set_count  == 1):
		license = query_set[0]
		# Remove license app map entry
		try:
			licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
			licenseappmap_entry.delete()
			print("Removed LicenseAppMap entry due to dereg for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
		except (KeyError, LicenseAppMap.DoesNotExist):
			return json_response("Dereg call made for non existant licenceappmap entry")
		if (license.licenseappmap_set.count()==0):
			license = query_set[0]
			license.delete()
			if (offer.active_license_count == 0):
				return json_response("Trying to reduce active_license_count when current active_license_count=0. Something went wrong")
			offer.active_license_count -= 1
			offer.save()
			print("Released Pool License entry for (license_id, user_id, device_id) =  (%s,%s,%s)"%(license_id, user_id, device_id))
	return json_response("success")

def dereg_by_server_if_req(user_id, device_id, app_id):
	# verify if the user, app is part of the license
	print("dereg by server called")
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
		# do nothing
		return json_response("Dereg call made for non existant license entry")
	elif (query_set_count  == 1):
		license = query_set[0]
		# Remove license app map entry
		try:
			licenseappmap_entry = license.licenseappmap_set.get(app_id = app_id)
			if (licenseappmap_entry.last_active_time +  timezone.timedelta(seconds = HEARTBEAT_TIME) < timezone.now()):
				licenseappmap_entry.delete()
				print("Removed LicenseAppMap entry due to expired heartbeat for (license_id, user_id, device_id, app_id) =  (%s,%s,%s,%s)"%(license_id, user_id, device_id, app_id))
		except (KeyError, LicenseAppMap.DoesNotExist):
			return json_response("Dereg call made for non existant licenceappmap entry")
		if (license.licenseappmap_set.count()==0):
			license = query_set[0]
			license.delete()
			if (offer.active_license_count == 0):
				return json_response("Trying to reduce active_license_count when current active_license_count=0. Something went wrong")
			offer.active_license_count -= 1
			offer.save()
			print("Released Pool License entry for (license_id, user_id, device_id) =  (%s,%s,%s)"%(license_id, user_id, device_id))
	return json_response("success")

def get_admin_console(request):
	licenses = License.objects.all()
	offers = Offer.objects.all()
	return render(request,"flux/admin_console.html",context={'licenses': licenses, 'offers' : offers})