# 品相系数
CONDITION_COEFFICIENTS = {
    "A1": 0.9,  # 九成新
    "A2": 0.8,  # 八五新
    "B": 0.7,   # 八成新
    "C": 0.5    # 五成新以上
}

# 流通系数（根据图书类型和市场需求调整）
CIRCULATION_COEFFICIENTS = {
    "教材": 1.0,
    "备考资料": 1.2,
    "课外读物": 0.8,
    "其他": 0.9
}

# 计算图书价格
def calculate_price(original_price, condition, category):
    """
    根据原价、品相和分类计算图书价格
    公式：价格 = 原价 × 品相系数 × 流通系数
    """
    condition_coefficient = CONDITION_COEFFICIENTS.get(condition, 0.5)
    circulation_coefficient = CIRCULATION_COEFFICIENTS.get(category, 0.9)
    
    price = original_price * condition_coefficient * circulation_coefficient
    # 四舍五入到小数点后两位
    return round(price, 2)

# 计算卖家保证金
def calculate_deposit(price):
    """
    根据图书价格计算卖家保证金
    公式：保证金 = 价格 × 20%，最低10元，最高200元
    """
    deposit = price * 0.2
    deposit = max(10, min(deposit, 200))
    # 四舍五入到整数
    return round(deposit)

# 计算纠纷仲裁费用
def calculate_arbiration_fee(price):
    """
    根据图书价格计算纠纷仲裁费用
    公式：仲裁费用 = 价格 × 5%，最低5元，最高50元
    """
    fee = price * 0.05
    fee = max(5, min(fee, 50))
    # 四舍五入到整数
    return round(fee)

# 验证图书价格是否合理
def validate_price(price, original_price, condition, category):
    """
    验证用户输入的价格是否合理
    合理范围：计算价格的80%-120%
    """
    calculated_price = calculate_price(original_price, condition, category)
    min_price = calculated_price * 0.8
    max_price = calculated_price * 1.2
    
    return min_price <= price <= max_price, min_price, max_price