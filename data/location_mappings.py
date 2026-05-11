"""
Subreddit → Location mapping for geo-visualization.
Maps subreddit names to city/country with lat/lng coordinates.
"""

SUBREDDIT_LOCATIONS = {
    # Global / General
    "worldnews": {"city": "Global", "country": "World", "lat": 0, "lng": 0},

    # United States
    "news": {"city": "Washington DC", "country": "USA", "lat": 38.9072, "lng": -77.0369},
    "politics": {"city": "Washington DC", "country": "USA", "lat": 38.9072, "lng": -77.0369},
    "uspolitics": {"city": "Washington DC", "country": "USA", "lat": 38.9072, "lng": -77.0369},
    "nyc": {"city": "New York", "country": "USA", "lat": 40.7128, "lng": -74.0060},
    "newyork": {"city": "New York", "country": "USA", "lat": 40.7128, "lng": -74.0060},
    "losangeles": {"city": "Los Angeles", "country": "USA", "lat": 34.0522, "lng": -118.2437},
    "la": {"city": "Los Angeles", "country": "USA", "lat": 34.0522, "lng": -118.2437},
    "chicago": {"city": "Chicago", "country": "USA", "lat": 41.8781, "lng": -87.6298},
    "houston": {"city": "Houston", "country": "USA", "lat": 29.7604, "lng": -95.3698},
    "phoenix": {"city": "Phoenix", "country": "USA", "lat": 33.4484, "lng": -112.0740},
    "philadelphia": {"city": "Philadelphia", "country": "USA", "lat": 39.9526, "lng": -75.1652},
    "sanfrancisco": {"city": "San Francisco", "country": "USA", "lat": 37.7749, "lng": -122.4194},
    "bayarea": {"city": "San Francisco", "country": "USA", "lat": 37.7749, "lng": -122.4194},
    "sandiego": {"city": "San Diego", "country": "USA", "lat": 32.7157, "lng": -117.1611},
    "dallas": {"city": "Dallas", "country": "USA", "lat": 32.7767, "lng": -96.7970},
    "austin": {"city": "Austin", "country": "USA", "lat": 30.2672, "lng": -97.7431},
    "boston": {"city": "Boston", "country": "USA", "lat": 42.3601, "lng": -71.0589},
    "seattle": {"city": "Seattle", "country": "USA", "lat": 47.6062, "lng": -122.3321},
    "seattlewa": {"city": "Seattle", "country": "USA", "lat": 47.6062, "lng": -122.3321},
    "portland": {"city": "Portland", "country": "USA", "lat": 45.5152, "lng": -122.6784},
    "denver": {"city": "Denver", "country": "USA", "lat": 39.7392, "lng": -104.9903},
    "miami": {"city": "Miami", "country": "USA", "lat": 25.7617, "lng": -80.1918},
    "atlanta": {"city": "Atlanta", "country": "USA", "lat": 33.7490, "lng": -84.3880},
    "lasvegas": {"city": "Las Vegas", "country": "USA", "lat": 36.1699, "lng": -115.1398},
    "vegas": {"city": "Las Vegas", "country": "USA", "lat": 36.1699, "lng": -115.1398},
    "detroit": {"city": "Detroit", "country": "USA", "lat": 42.3314, "lng": -83.0458},
    "minneapolis": {"city": "Minneapolis", "country": "USA", "lat": 44.9778, "lng": -93.2650},
    "orlando": {"city": "Orlando", "country": "USA", "lat": 28.5383, "lng": -81.3792},
    "nashville": {"city": "Nashville", "country": "USA", "lat": 36.1627, "lng": -86.7816},
    "saltlakecity": {"city": "Salt Lake City", "country": "USA", "lat": 40.7608, "lng": -111.8910},
    "raleigh": {"city": "Raleigh", "country": "USA", "lat": 35.7796, "lng": -78.6382},
    "charlotte": {"city": "Charlotte", "country": "USA", "lat": 35.2271, "lng": -80.8431},

    # United Kingdom
    "unitedkingdom": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
    "ukpolitics": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
    "london": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
    "manchester": {"city": "Manchester", "country": "UK", "lat": 53.4808, "lng": -2.2426},
    "birmingham": {"city": "Birmingham", "country": "UK", "lat": 52.4862, "lng": -1.8904},
    "edinburgh": {"city": "Edinburgh", "country": "UK", "lat": 55.9533, "lng": -3.1883},
    "glasgow": {"city": "Glasgow", "country": "UK", "lat": 55.8642, "lng": -4.2518},
    "liverpool": {"city": "Liverpool", "country": "UK", "lat": 53.4084, "lng": -2.9916},

    # Canada
    "canada": {"city": "Ottawa", "country": "Canada", "lat": 45.4215, "lng": -75.6972},
    "canadapolitics": {"city": "Ottawa", "country": "Canada", "lat": 45.4215, "lng": -75.6972},
    "toronto": {"city": "Toronto", "country": "Canada", "lat": 43.6532, "lng": -79.3832},
    "vancouver": {"city": "Vancouver", "country": "Canada", "lat": 49.2827, "lng": -123.1207},
    "montreal": {"city": "Montreal", "country": "Canada", "lat": 45.5017, "lng": -73.5673},
    "calgary": {"city": "Calgary", "country": "Canada", "lat": 51.0447, "lng": -114.0719},
    "ottawa": {"city": "Ottawa", "country": "Canada", "lat": 45.4215, "lng": -75.6972},

    # Australia
    "australia": {"city": "Canberra", "country": "Australia", "lat": -35.2809, "lng": 149.1300},
    "sydney": {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lng": 151.2093},
    "melbourne": {"city": "Melbourne", "country": "Australia", "lat": -37.8136, "lng": 144.9631},
    "brisbane": {"city": "Brisbane", "country": "Australia", "lat": -27.4698, "lng": 153.0251},
    "perth": {"city": "Perth", "country": "Australia", "lat": -31.9505, "lng": 115.8605},

    # India
    "india": {"city": "New Delhi", "country": "India", "lat": 28.6139, "lng": 77.2090},
    "delhi": {"city": "New Delhi", "country": "India", "lat": 28.6139, "lng": 77.2090},
    "mumbai": {"city": "Mumbai", "country": "India", "lat": 19.0760, "lng": 72.8777},
    "bangalore": {"city": "Bangalore", "country": "India", "lat": 12.9716, "lng": 77.5946},
    "kolkata": {"city": "Kolkata", "country": "India", "lat": 22.5726, "lng": 88.3639},
    "chennai": {"city": "Chennai", "country": "India", "lat": 13.0827, "lng": 80.2707},
    "hyderabad": {"city": "Hyderabad", "country": "India", "lat": 17.3850, "lng": 78.4867},
    "pune": {"city": "Pune", "country": "India", "lat": 18.5204, "lng": 73.8567},

    # China
    "china": {"city": "Beijing", "country": "China", "lat": 39.9042, "lng": 116.4074},
    "beijing": {"city": "Beijing", "country": "China", "lat": 39.9042, "lng": 116.4074},
    "shanghai": {"city": "Shanghai", "country": "China", "lat": 31.2304, "lng": 121.4737},
    "guangzhou": {"city": "Guangzhou", "country": "China", "lat": 23.1291, "lng": 113.2644},
    "shenzhen": {"city": "Shenzhen", "country": "China", "lat": 22.5431, "lng": 114.0579},

    # Japan
    "japan": {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lng": 139.6503},
    "tokyo": {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lng": 139.6503},
    "osaka": {"city": "Osaka", "country": "Japan", "lat": 34.6937, "lng": 135.5023},
    "japanlife": {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lng": 139.6503},

    # South Korea
    "korea": {"city": "Seoul", "country": "South Korea", "lat": 37.5665, "lng": 126.9780},
    "southkorea": {"city": "Seoul", "country": "South Korea", "lat": 37.5665, "lng": 126.9780},
    "seoul": {"city": "Seoul", "country": "South Korea", "lat": 37.5665, "lng": 126.9780},

    # Brazil
    "brasil": {"city": "Brasilia", "country": "Brazil", "lat": -15.7975, "lng": -47.8919},
    "saopaulo": {"city": "Sao Paulo", "country": "Brazil", "lat": -23.5505, "lng": -46.6333},
    "riodejaneiro": {"city": "Rio de Janeiro", "country": "Brazil", "lat": -22.9068, "lng": -43.1729},

    # Germany
    "germany": {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lng": 13.4050},
    "berlin": {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lng": 13.4050},
    "munich": {"city": "Munich", "country": "Germany", "lat": 48.1351, "lng": 11.5820},
    "hamburg": {"city": "Hamburg", "country": "Germany", "lat": 53.5511, "lng": 9.9937},
    "frankfurt": {"city": "Frankfurt", "country": "Germany", "lat": 50.1109, "lng": 8.6821},

    # France
    "france": {"city": "Paris", "country": "France", "lat": 48.8566, "lng": 2.3522},
    "paris": {"city": "Paris", "country": "France", "lat": 48.8566, "lng": 2.3522},
    "lyon": {"city": "Lyon", "country": "France", "lat": 45.7640, "lng": 4.8357},

    # Italy
    "italy": {"city": "Rome", "country": "Italy", "lat": 41.9028, "lng": 12.4964},
    "rome": {"city": "Rome", "country": "Italy", "lat": 41.9028, "lng": 12.4964},
    "milan": {"city": "Milan", "country": "Italy", "lat": 45.4642, "lng": 9.1900},

    # Spain
    "spain": {"city": "Madrid", "country": "Spain", "lat": 40.4168, "lng": -3.7038},
    "madrid": {"city": "Madrid", "country": "Spain", "lat": 40.4168, "lng": -3.7038},
    "barcelona": {"city": "Barcelona", "country": "Spain", "lat": 41.3874, "lng": 2.1686},

    # Russia
    "russia": {"city": "Moscow", "country": "Russia", "lat": 55.7558, "lng": 37.6173},
    "moscow": {"city": "Moscow", "country": "Russia", "lat": 55.7558, "lng": 37.6173},

    # Middle East
    "dubai": {"city": "Dubai", "country": "UAE", "lat": 25.2048, "lng": 55.2708},
    "uae": {"city": "Dubai", "country": "UAE", "lat": 25.2048, "lng": 55.2708},
    "israel": {"city": "Jerusalem", "country": "Israel", "lat": 31.7683, "lng": 35.2137},
    "saudiarabia": {"city": "Riyadh", "country": "Saudi Arabia", "lat": 24.7136, "lng": 46.6753},
    "iran": {"city": "Tehran", "country": "Iran", "lat": 35.6892, "lng": 51.3890},
    "turkey": {"city": "Istanbul", "country": "Turkey", "lat": 41.0082, "lng": 28.9784},
    "istanbul": {"city": "Istanbul", "country": "Turkey", "lat": 41.0082, "lng": 28.9784},

    # Africa
    "southafrica": {"city": "Johannesburg", "country": "South Africa", "lat": -26.2041, "lng": 28.0473},
    "nigeria": {"city": "Lagos", "country": "Nigeria", "lat": 6.5244, "lng": 3.3792},
    "kenya": {"city": "Nairobi", "country": "Kenya", "lat": -1.2921, "lng": 36.8219},
    "egypt": {"city": "Cairo", "country": "Egypt", "lat": 30.0444, "lng": 31.2357},
    "ethiopia": {"city": "Addis Ababa", "country": "Ethiopia", "lat": 9.0320, "lng": 38.7469},

    # Southeast Asia
    "singapore": {"city": "Singapore", "country": "Singapore", "lat": 1.3521, "lng": 103.8198},
    "malaysia": {"city": "Kuala Lumpur", "country": "Malaysia", "lat": 3.1390, "lng": 101.6869},
    "indonesia": {"city": "Jakarta", "country": "Indonesia", "lat": -6.2088, "lng": 106.8456},
    "thailand": {"city": "Bangkok", "country": "Thailand", "lat": 13.7563, "lng": 100.5018},
    "vietnam": {"city": "Hanoi", "country": "Vietnam", "lat": 21.0278, "lng": 105.8342},
    "philippines": {"city": "Manila", "country": "Philippines", "lat": 14.5995, "lng": 120.9842},

    # Mexico / Latin America
    "mexico": {"city": "Mexico City", "country": "Mexico", "lat": 19.4326, "lng": -99.1332},
    "argentina": {"city": "Buenos Aires", "country": "Argentina", "lat": -34.6037, "lng": -58.3816},
    "chile": {"city": "Santiago", "country": "Chile", "lat": -33.4489, "lng": -70.6693},
    "colombia": {"city": "Bogota", "country": "Colombia", "lat": 4.7110, "lng": -74.0721},
    "peru": {"city": "Lima", "country": "Peru", "lat": -12.0464, "lng": -77.0428},

    # Europe - Other
    "sweden": {"city": "Stockholm", "country": "Sweden", "lat": 59.3293, "lng": 18.0686},
    "stockholm": {"city": "Stockholm", "country": "Sweden", "lat": 59.3293, "lng": 18.0686},
    "norway": {"city": "Oslo", "country": "Norway", "lat": 59.9139, "lng": 10.7522},
    "denmark": {"city": "Copenhagen", "country": "Denmark", "lat": 55.6761, "lng": 12.5683},
    "netherlands": {"city": "Amsterdam", "country": "Netherlands", "lat": 52.3676, "lng": 4.9041},
    "amsterdam": {"city": "Amsterdam", "country": "Netherlands", "lat": 52.3676, "lng": 4.9041},
    "belgium": {"city": "Brussels", "country": "Belgium", "lat": 50.8503, "lng": 4.3517},
    "switzerland": {"city": "Zurich", "country": "Switzerland", "lat": 47.3769, "lng": 8.5417},
    "austria": {"city": "Vienna", "country": "Austria", "lat": 48.2082, "lng": 16.3738},
    "poland": {"city": "Warsaw", "country": "Poland", "lat": 52.2297, "lng": 21.0122},
    "ukraine": {"city": "Kyiv", "country": "Ukraine", "lat": 50.4501, "lng": 30.5234},
    "ireland": {"city": "Dublin", "country": "Ireland", "lat": 53.3498, "lng": -6.2603},
    "dublin": {"city": "Dublin", "country": "Ireland", "lat": 53.3498, "lng": -6.2603},
    "portugal": {"city": "Lisbon", "country": "Portugal", "lat": 38.7223, "lng": -9.1393},
    "greece": {"city": "Athens", "country": "Greece", "lat": 37.9838, "lng": 23.7275},
    "czech": {"city": "Prague", "country": "Czech Republic", "lat": 50.0755, "lng": 14.4378},
    "finland": {"city": "Helsinki", "country": "Finland", "lat": 60.1699, "lng": 24.9384},

    # Pakistan
    "pakistan": {"city": "Islamabad", "country": "Pakistan", "lat": 33.6844, "lng": 73.0479},
    "karachi": {"city": "Karachi", "country": "Pakistan", "lat": 24.8607, "lng": 67.0011},
    "lahore": {"city": "Lahore", "country": "Pakistan", "lat": 31.5204, "lng": 74.3587},
    "islamabad": {"city": "Islamabad", "country": "Pakistan", "lat": 33.6844, "lng": 73.0479},

    # Bangladesh
    "bangladesh": {"city": "Dhaka", "country": "Bangladesh", "lat": 23.8103, "lng": 90.4125},

    # Sri Lanka
    "srilanka": {"city": "Colombo", "country": "Sri Lanka", "lat": 6.9271, "lng": 79.8612},

    # Nepal
    "nepal": {"city": "Kathmandu", "country": "Nepal", "lat": 27.7172, "lng": 85.3240},

    # New Zealand
    "newzealand": {"city": "Wellington", "country": "New Zealand", "lat": -41.2865, "lng": 174.7762},
    "auckland": {"city": "Auckland", "country": "New Zealand", "lat": -36.8509, "lng": 174.7645},
}

URL_HINT_LOCATIONS = {
    "bbc.com": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
    "bbc.co.uk": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
    "cnn.com": {"city": "Atlanta", "country": "USA", "lat": 33.7490, "lng": -84.3880},
    "nytimes.com": {"city": "New York", "country": "USA", "lat": 40.7128, "lng": -74.0060},
    "washingtonpost.com": {"city": "Washington DC", "country": "USA", "lat": 38.9072, "lng": -77.0369},
    "reuters.com": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
    "aljazeera.com": {"city": "Doha", "country": "Qatar", "lat": 25.2854, "lng": 51.5310},
    "theguardian.com": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
    "foxnews.com": {"city": "New York", "country": "USA", "lat": 40.7128, "lng": -74.0060},
    "apnews.com": {"city": "New York", "country": "USA", "lat": 40.7128, "lng": -74.0060},
    "bloomberg.com": {"city": "New York", "country": "USA", "lat": 40.7128, "lng": -74.0060},
    "wsj.com": {"city": "New York", "country": "USA", "lat": 40.7128, "lng": -74.0060},
    "ndtv.com": {"city": "New Delhi", "country": "India", "lat": 28.6139, "lng": 77.2090},
    "timesofindia.com": {"city": "New Delhi", "country": "India", "lat": 28.6139, "lng": 77.2090},
    "hindustantimes.com": {"city": "New Delhi", "country": "India", "lat": 28.6139, "lng": 77.2090},
    "dawn.com": {"city": "Karachi", "country": "Pakistan", "lat": 24.8607, "lng": 67.0011},
    "tribune.com.pk": {"city": "Lahore", "country": "Pakistan", "lat": 31.5204, "lng": 74.3587},
    "dw.com": {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lng": 13.4050},
    "france24.com": {"city": "Paris", "country": "France", "lat": 48.8566, "lng": 2.3522},
    "rt.com": {"city": "Moscow", "country": "Russia", "lat": 55.7558, "lng": 37.6173},
    "sputniknews.com": {"city": "Moscow", "country": "Russia", "lat": 55.7558, "lng": 37.6173},
    "xinhuanet.com": {"city": "Beijing", "country": "China", "lat": 39.9042, "lng": 116.4074},
    "scmp.com": {"city": "Hong Kong", "country": "China", "lat": 22.3193, "lng": 114.1694},
    "abc.net.au": {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lng": 151.2093},
    "cbc.ca": {"city": "Toronto", "country": "Canada", "lat": 43.6532, "lng": -79.3832},
    "elpais.com": {"city": "Madrid", "country": "Spain", "lat": 40.4168, "lng": -3.7038},
    "lemonde.fr": {"city": "Paris", "country": "France", "lat": 48.8566, "lng": 2.3522},
    "spiegel.de": {"city": "Hamburg", "country": "Germany", "lat": 53.5511, "lng": 9.9937},
    "ansa.it": {"city": "Rome", "country": "Italy", "lat": 41.9028, "lng": 12.4964},
    "japantimes.co.jp": {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lng": 139.6503},
    "koreatimes.co.kr": {"city": "Seoul", "country": "South Korea", "lat": 37.5665, "lng": 126.9780},
    "straitstimes.com": {"city": "Singapore", "country": "Singapore", "lat": 1.3521, "lng": 103.8198},
}


def get_location_for_subreddit(subreddit: str):
    if not subreddit:
        return None
    return SUBREDDIT_LOCATIONS.get(subreddit.lower())


def get_location_for_url(url: str):
    if not url:
        return None
    for domain, loc in URL_HINT_LOCATIONS.items():
        if domain in url:
            return loc
    return None
