from flask import Response, json
from app import app, db
from app.models import StatsSteamReviews, StatsSteamGames, StatsSteamPlayerCount
from app.helpers import FormatTrendResponse
from flask_restful import Api, Resource, reqparse
from sqlalchemy import func, case
from datetime import datetime, timedelta
import math, time

api = Api(app)

###############################################################################

BASE_API_ADDRESS = '127.0.0.1:5000'
REVIEWS_API_ADDRESS = '/ZPXsteamdata/api/v1.0/reviews'
VOTES_API_ADDRESS = '/ZPXsteamdata/api/v1.0/reports/votes'
TRENDS_API_ADDRESS = '/ZPXsteamdata/api/v1.0/reports/trends'

JSON_FIELD_RESULT = 'result'
JSON_FIELD_REVIEWS = 'reviews'
JSON_FIELD_USER_NAME = 'user_name'
JSON_FIELD_DATE_POSTED = 'date_posted'
JSON_FIELD_HELPFUL_AMOUNT = 'helpful_amount'
JSON_FIELD_REVIEW_TEXT = 'review_text'
JSON_FIELD_RECOMMENDED = 'recommended'
JSON_FIELD_GAME_NAME = 'game_name'
JSON_FIELD_POS_VOTES = 'positive_votes'
JSON_FIELD_NEG_VOTES = 'negative_votes'
JSON_FIELD_VOTES = 'votes'
REQ_PARAM_PER_PAGE = 'per_page'
REQ_PARAM_PAGE = 'page'
REQ_PARAM_START_DATE = 'start_date'
REQ_PARAM_END_DATE = 'end_date'
REQ_PARAM_TIMESPAN = 'timespan'
DAILY_TIMESPAN = 'daily'

ERROR_MESSAGE_FIELD = 'message'

###############################################################################

class ReviewsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(REQ_PARAM_PER_PAGE, type = int, default = 10)
        self.reqparse.add_argument(REQ_PARAM_PAGE, type = int, default = 1)
        self.reqparse.add_argument(REQ_PARAM_START_DATE, type = str)
        self.reqparse.add_argument(REQ_PARAM_END_DATE, type = str)
        super(ReviewsAPI, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()

        # Set per_page between 1 and 20 (default 10).
        per_page = 20 if int(args[REQ_PARAM_PER_PAGE]) > 20 else int(args[REQ_PARAM_PER_PAGE])
        per_page = per_page if per_page > 0 else 10

        # Do not accept page values below 1.
        page = args[REQ_PARAM_PAGE] if args[REQ_PARAM_PAGE] > 1 else 1

        # Search for reviews between dates.
        if args[REQ_PARAM_START_DATE] != None and args[REQ_PARAM_END_DATE] != None:
            try:
                start_date = datetime.strptime(args[REQ_PARAM_START_DATE], '%Y-%m-%d')
                end_date = datetime.strptime(args[REQ_PARAM_END_DATE], '%Y-%m-%d')
            except ValueError:
                return { ERROR_MESSAGE_FIELD: 'Incorrect date format. Format should be YYYY-MM-DD.' }, 400
            day_delta = (end_date-start_date).days
            end_date += timedelta(days=1)   # Include end_date in the results.
            if day_delta <= 0:
                return { ERROR_MESSAGE_FIELD: 'end_date must be set to a later date than start_date.' }, 400
            query_results = StatsSteamReviews.query.with_entities(                                      \
                StatsSteamGames.display_name,                                                           \
                StatsSteamReviews.user_name,                                                            \
                StatsSteamReviews.date_posted,                                                          \
                StatsSteamReviews.helpful_amount,                                                       \
                StatsSteamReviews.review_text,                                                          \
                StatsSteamReviews.recommended)                                                          \
                .join(StatsSteamGames, StatsSteamReviews.steam_appid == StatsSteamGames.steam_appid)    \
                .filter(StatsSteamReviews.date_posted.between(start_date, end_date))                    \
                .order_by(StatsSteamReviews.date_posted)
            num_pages = math.ceil(query_results.count()/per_page)

        # List reviews, sorted by latest.
        else:
            query_results = StatsSteamReviews.query.with_entities(                                      \
                StatsSteamGames.display_name,                                                           \
                StatsSteamReviews.user_name,                                                            \
                StatsSteamReviews.date_posted,                                                          \
                StatsSteamReviews.helpful_amount,                                                       \
                StatsSteamReviews.review_text,                                                          \
                StatsSteamReviews.recommended)                                                          \
                .join(StatsSteamGames, StatsSteamReviews.steam_appid == StatsSteamGames.steam_appid)    \
                .order_by(StatsSteamReviews.date_posted.desc())
            num_pages = math.ceil(query_results.count()/per_page)
        if (num_pages > 0 and page > num_pages):
            return { ERROR_MESSAGE_FIELD: 'Page {0} does not exist. The last page number available is {1}.'.format(page, num_pages)}, 400
        reviews = query_results.limit(per_page).offset(per_page*(page-1)).all()

        # Format JSON response.
        reviews_json = []
        for game_name, user_name, date, helpful, review, recomended in reviews:
                reviews_json.append({                     \
                    JSON_FIELD_GAME_NAME: game_name,    \
                    JSON_FIELD_USER_NAME: user_name,    \
                    JSON_FIELD_DATE_POSTED: str(date),  \
                    JSON_FIELD_HELPFUL_AMOUNT: helpful, \
                    JSON_FIELD_REVIEW_TEXT: review,     \
                    JSON_FIELD_RECOMMENDED: recomended, })

        # Set JSON response.
        json_response = Response(json.dumps({ JSON_FIELD_RESULT: { JSON_FIELD_REVIEWS: reviews_json }}), status=200, mimetype='application/json')

        # Add Link header to take care of pagination.
        links = ''
        if (page > 1):
            links += '<{0}?per_page={1}>; rel="first", '.format(BASE_API_ADDRESS + REVIEWS_API_ADDRESS, per_page)
        if (page > 2):
            links += '<{0}?per_page={1}&page={2}>; rel="prev", '.format(BASE_API_ADDRESS + REVIEWS_API_ADDRESS, per_page, page-1)
        if (page < num_pages - 1):
            links += '<{0}?per_page={1}&page={2}>; rel="next", '.format(BASE_API_ADDRESS + REVIEWS_API_ADDRESS, per_page, page + 1)
        if (page < num_pages):
            links += '<{0}?per_page={1}&page={2}>; rel="last", '.format(BASE_API_ADDRESS + REVIEWS_API_ADDRESS, per_page, num_pages)
        if len(links) > 0:
            links = links[0:len(links) - 2]
            json_response.headers['Link'] = links

        return json_response
        


class VotesAPI(Resource):
    def get(self):
            games_json = []
            query_results = StatsSteamReviews.query.with_entities(                                      \
                StatsSteamGames.display_name,                                                           \
                func.count(case([(StatsSteamReviews.recommended == True, 1)])),                         \
                func.count(case([(StatsSteamReviews.recommended == False, 1)])))                        \
                .join(StatsSteamGames, StatsSteamReviews.steam_appid == StatsSteamGames.steam_appid)    \
                .group_by(StatsSteamGames.display_name)                                                 \
                .all()
            for game_name, pos_votes, neg_votes in query_results:
                games_json.append({                     \
                    JSON_FIELD_GAME_NAME: game_name,    \
                    JSON_FIELD_POS_VOTES: pos_votes,    \
                    JSON_FIELD_NEG_VOTES: neg_votes, })
            return { JSON_FIELD_RESULT: { JSON_FIELD_VOTES: games_json }}, 200
            


class TrendsAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(REQ_PARAM_TIMESPAN, type = str, default=DAILY_TIMESPAN)
        self.reqparse.add_argument(REQ_PARAM_START_DATE, type = str, required=True)
        self.reqparse.add_argument(REQ_PARAM_END_DATE, type = str, required=True)
        super(TrendsAPI, self).__init__()
        
    def get(self):
        args = self.reqparse.parse_args()
        trends_json = []
        try:
            start_date = datetime.strptime(args[REQ_PARAM_START_DATE], '%Y-%m-%d')
            end_date = datetime.strptime(args[REQ_PARAM_END_DATE], '%Y-%m-%d')
        except ValueError:
            return { ERROR_MESSAGE_FIELD: 'Incorrect date format. Format should be YYYY-MM-DD.' }, 400
        day_delta = (end_date-start_date).days
        end_date += timedelta(days=1)   # Include end_date in the results.
        if day_delta <= 0:
            return { ERROR_MESSAGE_FIELD: 'end_date must be set to a later date than start_date.' }, 400
        if args[REQ_PARAM_TIMESPAN] == 'yearly':
            query_results = StatsSteamPlayerCount.query.with_entities(                                      \
                func.date(StatsSteamPlayerCount.time_stamp, 'start of year'),                               \
                StatsSteamGames.display_name,                                                               \
                func.avg(StatsSteamPlayerCount.player_count))                                               \
                .filter(StatsSteamPlayerCount.time_stamp.between(                                           \
                    func.date(start_date, 'start of year'),                                                 \
                    func.date(end_date, '+1 year', 'start of year')))                                       \
                .join(StatsSteamGames, StatsSteamPlayerCount.steam_appid == StatsSteamGames.steam_appid)    \
                .group_by(StatsSteamGames.display_name)                                                     \
                .group_by(func.date(StatsSteamPlayerCount.time_stamp, 'start of year'))                     \
                .all()
            return FormatTrendResponse(query_results)
        elif args[REQ_PARAM_TIMESPAN] == 'weekly':
            query_results = StatsSteamPlayerCount.query.with_entities(                                      \
                func.date(StatsSteamPlayerCount.time_stamp, 'weekday 1', '-7 days'),                        \
                StatsSteamGames.display_name,                                                               \
                func.avg(StatsSteamPlayerCount.player_count))                                               \
                .filter(StatsSteamPlayerCount.time_stamp.between(                                           \
                    func.date(start_date, 'weekday 1'),                                                     \
                    func.date(end_date, 'weekday 1')))                                                      \
                .join(StatsSteamGames, StatsSteamPlayerCount.steam_appid == StatsSteamGames.steam_appid)    \
                .group_by(StatsSteamGames.display_name)                                                     \
                .group_by(func.date(StatsSteamPlayerCount.time_stamp, 'weekday 0'))                         \
                .all()
            return FormatTrendResponse(query_results)
        else:
            query_results = StatsSteamPlayerCount.query.with_entities(                                      \
                func.date(StatsSteamPlayerCount.time_stamp),                                                \
                StatsSteamGames.display_name,                                                               \
                func.avg(StatsSteamPlayerCount.player_count))                                               \
                .filter(StatsSteamPlayerCount.time_stamp.between(start_date, end_date))                     \
                .join(StatsSteamGames, StatsSteamPlayerCount.steam_appid == StatsSteamGames.steam_appid)    \
                .group_by(StatsSteamGames.display_name)                                                     \
                .group_by(func.date(StatsSteamPlayerCount.time_stamp))                                      \
                .all()
            return FormatTrendResponse(query_results)
                
api.add_resource(ReviewsAPI, REVIEWS_API_ADDRESS, endpoint = 'reviews')
api.add_resource(VotesAPI, VOTES_API_ADDRESS, endpoint = 'votes')
api.add_resource(TrendsAPI, TRENDS_API_ADDRESS, endpoint = 'trends')
