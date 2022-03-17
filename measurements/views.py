from django.shortcuts import redirect, render, get_object_or_404
from .models import Measurement
from .forms import MeasurementForm
from geopy.geocoders import Nominatim
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
from geopy.distance import geodesic
import folium


def calculate_distance(request):
    distance = None
    destination = None
    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurements')

    # works in live server
    # ip_ = get_ip_address(request)
    # print(ip_)
    ip = '162.254.206.227'
    country, city, lat, lon = get_geo(ip)

    location = geolocator.geocode(city)

    # ip location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)

    # folium map
    m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon), zoom_start=8)

    # location marker
    folium.Marker([l_lat, l_lon], tooltip='Click here for more', popup=city['city'], icon=folium.Icon(color='blue')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        # destination coordinates
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)

        # distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        # folium map
        m = folium.Map(width=800, height=500, location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))

        # location marker
        folium.Marker([l_lat, l_lon], tooltip='Click here for more', popup=city['city'], icon=folium.Icon(color='blue')).add_to(m)

        # destination marker
        folium.Marker([d_lat, d_lon], tooltip='Click here for more', popup=destination, icon=folium.Icon(color='red', icon='cloud')).add_to(m)

        # draw the line between location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=1, color='blue')
        m.add_child(line)

        instance.location = location
        instance.distance = distance
        instance.save()
        # return redirect(calculate_distance)

    m = m._repr_html_()

    context = {
        'distance': distance,
        'destination': destination,
        'form': form,
        'map': m,
    }
    return render(request, 'measurements/main.html', context)
