from requests import get
from keys import api_key

def distance(origin, destination, mode="walking"):
    #origin = origin.replace(", ", "+")
    # origin = findAddress(origin)[0]
    #destination = destination.replace(", ", "+")

    url =  f"https://maps.googleapis.com/maps/api/distancematrix/json?origins=address:{origin}&destinations=place_id:{destination}&units=imperial&key={api_key}&mode={mode}"
    request = get(url)
    response = request.json()

    if "ft" in response["rows"][0]["elements"][0]["distance"]["text"]:
        return ("0.1 miles", response["rows"][0]["elements"][0]["duration"]["text"])
    
    return (response["rows"][0]["elements"][0]["distance"]["text"], response["rows"][0]["elements"][0]["duration"]["text"])

def pureDistance(origin, destination, mode="walking"):  #distace in miles
    origin = origin.replace(", ", "+")
    destination = destination.replace(", ", "+")

    url =  f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&units=imperial&key={api_key}&mode={mode}"
    request = get(url)
    response = request.json()

    return (float((response["rows"][0]["elements"][0]["distance"]["value"])*0.000189394))

def findAddress(address):

    # url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={address}&key={api_key}&types=address" 
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}" 
    request = get(url) # The API Request
    # response = request.json()["predictions"]
    # addresses = []
    # for i in response:
    #     addresses.append(i["place_id"])
    # return addresses

    response = request.json()["results"]
    if response != []:
        place_id =  response[0]["place_id"]
    else:
        place_id = ""
    places = [place_id]
    return places
    

def findCoords(place_id):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?place_id={place_id}&key={api_key}" 
    request = get(url) # The API Request
    response = request.json()["results"]
    coords = []
    for i in response:
        coords.append(i["geometry"]["location"]["lat"])
        coords.append(i["geometry"]["location"]["lng"])
        break
    return coords

def getStreetID(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"
    request = get(url) # The API Request
    data = request.json()["result"]["address_components"]
    postal_code = ""
    for component in data:
        if "postal_code" in component["types"]:
            postal_code = component["long_name"]
            break

    if postal_code != "":
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={postal_code}&key={api_key}"
        request = get(url) # The API Request
        data = request.json()["results"]
    
        for result in data:
            if "postal_code" in result["types"]:
                return result["place_id"]
        return None
    else:
        return None
        
def getAddressName(place_id):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?place_id={place_id}&key={api_key}"
    request = get(url) # The API Request
    data = request.json()["results"]
    for result in data:
        return result["formatted_address"]

if __name__ == "__main__":
    address1 = findAddress("4 Warren Cl Rhydyfelin")[0]
    address2 = findAddress("Sengenydd Rd")[0]

    #print(distance(address1, address2, "driving"))
    #print(pureDistance(address1, address2, "driving"))
