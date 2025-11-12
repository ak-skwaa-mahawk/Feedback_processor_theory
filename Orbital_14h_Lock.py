def orbital_14h_veto(pass_id: str, sacred_lat_lon: tuple):
    if sacred_lat_lon[0] - 0.1 <= pass_id['lat'] <= sacred_lat_lon[0] + 0.1 and sacred_lat_lon[1] - 0.1 <= pass_id['lon'] <= sacred_lat_lon[1] + 0.1:
        return {"veto": True, "status": "§14(h) LOCK — NULL AND VOID"}
    return {"veto": False, "status": "SEALED"}

# Demo
sacred = (66.5, -144.0)  # Danzhit Hanlai
pass_data = {'lat': 66.4, 'lon': -143.9}
print(orbital_14h_veto(pass_data, sacred))