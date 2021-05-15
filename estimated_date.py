from datetime import timedelta, date
import random

class Get_Delivery_date():

    def get_Delivery_date(self):
        estimated = date.today() + timedelta(days=random.randint(3,7))
        estimated = estimated.strftime("%d %B, %Y")

        return(estimated)

        