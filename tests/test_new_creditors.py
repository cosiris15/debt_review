"""
测试两个新债权人案例并与原方案对比

债权人2: 黛绰维纳（上海）设计有限公司 - 服务合同纠纷
债权人3: 广林欧卡罗（广西）家居有限公司 - 股东出资义务纠纷

原方案结果目录: /Users/chenchu/Desktop/第1批债权目标输出结果/
"""

import httpx
import asyncio
import json
from pathlib import Path
from datetime import datetime

LANGGRAPH_API = "http://127.0.0.1:2024"

# 材料路径
MATERIALS_DIR = Path("/Users/chenchu/Desktop/第1批债权申报材料")
TARGET_OUTPUT_DIR = Path("/Users/chenchu/Desktop/第1批债权目标输出结果")

# 测试结果保存路径
OUTPUT_DIR = Path("/Users/chenchu/Desktop/代码制作台/debt_review/tests/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def run_workflow_via_api(
    debtor_name: str,
    bankruptcy_date: str,
    creditors: list,
    interest_stop_date: str = None
):
    """通过 LangGraph API 运行工作流"""

    async with httpx.AsyncClient(timeout=600) as client:
        # 1. 创建 thread
        thread_resp = await client.post(
            f"{LANGGRAPH_API}/threads",
            headers={"Content-Type": "application/json"},
            json={}
        )
        if thread_resp.status_code != 200:
            print(f"创建 thread 失败: {thread_resp.status_code} - {thread_resp.text}")
            return None
        thread = thread_resp.json()
        thread_id = thread["thread_id"]
        print(f"Created thread: {thread_id}")

        # 2. 准备输入 (使用 InputState 格式)
        input_data = {
            "debtor_name": debtor_name,
            "bankruptcy_date": bankruptcy_date,
            "creditors": creditors,
        }
        if interest_stop_date:
            input_data["interest_stop_date"] = interest_stop_date

        # 3. 运行工作流
        print(f"\n开始执行工作流...")

        run_resp = await client.post(
            f"{LANGGRAPH_API}/threads/{thread_id}/runs",
            json={
                "assistant_id": "debt_reviewer",
                "input": input_data
            }
        )
        run = run_resp.json()
        run_id = run["run_id"]
        print(f"Run started: {run_id}")

        # 4. 轮询等待完成
        while True:
            status_resp = await client.get(
                f"{LANGGRAPH_API}/threads/{thread_id}/runs/{run_id}"
            )
            status = status_resp.json()
            run_status = status.get("status")

            if run_status == "success":
                print(f"\n工作流执行完成!")
                break
            elif run_status == "error":
                print(f"\n工作流执行失败: {status.get('error')}")
                break
            elif run_status in ("pending", "running"):
                print(f"  状态: {run_status}...")
                await asyncio.sleep(3)
            else:
                print(f"  未知状态: {run_status}")
                await asyncio.sleep(3)

        # 5. 获取最终状态
        state_resp = await client.get(
            f"{LANGGRAPH_API}/threads/{thread_id}/state"
        )
        final_state = state_resp.json()

        return final_state


async def test_daichuoweina():
    """测试黛绰维纳（上海）设计有限公司 - 服务合同纠纷"""
    print("\n" + "=" * 70)
    print("测试债权人2: 黛绰维纳（上海）设计有限公司")
    print("案件类型: 服务合同纠纷（无生效法律文书）")
    print("申报金额: 767,992.45元")
    print("=" * 70)

    result = await run_workflow_via_api(
        debtor_name="上海欧卡罗家居有限公司",
        bankruptcy_date="2024-02-26",
        interest_stop_date="2024-02-25",
        creditors=[{
            "creditor_name": "黛绰维纳（上海）设计有限公司",
            "materials_path": str(MATERIALS_DIR / "240319-欧卡罗-债权申报材料-黛绰维纳.md"),
        }]
    )

    if result:
        await save_and_compare_result(
            result,
            creditor_name="黛绰维纳（上海）设计有限公司",
            target_dir_name="002-黛绰维纳（上海）设计有限公司"
        )

    return result


async def test_guanglin_oukalo():
    """测试广林欧卡罗（广西）家居有限公司 - 股东出资义务纠纷"""
    print("\n" + "=" * 70)
    print("测试债权人3: 广林欧卡罗（广西）家居有限公司")
    print("案件类型: 股东出资义务求偿权（无生效法律文书）")
    print("申报金额: 39,200,000.00元")
    print("=" * 70)

    result = await run_workflow_via_api(
        debtor_name="上海欧卡罗家居有限公司",
        bankruptcy_date="2024-02-26",
        interest_stop_date="2024-02-25",
        creditors=[{
            "creditor_name": "广林欧卡罗（广西）家居有限公司",
            "materials_path": str(MATERIALS_DIR / "注资3920-广林欧卡罗.md"),
        }]
    )

    if result:
        await save_and_compare_result(
            result,
            creditor_name="广林欧卡罗（广西）家居有限公司",
            target_dir_name="003-广林欧卡罗（广西）家居有限公司"
        )

    return result


async def save_and_compare_result(result: dict, creditor_name: str, target_dir_name: str):
    """保存结果并与原方案对比"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_subdir = OUTPUT_DIR / creditor_name.replace("（", "(").replace("）", ")")
    output_subdir.mkdir(parents=True, exist_ok=True)

    # 提取工作流结果
    values = result.get("values", {})
    creditors = values.get("creditors", [])

    if not creditors:
        print(f"警告: 没有找到债权人结果")
        return

    cred = creditors[0]

    # 保存事实核查报告
    fact_check_report = cred.get("fact_check_report") or ""
    if fact_check_report:
        fact_check_path = output_subdir / f"事实核查报告_{timestamp}.md"
        fact_check_path.write_text(fact_check_report, encoding="utf-8")
        print(f"\n事实核查报告已保存: {fact_check_path}")
        print(f"  长度: {len(fact_check_report)} 字符")

    # 保存分析报告
    analysis_report = cred.get("analysis_report") or ""
    if analysis_report:
        analysis_path = output_subdir / f"分析报告_{timestamp}.md"
        analysis_path.write_text(analysis_report, encoding="utf-8")
        print(f"分析报告已保存: {analysis_path}")
        print(f"  长度: {len(analysis_report)} 字符")

    # 保存最终报告
    final_report = cred.get("final_report") or ""
    if final_report:
        final_path = output_subdir / f"最终报告_{timestamp}.md"
        final_path.write_text(final_report, encoding="utf-8")
        print(f"最终报告已保存: {final_path}")
        print(f"  长度: {len(final_report)} 字符")

    # 保存完整状态 (JSON)
    state_path = output_subdir / f"完整状态_{timestamp}.json"
    state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # 与原方案对比
    print(f"\n{'='*50}")
    print(f"与原方案对比分析")
    print(f"{'='*50}")

    target_dir = TARGET_OUTPUT_DIR / target_dir_name

    # 读取原方案最终报告
    original_final_report_path = target_dir / "最终报告"
    original_final_reports = list(original_final_report_path.glob("*.md")) if original_final_report_path.exists() else []

    if original_final_reports:
        original_report = original_final_reports[0].read_text(encoding="utf-8")
        print(f"\n原方案最终报告: {original_final_reports[0].name}")
        print(f"  长度: {len(original_report)} 字符")

        # 提取关键信息对比
        await compare_reports(final_report, original_report, creditor_name)
    else:
        print(f"警告: 未找到原方案最终报告")

    # 读取原方案分析报告
    original_analysis_path = target_dir / "工作底稿"
    original_analyses = list(original_analysis_path.glob("*分析报告*.md")) if original_analysis_path.exists() else []

    if original_analyses:
        original_analysis = original_analyses[0].read_text(encoding="utf-8")
        print(f"\n原方案分析报告: {original_analyses[0].name}")
        print(f"  长度: {len(original_analysis)} 字符")


async def compare_reports(new_report: str, original_report: str, creditor_name: str):
    """对比新旧报告的关键信息"""

    print(f"\n--- 关键指标对比 ---")

    # 提取确认金额
    import re

    def extract_amount(text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1) if match else "未找到"

    # 对于黛绰维纳
    if "黛绰维纳" in creditor_name:
        # 原方案结论: 暂缓确认
        print(f"\n原方案结论: 暂缓确认")
        print(f"  原因: 案件未经法院或仲裁机构裁决，关键证据缺失")

        # 检查新报告是否也得出相同结论
        if "暂缓确认" in new_report or "暂缓" in new_report:
            print(f"新方案结论: 暂缓确认 ✓")
        elif "确认" in new_report:
            # 尝试提取确认金额
            amount_match = re.search(r"确认.*?(\d[\d,]*\.?\d*).*?元", new_report)
            if amount_match:
                print(f"新方案结论: 确认 {amount_match.group(1)} 元")
            else:
                print(f"新方案结论: 需要人工检查")
        else:
            print(f"新方案结论: 需要人工检查")

        # 关键检查点
        check_items = [
            ("就无原则", "是否提及就无原则"),
            ("证据缺失", "是否识别证据缺失"),
            ("未经.*裁决", "是否识别无生效法律文书"),
            ("诉讼时效", "是否分析诉讼时效"),
        ]

        print(f"\n关键检查点:")
        for pattern, desc in check_items:
            new_has = "✓" if re.search(pattern, new_report) else "✗"
            orig_has = "✓" if re.search(pattern, original_report) else "✗"
            print(f"  {desc}: 新方案={new_has}, 原方案={orig_has}")

    # 对于广林欧卡罗
    elif "广林欧卡罗" in creditor_name:
        # 原方案结论: 确认 39,200,000.00 元
        print(f"\n原方案结论: 确认债权 39,200,000.00 元（普通债权）")

        # 检查新报告确认金额
        amount_match = re.search(r"确认.*?(\d[\d,]*\.?\d*).*?元", new_report)
        if amount_match:
            print(f"新方案结论: 确认 {amount_match.group(1)} 元")
        else:
            print(f"新方案结论: 需要人工检查")

        # 关键检查点
        check_items = [
            ("就无原则", "是否提及就无原则"),
            ("股东出资", "是否识别股东出资义务"),
            ("破产法.*三十五条", "是否引用破产法第35条"),
            ("诉讼时效", "是否分析诉讼时效"),
            ("普通债权", "是否正确确定债权性质"),
        ]

        print(f"\n关键检查点:")
        for pattern, desc in check_items:
            new_has = "✓" if re.search(pattern, new_report) else "✗"
            orig_has = "✓" if re.search(pattern, original_report) else "✗"
            print(f"  {desc}: 新方案={new_has}, 原方案={orig_has}")


async def main():
    """主函数"""

    # 检查 langgraph dev 是否运行
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{LANGGRAPH_API}/ok")
            if resp.status_code != 200:
                print("错误: langgraph dev 未运行")
                print("请先运行: langgraph dev")
                return
    except:
        print("错误: 无法连接到 langgraph dev")
        print("请先运行: langgraph dev")
        return

    print("LangGraph API 连接成功!")

    # 检查材料是否存在
    daichuoweina_path = MATERIALS_DIR / "240319-欧卡罗-债权申报材料-黛绰维纳.md"
    guanglin_path = MATERIALS_DIR / "注资3920-广林欧卡罗.md"

    if not daichuoweina_path.exists():
        print(f"错误: 黛绰维纳材料不存在: {daichuoweina_path}")
        return
    if not guanglin_path.exists():
        print(f"错误: 广林欧卡罗材料不存在: {guanglin_path}")
        return

    print("材料文件检查通过!")

    # 运行测试
    results = {}

    # 测试黛绰维纳
    print("\n" + "#" * 70)
    print("# 开始测试债权人2: 黛绰维纳")
    print("#" * 70)
    results["黛绰维纳"] = await test_daichuoweina()

    # 测试广林欧卡罗
    print("\n" + "#" * 70)
    print("# 开始测试债权人3: 广林欧卡罗")
    print("#" * 70)
    results["广林欧卡罗"] = await test_guanglin_oukalo()

    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    for name, result in results.items():
        if result:
            values = result.get("values", {})
            creditors = values.get("creditors", [])
            if creditors:
                cred = creditors[0]
                has_fact = bool(cred.get("fact_check_report"))
                has_analysis = bool(cred.get("analysis_report"))
                has_final = bool(cred.get("final_report"))
                print(f"\n{name}:")
                print(f"  事实核查报告: {'✓' if has_fact else '✗'}")
                print(f"  分析报告: {'✓' if has_analysis else '✗'}")
                print(f"  最终报告: {'✓' if has_final else '✗'}")
            else:
                print(f"\n{name}: 无债权人结果")
        else:
            print(f"\n{name}: 执行失败")


if __name__ == "__main__":
    asyncio.run(main())
