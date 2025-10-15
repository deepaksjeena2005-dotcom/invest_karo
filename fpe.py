def app_point_estimation():
    users = load_users()
    num_users = len(users)
    total_balance = 0
    total_portfolio_value = 0
    for email, user in users.items():
        total_balance += user.get("balance", 0)
        auto_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("shares", {}).items())
        petro_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("petroleum_shares", {}).items())
        steel_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("steel_shares", {}).items())
        gold_value = sum(shares * PRICES.get(company, 0) for company, shares in user.get("gold_shares", {}).items())
        total_portfolio_value += auto_value + petro_value + steel_value + gold_value

    total_money = total_balance + total_portfolio_value
    return {
        "num_users": num_users,
        "total_balance": total_balance,
        "total_portfolio_value": total_portfolio_value,
        "total_money_in_app": total_money
    }
