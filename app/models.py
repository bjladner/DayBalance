from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from calendar import day_abbr, month_name
from app import db, login, balance_calendar


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    start_date = db.Column(db.Date, nullable=False)
    start_balance = db.Column(db.Float, nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def weekday_headers(self):
        weekday_headers = []
        for weekday in balance_calendar.iterweekdays():
            weekday_headers.append(day_abbr[weekday])
        return weekday_headers
    
    def month_name(self, month):
        return month_name[month]

    def month_days(self, year, month):
        return balance_calendar.itermonthdates(year, month)

    def month_starting_balance(self, year, month):
        month_start_day = list(balance_calendar.itermonthdates(year, month))[0]
        month_start_balance = 0

        prev_transactions = Transaction.query.filter(
            Transaction.user_id == self.id,
            Transaction.date >= self.start_date, 
            Transaction.date < month_start_day
        )

        for transaction in prev_transactions:
            if transaction.income == True:
                month_start_balance = month_start_balance + transaction.amount
            else:
                month_start_balance = month_start_balance - transaction.amount
        return month_start_balance

    def month_transactions(self, year, month):
        month_start_day = list(balance_calendar.itermonthdates(year, month))[0]
        month_end_day = list(balance_calendar.itermonthdates(year, month))[-1]
        return Transaction.query.filter(
            Transaction.user_id == self.id,
            Transaction.date >= month_start_day,
            Transaction.date <= month_end_day,
        )


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    income = db.Column(db.Boolean, default=False)
#    is_recurring = db.Column(db.Boolean, default=False)
#    freq = db.Column(db.String(8))  # DAILY, WEEKLY, MONTHLY, YEARLY
#    interval = db.Column(db.Integer)  # interval betweek frequency
#    wkst = db.Column(db.Integer)  # MO, TU, WE or int  # affects WEEKLY frequency
#    count = db.Column(db.Integer)  # number of occurrences (Cannot be used with until)
#    until = db.Column(db.Date, nullable=False)  # recurrence end date (Cannot be used with count)
#    transaction_exceptions = db.relationship('TransactionException', backref='transaction', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Transaction {}>'.format(self.title)

#    def add_recurrence():
#        self.is_recurring = True
#        pass
    
#    def return_transactions_between(self, start=self.date, end)
#        dates = rruleset()
#        dates.rrule(rrule(freq=self.freq, dtstart=self.date, interval=self.interval, wkst=self.wkst, count=self.count, until=self.until))
#        
#        exceptions = TransactionException.query.filter(
#            TransactionException.user_id == self.id,
#            TransactionException.date >= start, 
#            TransactionException.date <= end,
#        )
#        
#        for exception in exceptions:
#            if exception.delete:
#                dates.exdate(exception.date)
#            else:
#                dates.rdate(exception.date)
#
#        return dates.between(before=start, after=end, inc=True)

#class TransactionException(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    date = db.Column(db.DateTime, nullable=False)
#    delete = db.Column(db.Boolean)
#    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
