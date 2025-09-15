current_annot.set_color(color)

# Shade area between entry price and current price
# Remove old fills safely
for coll in ax.collections:
    coll.remove()

prices_arr = np.array(prices)
if prices_arr[-1] > ENTRY_PRICE:
    ax.fill_between(times, ENTRY_PRICE, prices_arr, where=(prices_arr >= ENTRY_PRICE),
                    color='green', alpha=0.1)
elif prices_arr[-1] < ENTRY_PRICE:
    ax.fill_between(times, prices_arr, ENTRY_PRICE, where=(prices_arr <= ENTRY_PRICE),
                    color='red', alpha=0.1)

return line_price, entry_annot, current_annot, pl_annot
