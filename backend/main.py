"""
流式对话演示 - Client SDK 版（手动管理上下文）

功能：
- 从控制台读取用户输入
- 使用 AsyncAnthropic 流式输出响应
- 手动拼接和管理对话历史
- 支持火山方舟等自定义 API 端点

安装依赖：
    pip install -r requirements.txt

运行：
    python main.py --api-key <YOUR_API_KEY>
    ark-f8a5b24d-176d-43e1-85a7-37938ad3b8c9-d148f

说明：
    Client SDK 的 messages.stream() 支持 token 级流式输出，
    但需要手动管理上下文（拼接 history）。
"""
import argparse
import asyncio

from anthropic import AsyncAnthropic


def parse_args():
    parser = argparse.ArgumentParser(description="流式对话演示（Client SDK - 手动上下文）")
    parser.add_argument("--api-key", required=True, help="API 密钥")
    parser.add_argument(
        "--base-url",
        default="https://ark.cn-beijing.volces.com/api/coding",
        help="API 端点",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-20250514",
        help="模型名称",
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    client = AsyncAnthropic(
        api_key=args.api_key,
        base_url=args.base_url,
    )

    print("=" * 50)
    print("Client SDK 流式对话（手动管理上下文）")
    print("输入消息后按回车发送，输入 'quit' 退出")
    print("=" * 50)
    print()

    # 手动管理历史
    history = []

    while True:
        user_input = input("你: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n再见！")
            break

        # 追加用户消息到历史
        history.append({"role": "user", "content": user_input})

        print("\nClaude: ", end="", flush=True)

        try:
            async with client.messages.stream(
                    model=args.model,
                    max_tokens=4096,
                    messages=history,
            ) as stream:
                async for text in stream.text_stream:
                    print(text, end="", flush=True)
                message = await stream.get_final_message()

            # 追加助手消息到历史
            assistant_text = "".join(
                block.text for block in message.content if hasattr(block, "text")
            )
            history.append({"role": "assistant", "content": assistant_text})

            print()
            print()

        except Exception as e:
            print(f"\n错误: {e}")
            # 移除失败的用户消息
            history.pop()
            print()


if __name__ == "__main__":
    asyncio.run(main())