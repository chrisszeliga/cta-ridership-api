import os
from flask import Flask
from flask_restx import Api, Resource, reqparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from helpers import get_stats, get_stations, get_ridership_breakdown, get_weekday_ridership, get_stops_stats, \
get_stops_by_line_and_direction, get_yearly_ridership, get_monthly_ridership, get_stations_nearby

app = Flask(__name__)
api = Api(app, doc="/docs")  # Swagger UI

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/day"]   # Hard daily cap for now
)
limiter.init_app(app)


@api.route("/stats")
class Stats(Resource):
    @limiter.limit("20/minute")
    def get(self):
        return get_stats()


@api.route("/stations")
class Stations(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("station", type=str, required=True, help="Station name is required")

    @limiter.limit("20/minute")
    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()
        station_name = args["station"].strip()
        return get_stations(station_name)


@api.route("/stations/ridership_breakdown")
class RidershipBreakdown(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("station", type=str, required=True, help="Station name is required")

    @limiter.limit("20/minute")
    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()
        station_name = args["station"].strip()
        return get_ridership_breakdown(station_name)


@api.route("/stations/weekday_ridership")
class WeekdayRidership(Resource):
    @limiter.limit("20/minute")
    def get(self):
        return get_weekday_ridership()

 
@api.route("/stations/yearly_ridership")
class YearlyRidership(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("station", type=str, required=True, help="Station name is required")
    
    @limiter.limit("20/minute")
    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()
        station_name = args["station"].strip()
        return get_yearly_ridership(station_name)


@api.route("/stations/monthly_ridership")
class MonthlyRidership(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("station", type=str, required=True, help="Station name is required")
    parser.add_argument("year", type=int, required=True, help="Year is required")

    @limiter.limit("20/minute")
    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()
        station_name = args["station"].strip()
        year = args["year"]
        return get_monthly_ridership(station_name, year)


@api.route("/stations/nearby")
class NearbyStations(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("latitude", type=float, required=True, help="Latitude is required and must between 40 and 43.")
    parser.add_argument("longitude", type=float, required=True, help="Longitude is required and must between -88 and -87.")

    @api.expect(parser)
    @limiter.limit("20/minute")
    def get(self):
        args = self.parser.parse_args()
        lat = args["latitude"]
        lon = args["longitude"]
        return get_stations_nearby(lat, lon)
    

@api.route("/stops/stats")
class StopsByColor(Resource):
    @limiter.limit("20/minute")
    def get(self):
        return get_stops_stats()


@api.route("/stops/line")
class StopsByLineAndDirection(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("line_color", type=str, required=True, help="Line color is required")
    parser.add_argument("direction", type=str, required=True, help="Direction is required (N/S/E/W)")

    @limiter.limit("20/minute")
    @api.expect(parser)
    def get(self):
        args = self.parser.parse_args()
        line_color = args["line_color"].strip()
        direction = args["direction"].strip()
        return get_stops_by_line_and_direction(line_color, direction)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
