#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
环境初始化检查器 (Environment Initialization Checker)

这个脚本用于检查债权人的处理环境是否已正确初始化，
用于Agent或主控制者验证环境状态。
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

class EnvironmentChecker:
    """环境初始化检查器"""
    
    def __init__(self, project_root: str = "/root/debt_review_solution"):
        self.project_root = Path(project_root)
        self.output_root = self.project_root / "输出"
    
    def check_creditor_environment(self, batch_number: str, creditor_number: str,
                                 creditor_name: str) -> Dict:
        """检查特定债权人的环境状态
        
        Args:
            batch_number: 批次号
            creditor_number: 债权人编号
            creditor_name: 债权人名称
            
        Returns:
            Dict: 检查结果
        """
        base_path = self.output_root / f"第{batch_number}批债权" / f"{creditor_number}-{creditor_name}"
        
        result = {
            "creditor_info": {
                "batch_number": batch_number,
                "creditor_number": creditor_number,
                "creditor_name": creditor_name,
                "base_path": str(base_path)
            },
            "environment_status": {
                "base_directory_exists": False,
                "config_file_exists": False,
                "directories_complete": False,
                "ready_for_processing": False
            },
            "directory_status": {},
            "config_content": None,
            "missing_components": [],
            "recommendations": []
        }
        
        # 检查基础目录
        if base_path.exists() and base_path.is_dir():
            result["environment_status"]["base_directory_exists"] = True
        else:
            result["missing_components"].append("基础目录不存在")
        
        # 检查配置文件
        config_file = base_path / ".processing_config.json"
        if config_file.exists():
            result["environment_status"]["config_file_exists"] = True
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    result["config_content"] = json.load(f)
            except Exception as e:
                result["missing_components"].append(f"配置文件读取错误: {e}")
        else:
            result["missing_components"].append("配置文件不存在")
        
        # 检查子目录
        required_dirs = ["工作底稿", "最终报告", "计算文件"]
        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            result["directory_status"][dir_name] = exists
            if not exists:
                result["missing_components"].append(f"缺少目录: {dir_name}")
        
        # 计算整体状态
        dirs_complete = all(result["directory_status"].values())
        result["environment_status"]["directories_complete"] = dirs_complete
        
        result["environment_status"]["ready_for_processing"] = (
            result["environment_status"]["base_directory_exists"] and
            result["environment_status"]["config_file_exists"] and
            result["environment_status"]["directories_complete"]
        )
        
        # 生成建议
        if not result["environment_status"]["ready_for_processing"]:
            result["recommendations"].append(
                f"运行初始化命令: python 债权处理工作流控制器.py {batch_number} {creditor_number} {creditor_name}"
            )
        
        return result
    
    def print_check_result(self, result: Dict):
        """打印检查结果
        
        Args:
            result: 检查结果字典
        """
        info = result["creditor_info"]
        status = result["environment_status"]
        
        print(f"\n🔍 环境初始化检查结果")
        print(f"   债权人: {info['creditor_name']}")
        print(f"   批次: 第{info['batch_number']}批")
        print(f"   编号: {info['creditor_number']}")
        print(f"   路径: {info['base_path']}")
        
        print(f"\n📋 检查状态:")
        print(f"   基础目录: {'✅' if status['base_directory_exists'] else '❌'}")
        print(f"   配置文件: {'✅' if status['config_file_exists'] else '❌'}")
        print(f"   目录结构: {'✅' if status['directories_complete'] else '❌'}")
        
        # 详细目录状态
        if result["directory_status"]:
            print(f"   子目录详情:")
            for dir_name, exists in result["directory_status"].items():
                print(f"     {dir_name}: {'✅' if exists else '❌'}")
        
        # 整体状态
        if status["ready_for_processing"]:
            print(f"\n✅ 环境已就绪，可以开始债权处理")
        else:
            print(f"\n❌ 环境未就绪，需要初始化")
            
            if result["missing_components"]:
                print(f"\n🚨 缺失组件:")
                for component in result["missing_components"]:
                    print(f"   - {component}")
            
            if result["recommendations"]:
                print(f"\n💡 建议执行:")
                for rec in result["recommendations"]:
                    print(f"   {rec}")
    
    def auto_detect_creditor_from_path(self, check_path: str) -> Optional[Tuple[str, str, str]]:
        """从路径自动检测债权人信息
        
        Args:
            check_path: 要检查的路径
            
        Returns:
            Tuple[str, str, str]: (批次号, 债权人编号, 债权人名称) 或 None
        """
        path = Path(check_path)
        
        # 检查路径格式是否匹配: 输出/第X批债权/编号-名称
        if path.name.count('-') >= 1:
            # 从目录名解析
            dir_name = path.name
            parts = dir_name.split('-', 1)
            if len(parts) == 2:
                creditor_number = parts[0]
                creditor_name = parts[1]
                
                # 从父目录获取批次号
                parent = path.parent.name
                if parent.startswith('第') and parent.endswith('批债权'):
                    batch_number = parent.replace('第', '').replace('批债权', '')
                    return batch_number, creditor_number, creditor_name
        
        return None

def main():
    """主函数 - 命令行接口"""
    if len(sys.argv) == 2:
        # 单参数模式：自动从路径检测
        check_path = sys.argv[1]
        checker = EnvironmentChecker()
        
        creditor_info = checker.auto_detect_creditor_from_path(check_path)
        if creditor_info:
            batch_number, creditor_number, creditor_name = creditor_info
            result = checker.check_creditor_environment(batch_number, creditor_number, creditor_name)
            checker.print_check_result(result)
        else:
            print(f"❌ 无法从路径解析债权人信息: {check_path}")
            print("路径格式应为: 输出/第X批债权/编号-债权人名称")
            sys.exit(1)
            
    elif len(sys.argv) == 4:
        # 三参数模式：直接指定
        batch_number = sys.argv[1]
        creditor_number = sys.argv[2]
        creditor_name = sys.argv[3]
        
        checker = EnvironmentChecker()
        result = checker.check_creditor_environment(batch_number, creditor_number, creditor_name)
        checker.print_check_result(result)
        
        # 返回适当的退出码
        if result["environment_status"]["ready_for_processing"]:
            sys.exit(0)  # 成功
        else:
            sys.exit(1)  # 需要初始化
    
    else:
        print("用法:")
        print("  python 环境初始化检查器.py <批次号> <债权人编号> <债权人名称>")
        print("  python 环境初始化检查器.py <债权人目录路径>")
        print()
        print("示例:")
        print("  python 环境初始化检查器.py 1 115 慈溪市东航建筑起重机械安装队")
        print("  python 环境初始化检查器.py /root/debt_review_solution/输出/第1批债权/115-慈溪市东航建筑起重机械安装队")
        sys.exit(1)

if __name__ == "__main__":
    main()