from app.models import Hotel

CITY_PROPERTIES: dict[str, list[str]] = {
    "Hyderabad": [
        "Grand Hyderabad Hotel",
        "Charminar Heritage Stay",
        "Banjara Hills Suites",
        "Hitech City Business Inn",
        "Gachibowli Tech Residency",
        "Jubilee Hills Boutique Hotel",
        "Madhapur Central Stay",
        "Kondapur Garden Hotel",
        "Begumpet Airport Hotel",
        "Secunderabad Club Inn",
        "Film Nagar View Stay",
        "Hitec Skyline Suites",
        "Necklace Road Lake Hotel",
        "Ameerpet City Center Hotel",
        "Kukatpally Metro Inn",
        "Shamshabad Transit Hotel",
        "Old City Haveli Stay",
        "Financial District Tower Hotel",
    ],
    "Bangalore": [
        "Bangalore Palace Hotel",
        "MG Road Boutique Hotel",
        "Whitefield Business Inn",
        "Indiranagar Garden Suites",
        "Koramangala Loft Hotel",
        "Electronic City Tech Stay",
        "UB City Luxury Hotel",
        "Brigade Road Central Inn",
        "Hebbal Lake View Hotel",
        "Jayanagar Family Residency",
        "Marathahalli Transit Hotel",
        "Yelahanka Airport Stay",
        "Malleshwaram Heritage Inn",
        "Sarjapur Road Suites",
        "Banashankari City Hotel",
        "Manyata Tech Park Inn",
        "Cubbon Park View Stay",
        "Silk Board Business Hotel",
    ],
    "Mumbai": [
        "Marine Drive Suites",
        "Gateway Mumbai Hotel",
        "Bandra Sea View Stay",
        "Andheri Business Inn",
        "Colaba Harbour Hotel",
        "Juhu Beach Residency",
        "Powai Lake View Hotel",
        "Lower Parel Loft Suites",
        "BKC Corporate Hotel",
        "Dadar City Center Inn",
        "Worli Sea Face Stay",
        "Santacruz Airport Hotel",
        "Thane Creek View Inn",
        "Navi Mumbai Business Stay",
        "Goregaon Film City Hotel",
        "Nariman Point Tower Hotel",
        "Versova Beach Suites",
        "Kurla Transit Residency",
    ],
    "New Delhi": [
        "Connaught Place Inn",
        "Lotus Temple View Hotel",
        "Aerocity Transit Hotel",
        "Karol Bagh City Stay",
        "Saket Select Suites",
        "Dwarka Sector Hotel",
        "Chanakyapuri Diplomatic Inn",
        "Hauz Khas Village Stay",
        "Kashmere Gate Heritage Hotel",
        "Nehru Place Business Inn",
        "Rajouri Garden Residency",
        "India Gate View Hotel",
        "Vasant Kunj Suites",
        "Mayur Vihar Family Inn",
        "Paharganj Traveller Hotel",
        "Greater Kailash Boutique Stay",
        "Rohini City Center Hotel",
        "Noida Border Business Hotel",
    ],
    "Chennai": [
        "Marina Beach Residency",
        "Nungambakkam Grand",
        "T Nagar Shopping Inn",
        "Adyar Garden Hotel",
        "OMR IT Corridor Stay",
        "Anna Nagar Family Suites",
        "Egmore Heritage Hotel",
        "Velachery Tech Inn",
        "Mylapore Temple Stay",
        "Guindy Race Course Hotel",
        "ECR Beach View Suites",
        "Tambaram Transit Hotel",
        "Porur Bypass Inn",
        "Teynampet Central Stay",
        "Besant Nagar Shore Hotel",
        "Koyambedu City Hotel",
        "Mahabalipuram Coast Stay",
        "Chennai Airport Business Inn",
    ],
    "Goa": [
        "Calangute Beach Resort",
        "Panaji Riverside Hotel",
        "Baga Shore Suites",
        "Anjuna Cliff Stay",
        "Candolim Palm Resort",
        "Miramar Bay Hotel",
        "Vagator Sunset Inn",
        "Colva Beach Residency",
        "Palolem South Goa Stay",
        "Mapusa Market Hotel",
        "Old Goa Heritage Inn",
        "Dona Paula View Suites",
        "Morjim Quiet Beach Stay",
        "Vasco Port Transit Hotel",
        "Fort Aguada Cliff Hotel",
        "Arambol Hippie Stay",
        "Margao City Center Inn",
        "Sinquerim Beach Resort",
    ],
    "Jaipur": [
        "Pink City Palace Hotel",
        "Amber Fort View Stay",
        "C Scheme Boutique Hotel",
        "MI Road Heritage Inn",
        "Jal Mahal Lake Hotel",
        "Bani Park Residency",
        "Vaishali Nagar Suites",
        "Raja Park Family Inn",
        "Hawa Mahal View Stay",
        "Tonk Road Business Hotel",
        "Amer Village Haveli",
        "Malviya Nagar City Hotel",
        "Jaipur Airport Transit Inn",
        "Johari Bazaar Heritage Stay",
        "Mansarovar Garden Hotel",
        "Civil Lines Club Inn",
        "Sitapura Industrial Stay",
        "Nahargarh Hill View Hotel",
    ],
    "Pune": [
        "Koregaon Park Stay",
        "Hinjewadi Tech Hotel",
        "FC Road Boutique Inn",
        "Viman Nagar Suites",
        "Kothrud Family Residency",
        "Magarpatta City Hotel",
        "Shivajinagar Central Stay",
        "Hadapsar Business Inn",
        "Baner Skyline Hotel",
        "Camp Area Heritage Stay",
        "Wakad IT Corridor Inn",
        "Kalyani Nagar Suites",
        "Sinhagad Road Hotel",
        "Pune Airport Transit Stay",
        "Deccan Gymkhana Inn",
        "Aundh Garden Hotel",
        "Pimpri Chinchwad Business Stay",
        "Lonavala Gateway Hotel",
    ],
    "Kolkata": [
        "Park Street Heritage",
        "Salt Lake Business Inn",
        "Howrah River View Hotel",
        "New Town Rajarhat Stay",
        "Esplanade Central Hotel",
        "Alipore Garden Suites",
        "Gariahat City Residency",
        "Dum Dum Airport Inn",
        "Victoria Memorial View Stay",
        "Ballygunge Boutique Hotel",
        "Science City Transit Hotel",
        "Camac Street Suites",
        "Rajarhat Eco Park Inn",
        "Shyambazar Heritage Stay",
        "New Market City Hotel",
        "Tollygunge Club Inn",
        "Sealdah Station Stay",
        "Princep Ghat Riverside Hotel",
    ],
    "Kochi": [
        "Fort Kochi Harbour Inn",
        "Marine Drive Kochi Hotel",
        "Edappally City Stay",
        "Kakkanad InfoPark Inn",
        "Mattancherry Heritage Hotel",
        "Vyttila Junction Suites",
        "Ernakulam Central Residency",
        "Cherai Beach Stay",
        "Willingdon Island Hotel",
        "Kaloor Metro Inn",
        "Fort Kochi Synagogue Stay",
        "Infopark Business Hotel",
        "Thevara Backwater Inn",
        "Nedumbassery Airport Stay",
        "MG Road Kochi Suites",
        "Palluruthy Harbour Hotel",
        "Broadway Market Inn",
        "Kumbalangi Village Stay",
    ],
}

_RATINGS = [4.5, 4.2, 4.3, 4.6, 4.1, 4.7, 4.4, 4.8, 4.0, 4.3, 4.5, 4.2, 4.6, 4.4, 4.1, 4.7, 4.3, 4.5]


def _build_hotels() -> list[Hotel]:
    hotels: list[Hotel] = []
    hotel_id = 1
    for city, names in CITY_PROPERTIES.items():
        for index, name in enumerate(names):
            hotels.append(
                Hotel(
                    id=hotel_id,
                    name=name,
                    city=city,
                    rating=_RATINGS[index % len(_RATINGS)],
                )
            )
            hotel_id += 1
    return hotels


_INITIAL_HOTELS = _build_hotels()

hotels: dict[int, Hotel] = {}
_next_id = 1


def _sync_next_id() -> None:
    global _next_id
    _next_id = max(hotels.keys(), default=0) + 1


def reset_data() -> None:
    hotels.clear()
    for hotel in _INITIAL_HOTELS:
        hotels[hotel.id] = hotel.model_copy()
    _sync_next_id()


def next_id() -> int:
    global _next_id
    value = _next_id
    _next_id += 1
    return value


reset_data()
