#!/usr/bin/env python3
"""
Test which Claude models are available in Vertex AI
"""
from anthropic import AnthropicVertex

# List of possible Claude model identifiers to test
possible_models = [
    # Sonnet 4.5
    "claude-sonnet-4-5@20250514",
    "claude-sonnet-4.5@20250514",
    "claude-4-5-sonnet@20250514",

    # Haiku 4.5
    "claude-haiku-4-5@20250514",
    "claude-4-5-haiku@20250514",

    # 3.5 Haiku
    "claude-3-5-haiku@20241022",
    "claude-3-5-haiku-20241022",

    # 3.5 Sonnet (older versions)
    "claude-3-5-sonnet@20241022",
    "claude-3-5-sonnet@20240620",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
]

project_id = "anetorg-sinaraya-kartik"
region = "us-east5"

print(f"Testing Claude models in project: {project_id}, region: {region}\n")

client = AnthropicVertex(region=region, project_id=project_id)

for model in possible_models:
    try:
        print(f"Testing {model}...", end=" ")
        message = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✓ WORKS! Response: {message.content[0].text[:50]}")
        break  # Found a working model, stop testing
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            print("✗ Not found")
        elif "403" in error_msg or "permission" in error_msg.lower():
            print("✗ Permission denied (might need to enable)")
        else:
            print(f"✗ Error: {error_msg[:100]}")

print("\nDone!")
