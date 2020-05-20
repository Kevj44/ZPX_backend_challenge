JSON_FIELD_RESULT = 'result'
JSON_FIELD_TRENDS = 'trends'
JSON_FIELD_DATE = 'date'
JSON_FIELD_AVG_PLAYER_COUNT = 'average_player_count'
JSON_FIELD_GROWTH = 'growth'

def FormatTrendResponse(query_results):
    json_response = { JSON_FIELD_RESULT: { JSON_FIELD_TRENDS: []} }
    games = {}
    for date, game_name, player_count in query_results:
        if game_name not in games:
            games[game_name] = [{                                   \
                JSON_FIELD_DATE: date,                              \
                JSON_FIELD_AVG_PLAYER_COUNT: int(player_count),     \
                JSON_FIELD_GROWTH: None                             \
            },]
        else:
            prev_avg_player_count = games[game_name][len(games[game_name]) - 1][JSON_FIELD_AVG_PLAYER_COUNT]
            if prev_avg_player_count == 0:
                games[game_name].append({                               \
                    JSON_FIELD_DATE: date,                              \
                    JSON_FIELD_AVG_PLAYER_COUNT: int(player_count),     \
                    JSON_FIELD_GROWTH: None                             \
                })
            else:
                games[game_name].append({                               \
                    JSON_FIELD_DATE: date,                              \
                    JSON_FIELD_AVG_PLAYER_COUNT: int(player_count),     \
                    JSON_FIELD_GROWTH: round(100 *                      \
                        (int(player_count) - prev_avg_player_count)     \
                        / prev_avg_player_count, 1)                     \
                })
    if (len(games) > 0):
        json_response[JSON_FIELD_RESULT][JSON_FIELD_TRENDS].append(games)
    return json_response, 200
