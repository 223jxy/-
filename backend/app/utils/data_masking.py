# 敏感数据脱敏工具

class DataMasking:
    """数据脱敏类"""
    
    @staticmethod
    def mask_email(email: str) -> str:
        """脱敏邮箱
        
        Args:
            email: 邮箱地址
            
        Returns:
            str: 脱敏后的邮箱
        """
        if not email:
            return email
        
        parts = email.split('@')
        if len(parts) != 2:
            return email
        
        username, domain = parts
        if len(username) <= 2:
            masked_username = username[0] + '*' * len(username[1:])
        else:
            masked_username = username[:2] + '*' * (len(username) - 2)
        
        return f"{masked_username}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """脱敏手机号
        
        Args:
            phone: 手机号
            
        Returns:
            str: 脱敏后的手机号
        """
        if not phone:
            return phone
        
        if len(phone) != 11:
            return phone
        
        return f"{phone[:3]}****{phone[-4:]}"
    
    @staticmethod
    def mask_id_card(id_card: str) -> str:
        """脱敏身份证号
        
        Args:
            id_card: 身份证号
            
        Returns:
            str: 脱敏后的身份证号
        """
        if not id_card:
            return id_card
        
        if len(id_card) != 18:
            return id_card
        
        return f"{id_card[:6]}********{id_card[-4:]}"
    
    @staticmethod
    def mask_name(name: str) -> str:
        """脱敏姓名
        
        Args:
            name: 姓名
            
        Returns:
            str: 脱敏后的姓名
        """
        if not name:
            return name
        
        if len(name) == 1:
            return name
        elif len(name) == 2:
            return f"{name[0]}*"
        else:
            return f"{name[0]}{'*' * (len(name) - 1)}"
    
    @staticmethod
    def mask_bank_card(bank_card: str) -> str:
        """脱敏银行卡号
        
        Args:
            bank_card: 银行卡号
            
        Returns:
            str: 脱敏后的银行卡号
        """
        if not bank_card:
            return bank_card
        
        if len(bank_card) < 8:
            return bank_card
        
        return f"{bank_card[:4]}****{bank_card[-4:]}"
    
    @staticmethod
    def mask_address(address: str) -> str:
        """脱敏地址
        
        Args:
            address: 地址
            
        Returns:
            str: 脱敏后的地址
        """
        if not address:
            return address
        
        if len(address) <= 6:
            return address
        
        return f"{address[:6]}****"

# 脱敏工具实例
data_masker = DataMasking()