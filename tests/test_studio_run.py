"""
通过 LangGraph API 运行测试 - 可在 LangStudio 中实时查看

使用方法:
1. 确保 langgraph dev 正在运行
2. 运行: python tests/test_studio_run.py
3. 打开 LangStudio 查看执行过程: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
"""

import httpx
import asyncio
import json
from pathlib import Path

LANGGRAPH_API = "http://127.0.0.1:2024"


async def run_workflow_via_api(
    debtor_name: str,
    bankruptcy_date: str,
    creditors: list,
    interest_stop_date: str = None
):
    """通过 LangGraph API 运行工作流"""

    async with httpx.AsyncClient(timeout=300) as client:
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
        print(f"在 LangStudio 中查看: {LANGGRAPH_API.replace('http://127.0.0.1:2024', 'https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024')}")
        print()

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
                await asyncio.sleep(2)
            else:
                print(f"  未知状态: {run_status}")
                await asyncio.sleep(2)

        # 5. 获取最终状态
        state_resp = await client.get(
            f"{LANGGRAPH_API}/threads/{thread_id}/state"
        )
        final_state = state_resp.json()

        return final_state


async def test_muchen():
    """测试上海牧诚贸易有限公司"""
    print("=" * 60)
    print("测试债权人: 上海牧诚贸易有限公司")
    print("=" * 60)

    result = await run_workflow_via_api(
        debtor_name="上海欧卡罗家居有限公司",
        bankruptcy_date="2024-02-26",
        interest_stop_date="2024-02-25",
        creditors=[{
            "creditor_name": "上海牧诚贸易有限公司",
            "materials_path": "/Users/chenchu/Desktop/第1批债权/债权申报书-上海牧诚贸易有限公司.md",
        }]
    )

    # 打印结果摘要
    values = result.get("values", {})
    creditors = values.get("creditors", [])

    if creditors:
        cred = creditors[0]
        print(f"\n=== 结果摘要 ===")
        print(f"事实核查报告: {len(cred.get('fact_check_report') or '')} 字符")
        print(f"分析报告: {len(cred.get('analysis_report') or '')} 字符")
        print(f"最终报告: {len(cred.get('final_report') or '')} 字符")

        if cred.get("confirmed_total"):
            print(f"确认金额: {cred.get('confirmed_total'):,.2f} 元")


async def main():
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
    print()

    await test_muchen()


if __name__ == "__main__":
    asyncio.run(main())
