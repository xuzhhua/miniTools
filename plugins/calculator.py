"""
示例插件 - 计算器工具
"""
from backend.base_plugin import BasePlugin
from typing import Dict, Any, List
import math


class CalculatorPlugin(BasePlugin):
    """计算器工具插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "Calculator"
        self.version = "2.0.0"
        self.description = "提供基本数学计算和科学计算功能"
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """定义插件参数"""
        return [
            {
                "name": "a",
                "type": "float",
                "required": True,
                "description": "第一个数字"
            },
            {
                "name": "b",
                "type": "float",
                "required": False,
                "description": "第二个数字（某些操作不需要）"
            },
            {
                "name": "operation",
                "type": "string",
                "required": True,
                "description": "操作类型: add(加), sub(减), mul(乘), div(除), pow(幂), sqrt(平方根), square(平方), sin(正弦), cos(余弦), tan(正切), log(对数), ln(自然对数), abs(绝对值), factorial(阶乘)"
            }
        ]
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行计算"""
        if params is None:
            params = {}
        
        try:
            a = float(params.get("a", 0))
            b_param = params.get("b")
            b = float(b_param) if b_param is not None else None
            operation = params.get("operation", "").lower()
            
            # 基本运算
            if operation == "add":
                if b is None:
                    return self._error("加法需要两个数字")
                result = a + b
                expression = f"{a} + {b} = {result}"
                
            elif operation == "sub":
                if b is None:
                    return self._error("减法需要两个数字")
                result = a - b
                expression = f"{a} - {b} = {result}"
                
            elif operation == "mul":
                if b is None:
                    return self._error("乘法需要两个数字")
                result = a * b
                expression = f"{a} × {b} = {result}"
                
            elif operation == "div":
                if b is None:
                    return self._error("除法需要两个数字")
                if b == 0:
                    return self._error("除数不能为0")
                result = a / b
                expression = f"{a} ÷ {b} = {result}"
            
            # 科学运算 - 需要两个数
            elif operation == "pow":
                if b is None:
                    return self._error("幂运算需要两个数字")
                result = math.pow(a, b)
                expression = f"{a}^{b} = {result}"
            
            # 科学运算 - 单个数
            elif operation == "sqrt":
                if a < 0:
                    return self._error("不能对负数开平方根")
                result = math.sqrt(a)
                expression = f"√{a} = {result}"
                
            elif operation == "square":
                result = a * a
                expression = f"{a}² = {result}"
                
            elif operation == "sin":
                result = math.sin(math.radians(a))
                expression = f"sin({a}°) = {result}"
                
            elif operation == "cos":
                result = math.cos(math.radians(a))
                expression = f"cos({a}°) = {result}"
                
            elif operation == "tan":
                result = math.tan(math.radians(a))
                expression = f"tan({a}°) = {result}"
                
            elif operation == "log":
                if a <= 0:
                    return self._error("对数的真数必须大于0")
                result = math.log10(a)
                expression = f"log({a}) = {result}"
                
            elif operation == "ln":
                if a <= 0:
                    return self._error("自然对数的真数必须大于0")
                result = math.log(a)
                expression = f"ln({a}) = {result}"
                
            elif operation == "abs":
                result = abs(a)
                expression = f"|{a}| = {result}"
                
            elif operation == "factorial":
                if a < 0 or a != int(a):
                    return self._error("阶乘只能计算非负整数")
                result = math.factorial(int(a))
                expression = f"{int(a)}! = {result}"
            
            else:
                return self._error(f"不支持的操作: {operation}")
            
            return {
                "success": True,
                "data": {
                    "result": result,
                    "expression": expression
                },
                "message": "计算成功"
            }
            
        except ValueError as e:
            return self._error(f"参数格式错误: {str(e)}")
        except Exception as e:
            return self._error(f"计算失败: {str(e)}")
    
    def _error(self, message: str) -> Dict[str, Any]:
        """返回错误信息"""
        return {
            "success": False,
            "data": None,
            "message": message
        }
