from typing import Any, Dict, List, Optional, Union
import re

# 输入验证工具

class InputValidator:
    """输入验证类"""
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 1, max_length: int = 255, allow_empty: bool = False) -> bool:
        """验证字符串
        
        Args:
            value: 要验证的值
            min_length: 最小长度
            max_length: 最大长度
            allow_empty: 是否允许为空
            
        Returns:
            bool: 是否有效
        """
        if value is None:
            return allow_empty
        
        if not isinstance(value, str):
            return False
        
        if allow_empty and value == "":
            return True
        
        return min_length <= len(value) <= max_length
    
    @staticmethod
    def validate_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> bool:
        """验证整数
        
        Args:
            value: 要验证的值
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            bool: 是否有效
        """
        if value is None:
            return False
        
        if not isinstance(value, int):
            return False
        
        if min_value is not None and value < min_value:
            return False
        
        if max_value is not None and value > max_value:
            return False
        
        return True
    
    @staticmethod
    def validate_float(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None) -> bool:
        """验证浮点数
        
        Args:
            value: 要验证的值
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            bool: 是否有效
        """
        if value is None:
            return False
        
        if not isinstance(value, (int, float)):
            return False
        
        if min_value is not None and value < min_value:
            return False
        
        if max_value is not None and value > max_value:
            return False
        
        return True
    
    @staticmethod
    def validate_email(value: Any) -> bool:
        """验证邮箱
        
        Args:
            value: 要验证的值
            
        Returns:
            bool: 是否有效
        """
        if value is None or not isinstance(value, str):
            return False
        
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, value))
    
    @staticmethod
    def validate_username(value: Any) -> bool:
        """验证用户名
        
        Args:
            value: 要验证的值
            
        Returns:
            bool: 是否有效
        """
        if value is None or not isinstance(value, str):
            return False
        
        # 用户名只能包含字母、数字、下划线，长度在3-20之间
        username_pattern = r"^[a-zA-Z0-9_]{3,20}$"
        return bool(re.match(username_pattern, value))
    
    @staticmethod
    def validate_password(value: Any) -> bool:
        """验证密码
        
        Args:
            value: 要验证的值
            
        Returns:
            bool: 是否有效
        """
        if value is None or not isinstance(value, str):
            return False
        
        # 密码长度至少8位，包含至少一个大写字母、一个小写字母和一个数字
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
        return bool(re.match(password_pattern, value))
    
    @staticmethod
    def validate_isbn(value: Any) -> bool:
        """验证ISBN
        
        Args:
            value: 要验证的值
            
        Returns:
            bool: 是否有效
        """
        if value is None or not isinstance(value, str):
            return False
        
        # ISBN-10或ISBN-13
        isbn_pattern = r"^(?:ISBN(?:-13)?:?\ )?(?=[0-9]{13}$|(?=(?:[0-9]+[-\ ]){4})[-\ 0-9]{17}$)97[89][-\ ]?[0-9]{1,5}[-\ ]?[0-9]+[-\ ]?[0-9]+[-\ ]?[0-9]$"
        return bool(re.match(isbn_pattern, value))
    
    @staticmethod
    def validate_book_condition(value: Any) -> bool:
        """验证图书品相
        
        Args:
            value: 要验证的值
            
        Returns:
            bool: 是否有效
        """
        valid_conditions = ["A1", "A2", "B", "C"]
        return value in valid_conditions
    
    @staticmethod
    def validate_input(data: Dict[str, Any], rules: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """验证输入数据
        
        Args:
            data: 输入数据
            rules: 验证规则
            
        Returns:
            Dict[str, List[str]]: 错误信息
        """
        errors = {}
        
        for field, field_rules in rules.items():
            field_errors = []
            value = data.get(field)
            
            # 检查是否必填
            if field_rules.get("required", False) and (value is None or value == ""):
                field_errors.append("This field is required")
            
            # 验证类型
            field_type = field_rules.get("type")
            if field_type == "string":
                if not InputValidator.validate_string(
                    value,
                    field_rules.get("min_length", 1),
                    field_rules.get("max_length", 255),
                    field_rules.get("allow_empty", False)
                ):
                    field_errors.append(f"Invalid string format")
            elif field_type == "integer":
                if not InputValidator.validate_integer(
                    value,
                    field_rules.get("min_value"),
                    field_rules.get("max_value")
                ):
                    field_errors.append(f"Invalid integer format")
            elif field_type == "float":
                if not InputValidator.validate_float(
                    value,
                    field_rules.get("min_value"),
                    field_rules.get("max_value")
                ):
                    field_errors.append(f"Invalid float format")
            elif field_type == "email":
                if not InputValidator.validate_email(value):
                    field_errors.append(f"Invalid email format")
            elif field_type == "username":
                if not InputValidator.validate_username(value):
                    field_errors.append(f"Invalid username format")
            elif field_type == "password":
                if not InputValidator.validate_password(value):
                    field_errors.append(f"Invalid password format")
            elif field_type == "isbn":
                if not InputValidator.validate_isbn(value):
                    field_errors.append(f"Invalid ISBN format")
            elif field_type == "book_condition":
                if not InputValidator.validate_book_condition(value):
                    field_errors.append(f"Invalid book condition")
            
            if field_errors:
                errors[field] = field_errors
        
        return errors

# 验证规则
VALIDATION_RULES = {
    "user": {
        "username": {
            "type": "username",
            "required": True
        },
        "email": {
            "type": "email",
            "required": True
        },
        "password": {
            "type": "password",
            "required": True
        },
        "university": {
            "type": "string",
            "required": True,
            "max_length": 100
        },
        "major": {
            "type": "string",
            "required": True,
            "max_length": 100
        },
        "grade": {
            "type": "string",
            "required": True,
            "max_length": 20
        }
    },
    "book": {
        "title": {
            "type": "string",
            "required": True,
            "max_length": 200
        },
        "author": {
            "type": "string",
            "required": True,
            "max_length": 100
        },
        "isbn": {
            "type": "isbn",
            "required": True
        },
        "original_price": {
            "type": "float",
            "required": True,
            "min_value": 0.01
        },
        "condition": {
            "type": "book_condition",
            "required": True
        },
        "category": {
            "type": "string",
            "required": True,
            "max_length": 50
        },
        "description": {
            "type": "string",
            "required": True,
            "max_length": 1000
        },
        "university": {
            "type": "string",
            "required": True,
            "max_length": 100
        },
        "major": {
            "type": "string",
            "required": True,
            "max_length": 100
        },
        "grade": {
            "type": "string",
            "required": True,
            "max_length": 20
        }
    }
}