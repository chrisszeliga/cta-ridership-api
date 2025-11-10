# CTA Ridership API

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live-brightgreen)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)

A RESTful API providing Chicago Transit Authority (CTA) ridership and station data. Built with **Python**, **Flask-RESTX**, and **SQLite**.

The API is hosted and publicly available at: [https://cta-ridership-api.fly.dev](https://cta-ridership-api.fly.dev)

Swagger UI documentation: [https://cta-ridership-api.fly.dev/docs](https://cta-ridership-api.fly.dev/docs)

---

## API Endpoints

| Endpoint                        | Method | Description                                                                                         |
| ------------------------------- | ------ | --------------------------------------------------------------------------------------------------- |
| `/stats`                        | GET    | Returns general statistics about CTA stations, stops, and ridership.                                |
| `/stations`                     | GET    | Search for stations by name (supports partial matches).                                             |
| `/stations/ridership_breakdown` | GET    | Get ridership totals and percentages for a station by day type (weekday, Saturday, Sunday/holiday). |
| `/stations/weekday_ridership`   | GET    | Total ridership per weekday across all stations.                                                    |
| `/stations/yearly_ridership`    | GET    | Yearly ridership for a specific station.                                                            |
| `/stations/monthly_ridership`   | GET    | Monthly ridership for a specific station and year.                                                  |
| `/stations/nearby`              | GET    | Get stations within a ~1 mile radius of a given latitude and longitude.                             |
| `/stops/stats`                  | GET    | Stops statistics by line color and direction.                                                       |
| `/stops/line`                   | GET    | List stops for a given line color and direction.                                                    |

---

## Notes
- The API uses a read-only SQLite database (CTA2_L_daily_ridership.db).
- Rate limiting is applied (20 requests/minute per IP) to prevent abuse.
