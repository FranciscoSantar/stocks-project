

def get_difference_percentage(purchase_price:float, current_price:float) -> str:
        percentage = ((current_price-purchase_price) / purchase_price) * 100
        final_percentage = "{:.3g}%".format(percentage)
        return final_percentage