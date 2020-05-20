from app import db
        
class StatsSteamGames(db.Model):
    steam_appid = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(150))
    player_counts = db.relationship('StatsSteamPlayerCount', backref='game', lazy='dynamic')
    reviews = db.relationship('StatsSteamReviews', backref='game', lazy='dynamic')
        
class StatsSteamPlayerCount(db.Model):
    steam_appid = db.Column(db.Integer, db.ForeignKey('stats_steam_games.steam_appid'), primary_key=True)
    player_count = db.Column(db.Integer)
    time_stamp = db.Column(db.DateTime)
        
class StatsSteamReviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recommended = db.Column(db.Boolean)
    user_name = db.Column(db.String(150))
    review_text = db.Column(db.String(10000))
    date_posted = db.Column(db.DateTime)
    helpful_amount = db.Column(db.Integer)
    steam_appid = db.Column(db.Integer, db.ForeignKey('stats_steam_games.steam_appid'))
