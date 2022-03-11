from datetime import datetime
from yahoo_fin import options
import numpy as np
import smtplib
import pandas_datareader as web
from black_scholes import BlackSholes
from UI import UserInterface

EMAIL = "your email address from which the email will be sent"
PASSWORD = "your password saved in environ"
user_interface = UserInterface()
EXPIRATION_DATE = (options.get_expiration_dates(user_interface.symbol.get()))

YIELD = "^TNX"
TODAY = datetime.now()
YESTERDAY = TODAY.replace(day=TODAY.day - 1)
ONE_YEAR_AGO = TODAY.replace(year=TODAY.year - 1)


# Calculating maturity input for BlackSholes
class MaturityDate:
    """ Calculates maturity for which checks whether the expiration date is today, and if it is so, takes the next
    expiration date in order to avoid maturity being negative"""

    def __init__(self, date_nr):
        self.date_nr = date_nr
        self.expiration_date = str((datetime.strptime(EXPIRATION_DATE[self.date_nr], "%B %d, %Y")).strftime("%m-%d-%Y"))
        self.maturity = (datetime.strptime(self.expiration_date, "%m-%d-%Y") - datetime.utcnow()).days / 365

    def check_maturity(self):
        if self.maturity < 0:
            self.expiration_date = str((datetime.strptime(EXPIRATION_DATE[self.date_nr + 1], "%B %d, %Y")).strftime
                                       ("%m-%d-%Y"))
            self.maturity = (datetime.strptime(self.expiration_date, "%m-%d-%Y") - datetime.utcnow()).days / 365
            return self.maturity
        else:
            return self.maturity

    def check_expiration_date(self):
        if self.maturity < 0:
            self.expiration_date = str(
                (datetime.strptime(EXPIRATION_DATE[self.date_nr + 1], "%B %d, %Y")).strftime("%m-%d-%Y"))
            return self.expiration_date
        else:
            return self.expiration_date


# Calculating interest rate input for BlackSholes formula
def interest_rate():
    """ Extracts the latest value of 10 years treasury yield. If the day of extraction is Monday, Sunday or Saturday,
     the day calculator is adjusted accordingly as the data is available only for weekdays """
    try:
        yesterday = TODAY.replace(day=TODAY.day - 1)
        rate = web.DataReader(YIELD, "yahoo", yesterday, TODAY)
        return round(rate.iloc[0]["Close"], 2)
    except KeyError:
        pass
    try:
        day_before_yesterday = TODAY.replace(day=TODAY.day - 2)
        rate = web.DataReader(YIELD, "yahoo", day_before_yesterday, TODAY)
        return round(rate.iloc[1]["Close"], 2)
    except KeyError:
        try:
            two_days_before_yesterday = TODAY.replace(day=TODAY.day - 3)
            rate = web.DataReader(YIELD, "yahoo", two_days_before_yesterday, TODAY)
            return round(rate.iloc[2]["Close"], 2)
        except KeyError:
            pass


interest = interest_rate()


def send_email(sent_to, info):
    """Function sends an email with the info about option prices if a person wants the results sent to their email"""
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(EMAIL, PASSWORD)
        connection.sendmail(from_addr=EMAIL,
                            to_addrs=sent_to,
                            msg=f"Subject:Options details\n\n{info}")


if user_interface.option.get() == "Call" and user_interface.detect:
    stock = user_interface.symbol.get()
    data_frame = web.DataReader(stock, "yahoo", ONE_YEAR_AGO, TODAY)
    data_frame = data_frame.sort_values(by="Date")
    data_frame = data_frame.dropna()
    data_frame = data_frame.assign(close_yesterday=data_frame.Close.shift(1))
    data_frame["returns"] = ((data_frame.Close - data_frame.close_yesterday) / data_frame.close_yesterday)
    volatility = np.sqrt(252) * data_frame["returns"].std()
    spot = data_frame["Close"].iloc[-1]

    call_price_diff = 0
    call_info = {"Quoted price": 0, "Black Scholes price": 0, "maturity": ""}
    for date in range(1, 2):
        call_options = options.get_calls(stock, EXPIRATION_DATE[date])
        call_strikes = call_options.loc[:, "Strike"].tolist()
        for strike in call_strikes:
            calculate_call_price = \
                BlackSholes(spot, strike, MaturityDate(date).check_maturity(), interest, volatility).call()
            quoted_call_price = (call_options[call_options["Strike"] == strike]).iloc[0]["Last Price"]
            prices_difference = round(abs(calculate_call_price - quoted_call_price), 2)
            if prices_difference > call_price_diff:
                call_price_diff = prices_difference
                call_info["Quoted price"] = quoted_call_price
                call_info["Black Scholes price"] = round(calculate_call_price, 2)
                call_info["maturity"] = MaturityDate(date).check_expiration_date()
    info = (f"The highest call price discrepancy for {stock} is: {call_price_diff}\n"
            f"Quoted price is {call_info['Quoted price']}\n"
            f"Black Scholes price is {call_info['Black Scholes price']}\nMaturity date is {call_info['maturity']}")
    print(info)
    if user_interface.email_yes.get() == 1:
        send_email(user_interface.email_text.get(), info)
        print(f"Email was sent to {user_interface.email_text.get()}")

elif user_interface.option.get() == "Put" and user_interface.detect:
    stock = user_interface.symbol.get()
    data_frame = web.DataReader(stock, "yahoo", ONE_YEAR_AGO, TODAY)
    data_frame = data_frame.sort_values(by="Date")
    data_frame = data_frame.dropna()
    data_frame = data_frame.assign(close_yesterday=data_frame.Close.shift(1))
    data_frame["returns"] = ((data_frame.Close - data_frame.close_yesterday) / data_frame.close_yesterday)
    volatility = np.sqrt(252) * data_frame["returns"].std()
    spot = data_frame["Close"].iloc[-1]

    put_price_diff = 0
    put_info = {"Quoted price": 0, "Black Scholes price": 0, "maturity": ""}
    for date in range(0, 1):
        put_options = options.get_puts(stock, EXPIRATION_DATE[date])
        put_strikes = put_options.loc[:, "Strike"].tolist()
        for strike in put_strikes:
            calculate_put_price = BlackSholes(spot, strike, MaturityDate(date).check_maturity(), interest,
                                              volatility).put()
            quoted_put_price = (put_options[put_options["Strike"] == strike]).iloc[0]["Last Price"]
            put_prices_difference = round(abs(calculate_put_price - quoted_put_price), 2)
            if put_prices_difference > put_price_diff:
                put_price_diff = put_prices_difference
                put_info["Quoted price"] = quoted_put_price
                put_info["Black Scholes price"] = round(calculate_put_price, 2)
                put_info["maturity"] = MaturityDate(date).check_expiration_date()

    info = (f"The highest put price discrepancy for {stock} is: {put_price_diff}\nQuoted price is "
            f"{put_info['Quoted price']} "
            f"\nBlack Scholes price is {put_info['Black Scholes price']}\nMaturity date is {put_info['maturity']}")
    print(info)
    if user_interface.email_yes.get() == 1:
        send_email(user_interface.email_text.get(), info)
        print(f"Email was sent to {user_interface.email_text.get()}")
