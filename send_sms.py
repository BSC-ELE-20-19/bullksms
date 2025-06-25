import africastalking

username="sandbox"
api_key="atsk_a9c76a831fee0036f7bebd11e5b72961b965cf839779078cd908c7e9d1341400cd5be540"
africastalking.initialize(username,api_key)

sms = africastalking.SMS
def sending(messages, recipients):
    #recipients = ["+265994136905","+265888391093","+265883256151", "+265998137309"]
    #message = " Kusamalidwa kwa Soya pokolola: Mukazula umikani, wombani mosamala asaphwanyike, petani, sankhani, pakilani m’matumba abwino. Mukatero muzapha makwacha ndithu. ACADES"
    message = messages
    sender = "ACADES"
    try:
        response = sms.send(message, recipients, sender)
        print (response)
    except Exception as e:
        print (f'Houston, we have a problem: {e}')
def send(self):
    pass