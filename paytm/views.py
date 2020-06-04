from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .checksum import verify_checksum
from msg.models import Message
from .models import Transaction

# Create your views here.

@csrf_exempt
def handleresponse(request):
	#paytm will send response here
	form = request.POST
	response_dict = {}
	for i in form.keys():
		response_dict[i] = form[i]
		if i == 'CHECKSUMHASH':
			checksum = form[i]
	verify = verify_checksum(response_dict, settings.MKEY ,checksum)
	if verify:
		if response_dict['RESPCODE'] == '01':
			#transaction success
			#Message.objects.filter(order_id=response_dict['ORDERID']).update(status=True)
			msg = Message.objects.get(order_id=response_dict['ORDERID'])
			msg.status = True
			msg.save()
			Transaction.objects.create(msg=msg,
			 tstatus=response_dict['RESPMSG'],txnid=response_dict['TXNID'],
			 txnamount=response_dict['TXNAMOUNT'],order_id=response_dict['ORDERID'],
			 bank_name=response_dict['BANKNAME'],bank_txnid=response_dict['BANKTXNID'],
			 tdate=response_dict['TXNDATE'],)
			return render(request,'paytm/success.html',{'response':response_dict})


	msg = Message.objects.get(order_id=response_dict['ORDERID'])
	Transaction.objects.create(msg=msg,
			 tstatus=response_dict['RESPMSG'],txnid=response_dict['TXNID'],
			 txnamount=response_dict['TXNAMOUNT'],order_id=response_dict['ORDERID'],)
			 
	return render(request,'paytm/failure.html',{'response':response_dict})