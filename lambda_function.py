import json
from datetime import datetime
import boto3
import time

from client.config_client import get_queue_config


def lambda_handler(event, context):
    print(event)
    startDate = int(time.time())
    
    while True:

        try:
    
            event_type = event['body']['eventType']
            cip = event['body']['data']['cip']
            
            
            #preguntar por los headers 
            try:
                PE_Signature = event['headers']['PE-Signature']
            except Exception as e:
                    print('no se tiene config PE-Signature')
            try:
                key = event['headers']['key']
            except Exception as e:
                print('no se tiene config key')
            status_code=''
                
            #PE         
                
            if  event_type == "cip.paid":
                print("Ingreso al cip.paid")
                frame_response = get_frame_response(cip)
                frame = json.loads(frame_response)
                dateExpiry = frame["data"]["dateExpiry"]
                
                expiry_date = valid_expiry_date(dateExpiry)
                
                if expiry_date ==  False:
                    response = {
                        "statusCode": 200,
                    }
                    return response
                else:
                    response = {
                        "statusCode": 400,
                        "message": "La fecha de expiracion caduco"
                    }
                
                
                    
                
        
        except Exception as e:
            
            print("General exception : "+ str(e))
            body = {"exception":str(e)}
            response = {
                "statusCode": 500,
                "body": json.dumps(body)
            }
        
        endDate = int(time.time())
        
        if endDate - startDate >= 15:
            response = {
                "statusCode": 400,
                "message": "Error de TimeOut"
            }
            break
    
    
            
            
    
    print("resultado final de la notificaion: ", response) 
    return response
    
    

def get_frame_response(cip):
    frame_response = None
    region = "us-east-1"
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table('transaction_messages')

    i = 0
    fails = 0
    for count in range(90):
        i = count + 1
        try:
            response = table.get_item(Key={"cip": cip})
            item = response["Item"]
            print(f'response: {item}')
            frame_response = item["content"]
            break
        except Exception:
            fails = fails + 1

        time.sleep(0.25)
    print('intents: ', str(i))
    print('fails: ', str(fails))
    print('frame_response: ', frame_response)
    
    return frame_response


def valid_expiry_date ( fecha ):
  format_string = '%Y-%m-%dT%H:%M:%S%z'
  date = datetime.strptime(fecha, format_string)
  year = date.strftime("%Y")
  month = date.strftime("%m")
  day = date.strftime("%d")
  hour = date.strftime("%H")
  minutes = date.strftime("%M")
  seconds = date.strftime("%S")
  z = date.strftime("%z")
  
  #fecha actual
  now = datetime.now().astimezone().replace(microsecond=0).isoformat()
  date_now = datetime.strptime(now, format_string)
  year_now = date_now.strftime("%Y")
  month_now = date_now.strftime("%m")
  day_now = date_now.strftime("%d")
  hour_now = date_now.strftime("%H")
  minutes_now = date_now.strftime("%M")
  seconds_now = date_now.strftime("%S")
  z_now = date_now.strftime("%z")


  #Variable para validar la fecha

  #Valid_date es Falso si la fecha aun no vence
  #Valid_date es Verdadero si la fecha ya venció
  valid_date = False

  valid_fecha = False

  #Comparamos la fecha

  #Comparamos el año
  if year_now <= year:
    print("El año no vence")
    if year_now == year:
      #Comparamos el mes
      if month_now <= month:
        print("El mes no vence")
        if month_now == month:
          #comparamos el día
          if day_now <= day:
            print("El dia no vence")
            if day_now == day:
              valid_fecha = True
          else:
            print("el dia vencio")
            valid_date = True
            return valid_date 
      else:
        print("el mes vencio")
        valid_date = True
        return valid_date
  else:
    print("El año vencio")
    valid_date = True
    return valid_date
  

  if valid_fecha == True:
    #Comparamos la hora
    #Horas homogeneas UTC +0000
    hour_utc = int(hour) - int((int(z)/100)) 
    hour_now_utc= int(hour_now) - int((int(z_now)/100))
    if hour_now_utc <= hour_utc:
      print("La hora no vence")
      if hour_now_utc == hour_utc:
        #Comparamos los minutos
        if minutes_now <= minutes:
          print("Los minutos no vencen")
          if minutes_now == minutes:
            #Comparamos los segundos
            if seconds_now <= seconds:
              print("Los segundos no vencen")
            else:
              print("Los segundos vencio")
              valid_date = True
              return valid_date
        else:
          print("Los minutos vencio")
          valid_date = True
          return valid_date
    else:
      print("La hora vencio")
      valid_date = True
      return valid_date

  return valid_date

