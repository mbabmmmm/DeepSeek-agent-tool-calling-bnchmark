import sys
sys.path.insert(0, "E:/count/tau-bench-main")

print("=" * 50)
print("查看 tools 模块")
print("=" * 50)

# 查看 tools 模块
import tau_bench.envs.airline.tools as tools_module
print("tools 模块内容:")
for item in dir(tools_module):
    if not item.startswith("_"):
        print(f"  {item}")

print("\n" + "=" * 50)
print("查看 wiki 模块")
print("=" * 50)

# 查看 wiki 模块
import tau_bench.envs.airline.wiki as wiki_module
print("wiki 模块内容:")
for item in dir(wiki_module):
    if not item.startswith("_"):
        print(f"  {item}")