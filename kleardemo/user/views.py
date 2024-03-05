from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from os import environ
from .models import USER_COLLECTION, ADDRESS_COLLECTION, WALLET_COLLECTION
from .validators import validate_password, check_email, EmailNotValidError, create_secure_password
from blockcypher import get_address_full, constants, create_wallet_from_address, simple_spend
import datetime


TOKEN=environ.get('token')

@api_view(http_method_names=['POST'])
def create_user(request):

    data = request.data

    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']

    if data['password_1']==data['password_2']:
        password= data['password_1']  
    else:
        return Response(data={'content':'Passwords does not match.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    if not validate_password(password=password):

        return Response(data={'content':'Password do not follow the password policy.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    hash_password = create_secure_password(password=password)

    checked_email = check_email(email=email, check_deliverability=True)

    if checked_email == EmailNotValidError:

        return Response(data={'content': str(checked_email)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    if USER_COLLECTION.find_one({
        "email":checked_email
    }):

        return Response(data={'content': "Email already exist."}, status=status.HTTP_406_NOT_ACCEPTABLE)

    try:
        USER_COLLECTION.insert_one(
            {
                'first_name':first_name,
                'last_name':last_name,
                'password':hash_password,
                'email':checked_email,
                'is_active':False
            }
        )

        return Response(data={'content':'User created, check email for verfication link.'}, status=status.HTTP_201_CREATED)

    except Exception as e:

        return Response(data={'content': str(e)}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
@api_view(http_method_names=['POST'])
def login(request):

    body = request.data

    email = body['email']
    password = body['password']

    checked_email = check_email(email=email)

    if checked_email == EmailNotValidError:

        return Response(data={'content': str(checked_email)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    hash_password = create_secure_password(password=password)

    if not USER_COLLECTION.find_one({'email':checked_email, 'password': hash_password}):

        return Response(data={'content':'Wrong Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(data='Successfully logged in!', status=status.HTTP_200_OK)

@api_view(http_method_names=['GET'])
def search_address(request):
    params=request.GET

    address = params['address']

    thirty_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)

    data = ADDRESS_COLLECTION.find_one({"address":address, "querytime": {"$gte":thirty_minutes_ago}})  

    if not data :

        for symbol in constants.COIN_SYMBOL_LIST:
            try:
                data = get_address_full(address=address, api_key=TOKEN, coin_symbol=symbol)
                data['querytime']= datetime.datetime.utcnow()
                ADDRESS_COLLECTION.replace_one(filter={"address":address}, replacement=data) if ADDRESS_COLLECTION.find_one({"address":address}) != None else ADDRESS_COLLECTION.insert_one(data)
                break
            except:
                continue

    if '_id' in data.keys():
        data.pop('_id') 

    return Response(data=data, status=status.HTTP_200_OK)

@api_view(http_method_names=['POST'])
def create_wallet(request):
    body = request.data
    email = body['email']
    address = body['address']
    name = body['walletName']

    for symbol in constants.COIN_SYMBOL_LIST:

        try:
            create_wallet_from_address(wallet_name=name, address=address, api_key=TOKEN, coin_symbol=symbol)

        except:
            continue

        WALLET_COLLECTION.insert_one({"email":email, "name": name, "address":address, "coin_symbol": symbol})

        break

    return Response(data={"content": "successful"}, status=status.HTTP_201_CREATED)

@api_view(http_method_names=['GET'])
def get_wallet_info(request):

    params= request.GET

    email = params['email']

    wallets = WALLET_COLLECTION.find({"email":email})
    data = []

    for wallet in wallets:
        info = get_address_full(address=wallet['address'], api_key=TOKEN, coin_symbol=wallet['coin_symbol'])
        info['name']= wallet['name']
        info['coin_symbol']= wallet['coin_symbol']
        data.append(info)

    print(data)
    return Response(data=data)

@api_view(http_method_names=['POST'])
def make_payment_api(request):

    body = request.data

    coin_symbol = body["coin_symbol"]
    private_key = body["private_key"]
    recipient_address = body["recipient_address"]
    amount = int(body["amount"])

    transaction_id = simple_spend(from_privkey=private_key, to_address=recipient_address, to_satoshis=amount, api_key=TOKEN, coin_symbol=coin_symbol)
    return Response(data={"content": transaction_id}, status=status.HTTP_202_ACCEPTED)