默认调度策略已被修改为sjf策略，如果需要使用主动的priority策略，请在运行时指定--scheduling-policy priority；

如果需要使用我们的策略，请将目录下scheduler.py复制到your_envs/vllm/lib/python3.10/site-packages/vllm/core/scheduler.py下；

如果需要使用我们的测试，请在目录下运行python main.py。